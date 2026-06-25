import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página do Streamlit
st.set_page_config(page_title="Dashboard Diagnóstico - SENAI", layout="wide")

# 1. CARGA E ESTRUTURAÇÃO DOS DADOS DO SIMULADO
@st.cache_data
def carregar_dados_questoes():
    # Mapeamento real das questões enviadas no documento
    questoes = {
        'ID_Questao': [
            'SAEP_49729', 'SAEP_49909', 'SAEP_49912', 'SAEP_49941', 'SAEP_50837',
            'SAEP_52999', 'SAEP_53012', 'SAEP_60070', 'SAEP_66110', 'SAEP_69214',
            'SAEP_69259', 'SAEP_69350', 'SAEP_69354', 'SAEP_COZINHA'
        ],
        'Assunto': [
            'Algoritmos (Consumo)', 'Excel (Divisão)', 'Lógica (Condicional)', 'Lógica (Porcentagem)', 'IoT (Arduino/LED)',
            'Excel (Soma)', 'Git (Controle Versão)', 'IoT (Lei de Ohm)', 'Estrutura de Dados (Hash)', 'Estrutura de Dados (Árvore)',
            'Lógica (Tipos Primitivos)', 'Documentação (Análise)', 'Linguagem C (Loops)', 'Lógica (Expressões)'
        ],
        'Dificuldade': [
            'Muito Fácil', 'Fácil', 'Médio', 'Médio', 'Fácil',
            'Difícil', 'Médio', 'Muito Difícil', 'Médio', 'Médio',
            'Fácil', 'Difícil', 'Médio', 'Médio'
        ],
        'Competencia': ['C3', 'C1', 'C3', 'C2', 'C1', 'C1', 'C2', 'C3', 'C3', 'C3', 'C1', 'C3', 'C3', 'C3']
    }
    return pd.DataFrame(questoes)

@st.cache_data
def gerar_dados_alunos(df_questoes, qtd_alunos=30):
    # Simulação de uma turma de 30 alunos resolvendo a prova
    np.random.seed(42)
    alunos_nomes = [f"Aluno {i}" for i in range(1, qtd_alunos + 1)]
    
    linhas = []
    # Definindo pesos de acerto baseados na dificuldade real dos itens
    pesos = {'Muito Fácil': 0.90, 'Fácil': 0.80, 'Médio': 0.65, 'Difícil': 0.40, 'Muito Difícil': 0.20}
    
    for aluno in alunos_nomes:
        for idx, row in df_questoes.iterrows():
            # Gera 1 (acertou) ou 0 (errou) baseado na dificuldade do item
            acertou = np.random.choice([1, 0], p=[pesos[row['Dificuldade']], 1 - pesos[row['Dificuldade']]])
            linhas.append({
                'Aluno': aluno,
                'ID_Questao': row['ID_Questao'],
                'Nota': acertou
            })
    return pd.DataFrame(linhas)

# Inicializando os dados
df_q = carregar_dados_questoes()
df_f = gerar_dados_alunos(df_q)

# Cruzando as tabelas (Equivalente ao relacionamento no Power BI)
df_completo = pd.merge(df_f, df_q, on='ID_Questao')

# --- INTERFACE DO DASHBOARD ---
st.title("📊 Dashboard de Diagnóstico de Turma")
st.subheader("Curso: Técnico Em Desenvolvimento De Sistemas | Matriz 2021")
st.markdown("---")

# Filtro Lateral
competencia_selecionada = st.sidebar.multiselect(
    "Filtrar por Competência Macro:",
    options=df_completo['Competencia'].unique(),
    default=df_completo['Competencia'].unique()
)
df_filtrado = df_completo[df_completo['Competencia'].isin(competencia_selecionada)]

# MÈTRICAS GERAIS (Cards do Topo)
total_alunos = df_filtrado['Aluno'].nunique()
taxa_acerto_geral = df_filtrado['Nota'].mean() * 100
questoes_criticas = df_filtrado.groupby('Assunto')['Nota'].mean().loc[lambda x: x < 0.5].count()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Alunos Avaliados", f"{total_alunos}")
with col2:
    st.metric("Média Geral de Acertos", f"{taxa_acerto_geral:.1f}%")
with col3:
    st.metric("Tópicos Críticos (<50% acerto)", f"{questoes_criticas}")

st.markdown("---")

# SEÇÃO DE ANÁLISE VISUAL
col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("🎯 Taxa de Acerto por Tópico / Questão")
    df_topicos = df_filtrado.groupby('Assunto')['Nota'].mean().reset_index()
    df_topicos['Nota'] = df_topicos['Nota'] * 100
    df_topicos = df_topicos.sort_values(by='Nota', ascending=True)
    
    fig_barra = px.bar(
        df_topicos, x='Nota', y='Assunto', orientation='h',
        labels={'Nota': '% de Acerto', 'Assunto': 'Conteúdo Avaliado'},
        color='Nota', color_continuous_scale='RdYlGn', range_color=[20, 90]
    )
    st.plotly_chart(fig_barra, use_container_width=True)

with col_dir:
    st.subheader("⚖️ Desempenho por Nível de Dificuldade")
    df_dif = df_filtrado.groupby('Dificuldade')['Nota'].mean().reset_index()
    df_dif['Nota'] = df_dif['Nota'] * 100
    # Ordenação lógica de dificuldade
    df_dif['Dificuldade'] = pd.Categorical(df_dif['Dificuldade'], categories=['Muito Fácil', 'Fácil', 'Médio', 'Difícil', 'Muito Difícil'], ordered=True)
    df_dif = df_dif.sort_values('Dificuldade')
    
    fig_linha = px.line(
        df_dif, x='Dificuldade', y='Nota', markers=True,
        labels={'Nota': '% Médio de Acerto'}, text=df_dif['Nota'].map('{:.1f}%'.format)
    )
    fig_linha.update_traces(textposition="top center")
    st.plotly_chart(fig_linha, use_container_width=True)

st.markdown("---")

# VISÃO MATRIZ (CONSELHO DE CLASSE)
st.subheader("👁️ Visão Individual de Alunos vs Questões (Matriz de Calor)")
st.write("Verde indica acerto (1) e Vermelho indica erro (0). Ideal para identificar alunos que precisam de recuperação.")

df_pivot = df_filtrado.pivot_table(index='Aluno', columns='Assunto', values='Nota', aggfunc='mean')

# Plotando Mapa de Calor utilizando Plotly Graph Objects
fig_heatmap = go.Figure(data=go.Heatmap(
    z=df_pivot.values,
    x=df_pivot.columns,
    y=df_pivot.index,
    colorscale=[[0, '#e74c3c'], [1, '#2ecc71']],
    showscale=False
))
fig_heatmap.update_layout(xaxis_tickangle=-45, height=500)
st.plotly_chart(fig_heatmap, use_container_width=True)