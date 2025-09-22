# app.py - Versão 6.0: Correção de perda de dados e adição de contadores (Completo)

import streamlit as st
import pandas as pd
import os
from PIL import Image
import time
import gspread
from gspread_dataframe import get_as_dataframe

# =================================================================================
# --- CONFIGURAÇÃO E ESTILO ---
# =================================================================================
st.set_page_config(page_title="COMPROP | Dashboard", layout="wide")
CAMINHO_LOGO = 'image_9b00e0.png' # A logo precisa estar na mesma pasta

def carregar_css():
    css = """
    <style>
        .stButton>button { background-color: #F37A24; color: white; }
        h1, h2, h3 { color: #004225; }
        .stMetric { background-color: #F0F2F6; border-radius: 10px; padding: 15px; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

carregar_css()

# =================================================================================
# --- CONEXÃO SEGURA E CARREGAMENTO DE DADOS DO GOOGLE SHEETS ---
# =================================================================================
def conectar_google_sheets():
    try:
        creds_dict = st.secrets["gcp_service_account"]
        gc = gspread.service_account_from_dict(creds_dict)
        spreadsheet = gc.open("COMPROP_Dashboard_Data")
        worksheet = spreadsheet.sheet1
        return worksheet
    except Exception as e:
        st.error("Falha na conexão com o Google Sheets. Verifique os 'Secrets' e o compartilhamento da planilha.")
        st.exception(e)
        return None

@st.cache_data(ttl=600)
def carregar_dados_online():
    worksheet = conectar_google_sheets()
    if worksheet:
        df = get_as_dataframe(worksheet, evaluate_formulas=True)
        df.dropna(how='all', inplace=True)
        
        colunas_essenciais = ['Data Emissão', 'Total do Item', 'Preço de Custo', 'Quantidade', 'Valor Unitário', 'Cliente', 'Item Descrição', 'Movimentação', 'Representante', 'Nota']
        for col in colunas_essenciais:
            if col not in df.columns:
                df[col] = pd.NA
        
        # A linha que removia dados com data vazia foi permanentemente retirada.
        df['Data Emissão'] = pd.to_datetime(df['Data Emissão'], errors='coerce')
        for col in ['Total do Item', 'Preço de Custo', 'Quantidade', 'Valor Unitário']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    return pd.DataFrame()

df = carregar_dados_online()

# =================================================================================
# --- BARRA LATERAL (SIDEBAR) COM FILTROS E DOWNLOAD ---
# =================================================================================
st.sidebar.image(CAMINHO_LOGO)
st.sidebar.title("Painel de Controle")
st.sidebar.divider()
st.sidebar.header("Filtros de Análise")

if not df.empty:
    df_filtrado = df.copy()

    # Filtro de Data (ignora datas vazias/NaT para definir o range)
    datas_validas = df_filtrado['Data Emissão'].dropna()
    data_min = datas_validas.min().date()
    data_max = datas_validas.max().date()
    
    data_inicial = st.sidebar.date_input("Data Inicial", data_min, min_value=data_min, max_value=data_max)
    data_final = st.sidebar.date_input("Data Final", data_max, min_value=data_inicial, max_value=data_max)

    clientes_unicos = sorted(df_filtrado['Cliente'].astype(str).unique())
    if 'clientes_selecionados' not in st.session_state:
        st.session_state.clientes_selecionados = clientes_unicos

    col1, col2 = st.sidebar.columns(2)
    if col1.button("Selecionar Todos", use_container_width=True):
        st.session_state.clientes_selecionados = clientes_unicos
    if col2.button("Limpar Seleção", use_container_width=True):
        st.session_state.clientes_selecionados = []
    
    clientes_selecionados = st.sidebar.multiselect("Clientes", clientes_unicos, key='clientes_selecionados')
    item_pesquisado = st.sidebar.text_input("Pesquisar por nome do Item")

    # Aplica os filtros
    df_filtrado = df_filtrado[
        (df_filtrado['Data Emissão'].dt.date >= data_inicial) &
        (df_filtrado['Data Emissão'].dt.date <= data_final) &
        (df_filtrado['Cliente'].isin(clientes_selecionados))
    ]
    if item_pesquisado:
        df_filtrado = df_filtrado[df_filtrado['Item Descrição'].str.contains(item_pesquisado, case=False, na=False)]
        
    st.sidebar.divider()
    st.sidebar.header("Download de Dados")

    csv = df_filtrado.to_csv(index=False).encode('utf-8')

    st.sidebar.download_button(
       label="📥 Baixar Dados Filtrados (.csv)",
       data=csv,
       file_name='dados_comprop_filtrados.csv',
       mime='text/csv',
       use_container_width=True
    )

else:
    st.sidebar.warning("Aguardando dados da nuvem...")
    df_filtrado = pd.DataFrame()

# =================================================================================
# --- PÁGINA PRINCIPAL COM DASHBOARD ---
# =================================================================================
st.title("Dashboard de Análise de Vendas")

if not df.empty:
    # Contador de Registros para transparência
    st.info(f"Exibindo **{len(df_filtrado):,}** de **{len(df):,}** registros totais.")
    st.divider()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard Geral", "📈 Entradas vs. Saídas", "🏆 Ranking de Produtos", 
        "👑 Ranking Vendedores", "📋 Consulta Detalhada"
    ])

    with tab1:
        tipo_analise = st.radio(
            "Selecione a visão do Dashboard:", ["Vendas", "Compras"], horizontal=True
        )
        st.divider()

        if tipo_analise == "Vendas":
            df_vendas = df_filtrado[df_filtrado['Movimentação'] == 'Saída']
            st.subheader("Resumo de Vendas")
            total_vendas = df_vendas['Total do Item'].sum()
            total_custo_vendas = (df_vendas['Custo Total']).sum()
            lucro_bruto = total_vendas - total_custo_vendas
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Vendas Totais", f"R$ {total_vendas:,.2f}")
            col2.metric("Custo das Vendas", f"R$ {total_custo_vendas:,.2f}")
            col3.metric("Lucro Bruto", f"R$ {lucro_bruto:,.2f}")

            st.subheader("Vendas por Cliente")
            vendas_por_cliente = df_vendas.groupby('Cliente')['Total do Item'].sum().sort_values(ascending=False)
            st.bar_chart(vendas_por_cliente)

        elif tipo_analise == "Compras":
            df_compras = df_filtrado[df_filtrado['Movimentação'] == 'Entrada']
            st.subheader("Resumo de Compras")
            total_compras = df_compras['Total do Item'].sum()
            num_notas_compra = df_compras['Nota'].nunique()

            col1, col2 = st.columns(2)
            col1.metric("Total de Compras", f"R$ {total_compras:,.2f}")
            col2.metric("Notas de Compra", f"{num_notas_compra}")

            st.subheader("Maiores Compras (por Fornecedor/Cliente)")
            compras_por_fornecedor = df_compras.groupby('Cliente')['Total do Item'].sum().sort_values(ascending=False).nlargest(15)
            st.bar_chart(compras_por_fornecedor)

    with tab2:
        st.header("Comparativo de Entradas vs. Saídas")
        movimentacao_diaria = df_filtrado.groupby([df_filtrado['Data Emissão'].dt.date, 'Movimentação'])['Total do Item'].sum().unstack(fill_value=0)
        st.bar_chart(movimentacao_diaria)
        st.dataframe(movimentacao_diaria)

    with tab3:
        st.header("Ranking de Produtos Mais Vendidos")
        ranking_produtos = df_filtrado[df_filtrado['Movimentação'] == 'Saída'].groupby('Item Descrição').agg(
            Quantidade_Vendida=('Quantidade', 'sum'),
            Valor_Total_Vendido=('Total do Item', 'sum')
        ).sort_values(by='Valor_Total_Vendido', ascending=False).reset_index()
        
        st.dataframe(ranking_produtos, width='stretch',
            column_config={"Valor_Total_Vendido": st.column_config.NumberColumn("Valor Total Vendido", format="R$ %.2f")}
        )

    with tab4:
        st.header("Ranking de Vendas por Vendedor (Representante)")
        df_vendedores = df_filtrado[(df_filtrado['Movimentação'] == 'Saída') & (df_filtrado['Representante'] != 'N/A')]
        if not df_vendedores.empty:
            ranking_vendedores = df_vendedores.groupby('Representante').agg(
                Valor_Total_Vendido=('Total do Item', 'sum'),
                Quantidade_de_Vendas=('Nota', 'nunique')
            ).sort_values(by='Valor_Total_Vendido', ascending=False).reset_index()
            st.dataframe(ranking_vendedores, width='stretch',
                column_config={"Valor_Total_Vendido": st.column_config.NumberColumn("Valor Total Vendido", format="R$ %.2f")}
            )
        else:
            st.info("Não há dados de vendas por representante para o período e filtros selecionados.")

    with tab5:
        st.header("Consulta Detalhada dos Dados Filtrados")
        st.dataframe(df_filtrado, width='stretch',
            column_config={
                "Valor Unitário": st.column_config.NumberColumn(format="R$ %.2f"),
                "Total do Item": st.column_config.NumberColumn(format="R$ %.2f"),
                "Preço de Venda": st.column_config.NumberColumn(format="R$ %.2f"),
                "Preço de Custo": st.column_config.NumberColumn(format="R$ %.2f"),
                "Custo Total": st.column_config.NumberColumn(format="R$ %.2f"),
            }
        )
else:
    st.info("Aguardando dados da nuvem... A planilha online pode estar vazia ou indisponível.")
    st.warning("Se a automação acabou de ser executada, pode levar alguns instantes para os dados atualizarem. Tente recarregar a página (F5).")