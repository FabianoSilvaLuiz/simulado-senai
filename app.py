import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página do Streamlit
st.set_page_config(page_title="Dashboard Diagnóstico - SENAI", layout="wide")

# 1. CARGA REAL DOS DADOS DA PROVA (Baseado no PDF)
@st.cache_data
def carregar_dados_questoes():
    questoes = {
        'ID_Questao': [
            'SAEP_49729', 'SAEP_49909', 'SAEP_49912', 'SAEP_49941', 'SAEP_50048',
            'SAEP_50837', 'SAEP_52999', 'SAEP_53012', 'SAEP_60070', 'SAEP_66110',
            'SAEP_69214', 'SAEP_69259', 'SAEP_69350', 'SAEP_69354'
        ],
        'Assunto': [
            'Algoritmos (Consumo)', 'Excel (Horário de Pico)', 'Lógica (Maioridade)', 'Vendas (Descontos)', 'IoT (Circuito Semáforo)',
            'Excel (Horas Técnicos)', 'Git (Controle Versão)', 'IoT (Lei de Ohm)', 'Estrutura Dados (Grandes Volumes)', 'Estrutura Dados (Biblioteca)',
            'Lógica (Tipos Primitivos)', 'Documentação (Etapas Web)', 'Linguagem C (Loops Pares)', 'Lógica (Expressões Cozinha)'
        ],
        'Dificuldade': [
            'Muito Fácil', 'Fácil', 'Médio', 'Médio', 'Médio',
            'Fácil', 'Difícil', 'Médio', 'Muito Difícil', 'Médio',
            'Médio', 'Fácil', 'Difícil', 'Médio'
        ],
        'Competencia': ['C3', 'C1', 'C3', 'C3', 'C2', 'C1', 'C1', 'C2', 'C3', 'C3', 'C3', 'C1', 'C3', 'C3']
    }
    return pd.DataFrame(questoes)

@st.cache_data
def gerar_dados_alunos_reais(df_questoes):
    # Simulação de pauta com alunos do ambiente técnico do SENAI
    np.random.seed(10)
    nomes_alunos = [
        "Alexandre Silva", "Beatriz Santos", "Carlos Eduardo", "Daniela Costa", "Gabriel Almeida",
        "Guilherme Rocha", "Gustavo Lima", "Julia Fernandes", "Lucas Oliveira", "Mariana Ribeiro",
        "Mateus Carvalho", "Pedro Henrique", "Rafael Souza", "Rodrigo Martins", "Vinícius Gomes"
    ]
    
    linhas = []
    pesos = {'Muito Fácil': 0.90, 'Fácil': 0.80, 'Médio': 0.65, 'Difícil': 0.45, 'Muito Difícil': 0.25}
    
    for aluno in nomes_alunos:
        for idx, row in df_questoes.iterrows():
            acertou = np.random.choice([1, 0], p=[pesos[row['Dificuldade']], 1 - pesos[row['Dificuldade']]])
            linhas.append({'Aluno': aluno, 'ID_Questao': row['ID_Questao'], 'Nota': acertou})
    return pd.DataFrame(linhas)

df_q = carregar_dados_questoes()
df_f = gerar_dados_alunos_reais(df_q)
df_completo = pd.merge(df_f, df_q, on='ID_Questao')

# --- INTERFACE VISUAL ---
st.title("📊 Dashboard de Diagnóstico de Turma Completo")
st.subheader("Curso: Técnico Em Desenvolvimento De Sistemas | SENAI")
st.markdown("---")

# --- BARRA LATERAL DE FILTROS ---
st.sidebar.header("🔍 Painel de Controle")
visao = st.sidebar.radio("Selecione o Nível de Análise:", ["Visão Geral da Turma", "Visão por Aluno Individual"])

competencia_selecionada = st.sidebar.multiselect(
    "Filtrar por Competência Macro:",
    options=df_completo['Competencia'].unique(),
    default=df_completo['Competencia'].unique()
)
df_filtrado = df_completo[df_completo['Competencia'].isin(competencia_selecionada)]

# --- MODO 1: VISÃO GERAL DA TURMA ---
if visao == "Visão Geral da Turma":
    total_alunos = df_filtrado['Aluno'].nunique()
    taxa_acerto_geral = df_filtrado['Nota'].mean() * 100
    questoes_criticas = df_filtrado.groupby('Assunto')['Nota'].mean().loc[lambda x: x < 0.5].count()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Alunos Avaliados", f"{total_alunos}")
    with col2:
        st.metric("Média Geral da Turma", f"{taxa_acerto_geral:.1f}%")
    with col3:
        st.metric("Tópicos Críticos (<50% acertos)", f"{questoes_criticas}")

    st.markdown("---")
    
    # --- NOVA SEÇÃO: RANKING DE DESEMPENHO (MELHORES E PIORES) ---
    st.subheader("🏆 Ranking de Rendimento Escolar")
    
    # Calcular a nota final de cada aluno (porcentagem de acertos)
    df_ranking = df_filtrado.groupby('Aluno')['Nota'].mean().reset_index()
    df_ranking['Aproveitamento'] = df_ranking['Nota'] * 100
    df_ranking = df_ranking.sort_values(by='Aproveitamento', ascending=False).reset_index(drop=True)
    
    col_melhores, col_piores = st.columns(2)
    
    with col_melhores:
        st.write("⭐ **Alunos Destaques (Maiores Notas)**")
        df_top = df_ranking.head(3)[['Aluno', 'Aproveitamento']].copy()
        df_top['Aproveitamento'] = df_top['Aproveitamento'].map('{:.1f}%'.format)
        st.dataframe(df_top, use_container_width=True, hide_index=True)
        
    with col_piores:
        st.write("⚠️ **Alunos com Baixo Rendimento (Atenção/Recuperação)**")
        df_Low = df_ranking.tail(3)[['Aluno', 'Aproveitamento']].copy()
        df_Low['Aproveitamento'] = df_Low['Aproveitamento'].map('{:.1f}%'.format)
        # Inverter para mostrar o menor na primeira linha da tabela de atenção
        df_Low = df_Low.sort_values(by='Aproveitamento', ascending=True)
        st.dataframe(df_Low, use_container_width=True, hide_index=True)

    st.markdown("---")
    col_esq, col_dir = st.columns(2)

    with col_esq:
        st.subheader("🎯 Desempenho por Conteúdo da Matriz")
        df_topicos = df_filtrado.groupby('Assunto')['Nota'].mean().reset_index()
        df_topicos['Nota'] = df_topicos['Nota'] * 100
        df_topicos = df_topicos.sort_values(by='Nota', ascending=True)
        fig_barra = px.bar(df_topicos, x='Nota', y='Assunto', orientation='h', color='Nota', color_continuous_scale='RdYlGn', range_color=[30, 85])
        st.plotly_chart(fig_barra, use_container_width=True)

    with col_dir:
        st.subheader("⚖️ Distribuição por Nível de Dificuldade")
        df_dif = df_filtrado.groupby('Dificuldade')['Nota'].mean().reset_index()
        df_dif['Nota'] = df_dif['Nota'] * 100
        df_dif['Dificuldade'] = pd.Categorical(df_dif['Dificuldade'], categories=['Muito Fácil', 'Fácil', 'Médio', 'Difícil', 'Muito Difícil'], ordered=True)
        fig_linha = px.line(df_dif.sort_values('Dificuldade'), x='Dificuldade', y='Nota', markers=True, text=df_dif['Nota'].map('{:.1f}%'.format))
        st.plotly_chart(fig_linha, use_container_width=True)

    st.markdown("---")
    st.subheader("👁️ Mapa de Calor Completo (Acertos Gerais)")
    df_pivot = df_filtrado.pivot_table(index='Aluno', columns='Assunto', values='Nota', aggfunc='mean')
    fig_heatmap = go.Figure(data=go.Heatmap(z=df_pivot.values, x=df_pivot.columns, y=df_pivot.index, colorscale=[[0, '#e74c3c'], [1, '#2ecc71']], showscale=False))
    fig_heatmap.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig_heatmap, use_container_width=True)

# --- MODO 2: VISÃO POR ALUNO INDIVIDUAL ---
else:
    lista_alunos = sorted(df_filtrado['Aluno'].unique())
    aluno_selecionado = st.sidebar.selectbox("Escolha o Aluno para analisar:", lista_alunos)
    
    df_aluno = df_filtrado[df_filtrado['Aluno'] == aluno_selecionado]
    
    total_questoes = len(df_aluno)
    total_acertos = int(df_aluno['Nota'].sum())
    total_erros = int(total_questoes - total_acertos)
    taxa_individual = (total_acertos / total_questoes) * 100

    st.subheader(f"👤 Relatório de Diagnóstico Focado: {aluno_selecionado}")
    
    card1, card2, card3, card4 = st.columns(4)
    with card1:
        st.metric("Aproveitamento do Aluno", f"{taxa_individual:.1f}%")
    with card2:
        st.metric("Total de Acertos", f"✅ {total_acertos}")
    with card3:
        st.metric("Total de Erros", f"❌ {total_erros}")
    with card4:
        media_sala = df_filtrado['Nota'].mean() * 100
        diferenca = taxa_individual - media_sala
        st.metric("Vs Média Geral", f"{diferenca:+.1f}%", delta=f"{diferenca:.1f}%")

    st.markdown("---")
    col_grafico, col_tabela = st.columns([1, 2])
    
    with col_grafico:
        st.write("📊 **Proporção de Acertos/Erros**")
        fig_pizza = px.pie(
            names=['Acertos', 'Erros'], 
            values=[total_acertos, total_erros],
            color=['Acertos', 'Erros'],
            color_discrete_map={'Acertos': '#2ecc71', 'Erros': '#e74c3c'},
            hole=0.4
        )
        st.plotly_chart(fig_pizza, use_container_width=True)

    with col_tabela:
        st.write("📋 **Desempenho Individual por Item Evaluado**")
        
        df_tabela_aluno = df_aluno[['ID_Questao', 'Assunto', 'Dificuldade', 'Competencia', 'Nota']].copy()
        df_tabela_aluno['Resultado'] = df_tabela_aluno['Nota'].apply(lambda x: "✅ Acertou" if x == 1 else "❌ Errou")
        
        def aplicar_cor(val):
            color = '#d4edda' if "Acertou" in val else '#f8d7da'
            text_color = '#155724' if "Acertou" in val else '#721c24'
            return f'background-color: {color}; color: {text_color}; font-weight: bold;'
        
        df_exibir = df_tabela_aluno[['ID_Questao', 'Assunto', 'Dificuldade', 'Competencia', 'Resultado']].reset_index(drop=True)
        
        st.dataframe(df_exibir.style.map(aplicar_cor, subset=['Resultado']), use_container_width=True, height=450)