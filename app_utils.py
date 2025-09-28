# app_utils.py (Versão Final com Lógica Online/Offline)

import streamlit as st
import pandas as pd
import os
from datetime import date
import gspread
from gspread_dataframe import get_as_dataframe

# Importa as configurações do arquivo central
from config import CAMINHO_LOGO, CAMINHO_EXCEL_LOCAL, MODO_ONLINE, NOME_PLANILHA_ONLINE

def _limpar_df_movimentacoes(df):
    """Função interna para limpar o dataframe de movimentações."""
    if not df.empty:
        df.columns = df.columns.str.strip()
        if 'Data Emissão' in df.columns:
            df['Data Emissão'] = pd.to_datetime(df['Data Emissão'], format='%d/%m/%Y', errors='coerce')
        if 'Data de Vencimento' in df.columns:
            df['Data de Vencimento'] = pd.to_datetime(df['Data de Vencimento'], format='%d/%m/%Y', errors='coerce')
    return df

def _limpar_df_estoque(df):
    """Função interna para limpar o dataframe de estoque."""
    if not df.empty:
        df.columns = df.columns.str.strip()
        for col in ['Saldo', 'Custo Unit.', 'Custo Total']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce').fillna(0)
    return df

@st.cache_data(ttl=600)
def carregar_dados():
    """Função mestra que decide se carrega os dados do arquivo local ou online."""
    if MODO_ONLINE:
        try:
            creds_dict = st.secrets["gcp_service_account"]
            gc = gspread.service_account_from_dict(creds_dict)
            spreadsheet = gc.open(NOME_PLANILHA_ONLINE)
            
            mov_sheet = spreadsheet.worksheet('Movimentacoes')
            est_sheet = spreadsheet.worksheet('Estoque')
            
            df_mov = get_as_dataframe(mov_sheet, evaluate_formulas=True)
            df_est = get_as_dataframe(est_sheet, evaluate_formulas=True)
            
            return _limpar_df_movimentacoes(df_mov), _limpar_df_estoque(df_est)

        except Exception as e:
            st.error("Falha ao carregar dados online.")
            st.exception(e)
            return pd.DataFrame(), pd.DataFrame()
    else: # Modo Local
        try:
            if os.path.exists(CAMINHO_EXCEL_LOCAL):
                dados_excel = pd.read_excel(CAMINHO_EXCEL_LOCAL, sheet_name=None)
                df_mov = dados_excel.get('Movimentacoes', pd.DataFrame())
                df_est = dados_excel.get('Estoque', pd.DataFrame())
                return _limpar_df_movimentacoes(df_mov), _limpar_df_estoque(df_est)
            else:
                return pd.DataFrame(), pd.DataFrame()
        except Exception as e:
            st.error(f"Erro ao carregar o arquivo Excel local: {e}")
            return pd.DataFrame(), pd.DataFrame()

def construir_sidebar(df):
    """Cria a barra lateral com logo e filtros, e retorna o dataframe filtrado."""
    st.sidebar.image(CAMINHO_LOGO)
    st.sidebar.title("Painel de Controle")
    if MODO_ONLINE:
        st.sidebar.success("Modo: Online ☁️")
    else:
        st.sidebar.warning("Modo: Local 💻")
    st.sidebar.divider()
    st.sidebar.header("Filtros de Análise")

    if df.empty:
        st.sidebar.warning("Nenhum dado de movimentação carregado.")
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