import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
# --- Define o título da página, o ícone e o layout para ocupar a largura inteira ---
st.set_page_config(
    page_title="DashBoard de Salário na Área de Dados",
    page_icon="🎲",
    layout="wide"
)

# --- Carregamento de Dados ---
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")
# Exibe os nomes das colunas para debug
#st.write(df.columns)

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔎Filtros") 

# --- Filtro de Ano ---

anos_disponiveis = sorted(df['ano'].unique())
ano_selecionado = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

#--- Filtro de Senioridade ---
senioridade_disponivel = sorted(df['senioridade'].unique())
senioridade_selecionadas = st.sidebar.multiselect("senioridade", senioridade_disponivel, default=senioridade_disponivel)

#--- Filtro por tipo de contrato ---
contrato_disponivel = sorted(df['contrato'].unique())
contrato_selecionados = st.sidebar.multiselect("Tipo de Contrato", contrato_disponivel, default=contrato_disponivel)

#--- Filtro por tamanho da empresa ---
tamanhos_disponivel = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponivel, default=tamanhos_disponivel)

#--- Filtragem do DataFrame ---
#--- O dataframe principal é filtrado com base nas seleções feitas na barra lateral ---
df_filtrado = df[
    (df['ano'].isin(ano_selecionado)) &
    (df['senioridade'].isin(senioridade_selecionadas)) &
    (df['contrato'].isin(contrato_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

#--- Conteúdo Principal ---
st.title ("🎲DashBoard de Análise de Salários na área de Dados")
st.markdown("Explore os dados salariais na área de Dados nos últimos anos. Utilize os filtros na barra lateral para refinar sua análise.")

#--- Métricas Principais (KPIs) ---
st.subheader("Metricas Gerais (Salário Anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    salario_minimo = df_filtrado['usd'].min()
    total_registro = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado['cargo'].mode()[0]
else:
    salario_medio, salario_maximo, salario_minimo, total_registro, cargo_mais_frequente = 0, 0, 0, 0, ""

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Salario Medio", f"${salario_medio:,.0f}")
col2.metric("Salario Maximo", f"${salario_maximo:,.0f}")
col3.metric("Salario Minimo", f"${salario_minimo:,.0f}")
col4.metric("Total de Registros", f"{total_registro:,}")
col5.metric("Cargo Mais Frequente", cargo_mais_frequente)


st.markdown("---")

#--- Definição das colunas para os gráficos ---
col_graf1, col_graf2 = st.columns(2)

#--- Analises Visuais com Plotly ---


with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 Cargos por Salário Médio",
            labels={'usd': "Media Salarial Anual (USD)", 'cargo': ""},
            color_discrete_sequence=['#d62728']  # vermelho
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.write("Nenhum dado disponível para exibir o gráfico de cargos.")

    with col_graf2:
        if not df_filtrado.empty:
            grafico_hist = px.histogram(
                df_filtrado,
                x='usd',
                nbins=30,
                title="Distribuição Salarial",
                labels={'usd': "Faixa Salarial (USD)", 'count': ""},
                color_discrete_sequence=['#d62728']  # vermelho
            )
            grafico_hist.update_layout(title_x=0.1)
            st.plotly_chart(grafico_hist, use_container_width=True)
        else:
            st.write("Nenhum dado disponível para exibir o gráfico de distribuição.")

    col_graf3, col_graf4 = st.columns(2)

    with col_graf3:
        if not df_filtrado.empty:
            remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
            remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
            grafico_remoto = px.pie(
                remoto_contagem,
                names='tipo_trabalho',
                values='quantidade',
                title='Proporção dos Tipos de Trabalho Remoto',
                hole=0.5,
                color_discrete_sequence=['#d62728', '#ff9896', '#c9302c', '#ff6666']  # tons de vermelho
            )
            grafico_remoto.update_traces(textinfo='percent+label')
            grafico_remoto.update_layout(title_x=0.1)
            st.plotly_chart(grafico_remoto, use_container_width=True)
        else:
            st.write("Nenhum dado disponível para exibir o gráfico dos tipos de trabalho remoto.")

    with col_graf4:
        if not df_filtrado.empty:
            df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
            media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
            grafico_paises = px.choropleth(
                media_ds_pais,
                locations = 'residencia_iso3',
                color = 'usd',
                title = 'Salario Medio de Data Scientists por País',
                labels = {'usd': "Salário Médio (USD)", 'residencia_iso3': "País"},
                color_continuous_scale="Viridis"  # <- Paleta de cores adicionada aqui
            )
            grafico_paises.update_layout(title_x=0.1)
            st.plotly_chart(grafico_paises, use_container_width=True)
        else:
            st.write("Nenhum dado disponível para exibir o gráfico de países.")


#--- Tabela de Dados Detalhados ---
st.subheader('Dados Detalhados')
st.dataframe(df_filtrado)
