# app_utils.py
# Módulo com funções utilitárias para o app Streamlit.

import streamlit as st
import pandas as pd
import os
from datetime import date
from config import CAMINHO_LOGO, CAMINHO_EXCEL_LOCAL

@st.cache_data(ttl=600)
def carregar_dados():
    """Carrega os dados das duas abas (Movimentacoes e Estoque) do arquivo local."""
    if os.path.exists(CAMINHO_EXCEL_LOCAL):
        dados_excel = pd.read_excel(CAMINHO_EXCEL_LOCAL, sheet_name=None)
        df_mov = dados_excel.get('Movimentacoes', pd.DataFrame())
        df_est = dados_excel.get('Estoque', pd.DataFrame())
        
        # Limpeza de dados...
        if not df_mov.empty:
            df_mov.columns = df_mov.columns.str.strip()
            df_mov['Data Emissão'] = pd.to_datetime(df_mov['Data Emissão'], format='%d/%m/%Y', errors='coerce')
            df_mov['Data de Vencimento'] = pd.to_datetime(df_mov['Data de Vencimento'], format='%d/%m/%Y', errors='coerce')
        if not df_est.empty:
            df_est.columns = df_est.columns.str.strip()

        return df_mov, df_est
    return pd.DataFrame(), pd.DataFrame()

def construir_sidebar(df):
    """Cria a barra lateral com logo e filtros, e retorna o dataframe filtrado."""
    st.sidebar.image(CAMINHO_LOGO)
    st.sidebar.title("Painel de Controle")
    st.sidebar.warning("Modo: Local 💻")
    st.sidebar.divider()
    st.sidebar.header("Filtros de Análise")

    if df.empty:
        st.sidebar.warning("Nenhum dado carregado.")
        return pd.DataFrame()

    df_filtrado = df.copy()
    
    # Filtro de data fixo e estável por Data de Emissão
    ativar_filtro_data = st.sidebar.checkbox("Filtrar por Período", value=False)
    
    datas_validas = df['Data Emissão'].dropna()

    if ativar_filtro_data and not datas_validas.empty:
        data_min_default = datas_validas.min().date()
        data_max_default = datas_validas.max().date()
        data_inicial = st.sidebar.date_input("Data Inicial", data_min_default, min_value=data_min_default, max_value=data_max_default)
        data_final = st.sidebar.date_input("Data Final", data_max_default, min_value=data_inicial, max_value=data_max_default)
        df_filtrado = df_filtrado[df_filtrado['Data Emissão'].dt.date.between(data_inicial, data_final)]
    elif ativar_filtro_data and datas_validas.empty:
        st.sidebar.warning("Nenhuma data válida encontrada para filtrar.")

    # Filtros restantes
    clientes_unicos = sorted(df['Cliente'].astype(str).unique())
    if 'clientes_selecionados' not in st.session_state:
        st.session_state.clientes_selecionados = clientes_unicos

    col1, col2 = st.sidebar.columns(2)
    if col1.button("Selecionar Todos", use_container_width=True):
        st.session_state.clientes_selecionados = clientes_unicos
        st.rerun()
    if col2.button("Limpar Seleção", use_container_width=True):
        st.session_state.clientes_selecionados = []
        st.rerun()
    
    clientes_selecionados = st.sidebar.multiselect("Clientes", clientes_unicos, default=st.session_state.clientes_selecionados)
    
    item_pesquisado = st.sidebar.text_input("Pesquisar por nome do Item")
    nf_pesquisada = st.sidebar.text_input("Pesquisar por Nº da Nota")
    pagamento_pesquisado = st.sidebar.text_input("Pesquisar por Forma de Pagto")
    vendedor_pesquisado = st.sidebar.text_input("Pesquisar por Vendedor")

    if clientes_selecionados:
        df_filtrado = df_filtrado[df_filtrado['Cliente'].isin(clientes_selecionados)]
    if item_pesquisado:
        df_filtrado = df_filtrado[df_filtrado['Item Descrição'].str.contains(item_pesquisado, case=False, na=False)]
    if nf_pesquisada:
        df_filtrado = df_filtrado[df_filtrado['Nota'].astype(str).str.contains(nf_pesquisada, case=False, na=False)]
    if pagamento_pesquisado:
        df_filtrado = df_filtrado[df_filtrado['Forma de Pagto'].str.contains(pagamento_pesquisado, case=False, na=False)]
    if vendedor_pesquisado:
        df_filtrado = df_filtrado[df_filtrado['Representante'].str.contains(vendedor_pesquisado, case=False, na=False)]

    st.sidebar.divider()
    st.sidebar.header("Download de Dados")
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(label="📥 Baixar Dados Filtrados (.csv)", data=csv, file_name='dados_comprop_filtrados.csv', mime='text/csv', use_container_width=True)

    return df_filtrado