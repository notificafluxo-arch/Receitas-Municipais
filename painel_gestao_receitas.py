# painel_gestao_receitas_searchable.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Painel de Gestão de Receitas", layout="wide")
st.title("🏛️ Painel de Gestão de Receitas por Instituição")

# Upload do arquivo
uploaded_file = st.file_uploader("📁 Escolha seu arquivo CSV ou Excel", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df.columns = [c.strip().upper() for c in df.columns]

    # Filtros na barra lateral (buscáveis)
    st.sidebar.header("Filtros do Painel")
    
    exercicios = sorted(df['EXERCICIO'].unique())
    competencias = df['COMPETENCIA'].unique()
    instituicoes = df['INSTITUIÇÃO'].unique()
    receitas = df['RECEITA'].unique()

    filtro_exercicio = st.sidebar.selectbox("Ano (Exercício)", exercicios)
    filtro_competencia = st.sidebar.multiselect("Competência", competencias, default=competencias)
    filtro_instituicao = st.sidebar.multiselect("Instituição (até 4)", instituicoes, default=instituicoes[:4])
    filtro_receita = st.sidebar.multiselect("Receita específica", receitas, default=receitas)

    # Aplicando filtros
    df_filtrado = df[
        (df['EXERCICIO'] == filtro_exercicio) &
        (df['COMPETENCIA'].isin(filtro_competencia)) &
        (df['INSTITUIÇÃO'].isin(filtro_instituicao)) &
        (df['RECEITA'].isin(filtro_receita))
    ]

    if df_filtrado.empty:
        st.warning("⚠ Nenhum dado encontrado para os filtros selecionados.")
    else:
        instituicao_principal = filtro_instituicao[0]

        # Cards de resumo
        total_principal = df_filtrado[df_filtrado['INSTITUIÇÃO']==instituicao_principal]['VALOR'].sum()
        media_comparadas = df_filtrado[df_filtrado['INSTITUIÇÃO']!=instituicao_principal]['VALOR'].mean()
        percentual_participacao = total_principal / df_filtrado['VALOR'].sum() * 100

        col1, col2, col3 = st.columns(3)
        col1.metric(f"💰 Total {instituicao_principal}", f"R${total_principal:,.2f}")
        col2.metric(f"📊 Média das demais instituições", f"R${media_comparadas:,.2f}")
        col3.metric(f"📌 Participação (%)", f"{percentual_participacao:.2f}%")

        st.markdown("---")

        # Gráfico 1: Ranking geral
        st.subheader("🏆 Ranking de Receitas por Instituição")
        df_rank = df_filtrado.groupby('INSTITUIÇÃO')['VALOR'].sum().reset_index().sort_values(by='VALOR', ascending=False)
        fig_rank = px.bar(df_rank, x='INSTITUIÇÃO', y='VALOR', text='VALOR',
                          color='INSTITUIÇÃO', color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_rank, use_container_width=True)

        # Gráfico 2: Evolução por competência
        st.subheader("📈 Evolução da Receita por Competência")
        df_trend = df_filtrado.groupby(['COMPETENCIA', 'INSTITUIÇÃO'])['VALOR'].sum().reset_index()
        fig_trend = px.line(df_trend, x='COMPETENCIA', y='VALOR', color='INSTITUIÇÃO', markers=True,
                            labels={'VALOR':'Valor', 'COMPETENCIA':'Competência'},
                            color_discrete_sequence=px.colors.qualitative.Set1)
        st.plotly_chart(fig_trend, use_container_width=True)

        # Gráfico 3: Percentual de participação (Donut)
        st.subheader("🥧 Percentual de Participação por Instituição")
        df_pct = df_filtrado.groupby('INSTITUIÇÃO')['VALOR'].sum().reset_index()
        fig_pie = px.pie(df_pct, names='INSTITUIÇÃO', values='VALOR', color='INSTITUIÇÃO',
                         color_discrete_sequence=px.colors.qualitative.Pastel, hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

        # Gráfico 4: Comparativo individual de receitas
        st.subheader("🔹 Comparativo de Receitas Entre Municípios")
        df_ind = df_filtrado.groupby(['RECEITA', 'INSTITUIÇÃO'])['VALOR'].sum().reset_index()
        fig_ind = px.bar(df_ind, x='RECEITA', y='VALOR', color='INSTITUIÇÃO', barmode='group',
                         text='VALOR', color_discrete_sequence=px.colors.qualitative.Vivid)
        st.plotly_chart(fig_ind, use_container_width=True)
