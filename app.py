# app.py - Versão 10.1: Definitiva, Completa e Funcional (Online/Offline)

import streamlit as st
import pandas as pd
import os
from PIL import Image
import time
import gspread
from gspread_dataframe import get_as_dataframe
from datetime import date

# Importa as configurações do arquivo central
from config import CAMINHO_LOGO, CAMINHO_EXCEL_LOCAL, NOME_PLANILHA_ONLINE

# =================================================================================
# --- CHAVE SELETORA DE MODO DE OPERAÇÃO ---
# =================================================================================
# Mude para True para usar a Planilha Google (quando a API estiver ativa)
# Mude para False para usar o arquivo Excel local
MODO_ONLINE = True 

# =================================================================================
# --- CONFIGURAÇÃO E ESTILO ---
# =================================================================================
st.set_page_config(page_title="COMPROP | Dashboard", layout="wide")

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
# --- FUNÇÕES DE CARREGAMENTO DE DADOS ---
# =================================================================================

def conectar_google_sheets():
    """Conecta ao Google Sheets usando os Secrets do Streamlit."""
    try:
        creds_dict = st.secrets["gcp_service_account"]
        gc = gspread.service_account_from_dict(creds_dict)
        spreadsheet = gc.open(NOME_PLANILHA_ONLINE)
        return spreadsheet
    except Exception as e:
        st.error("Falha na conexão com o Google Sheets.")
        st.exception(e)
        return None

@st.cache_data(ttl=600)
def carregar_dados_online():
    """Carrega dados das abas 'Movimentacoes' e 'Estoque' da Planilha Google."""
    spreadsheet = conectar_google_sheets()
    if spreadsheet:
        try:
            mov_sheet = spreadsheet.worksheet('Movimentacoes')
            est_sheet = spreadsheet.worksheet('Estoque')
            
            df_mov = get_as_dataframe(mov_sheet, evaluate_formulas=True)
            df_est = get_as_dataframe(est_sheet, evaluate_formulas=True)

            # Limpeza do DataFrame de Movimentações
            if not df_mov.empty:
                df_mov.dropna(how='all', inplace=True)
                df_mov.columns = df_mov.columns.str.strip()
                if 'Data Emissão' in df_mov.columns:
                    df_mov['Data Emissão'] = pd.to_datetime(df_mov['Data Emissão'], format='%d/%m/%Y', errors='coerce')
                if 'Data de Vencimento' in df_mov.columns:
                    df_mov['Data de Vencimento'] = pd.to_datetime(df_mov['Data de Vencimento'], format='%d/%m/%Y', errors='coerce')

            # Limpeza do DataFrame de Estoque
            if not df_est.empty:
                df_est.dropna(how='all', inplace=True)
                df_est.columns = df_est.columns.str.strip()
            
            return df_mov, df_est
        except Exception as e:
            st.error(f"Erro ao ler as abas da Planilha Google: {e}")
            return pd.DataFrame(), pd.DataFrame()
    return pd.DataFrame(), pd.DataFrame()


def carregar_dados_locais(caminho_arquivo):
    """Carrega dados das abas 'Movimentacoes' e 'Estoque' de um arquivo Excel."""
    try:
        if os.path.exists(caminho_arquivo):
            dados_excel = pd.read_excel(caminho_arquivo, sheet_name=None)
            
            df_mov = dados_excel.get('Movimentacoes', pd.DataFrame())
            df_est = dados_excel.get('Estoque', pd.DataFrame())
            
            # Limpeza do DataFrame de Movimentações
            if not df_mov.empty:
                df_mov.columns = df_mov.columns.str.strip()
                if 'Data Emissão' in df_mov.columns:
                    df_mov['Data Emissão'] = pd.to_datetime(df_mov['Data Emissão'], errors='coerce')
                if 'Data de Vencimento' in df_mov.columns:
                    df_mov['Data de Vencimento'] = pd.to_datetime(df_mov['Data de Vencimento'], errors='coerce')
                for col in ['Total do Item', 'Preço de Custo', 'Quantidade', 'Valor Unitário']:
                    if col in df_mov.columns:
                        df_mov[col] = pd.to_numeric(df_mov[col], errors='coerce').fillna(0)

            # Limpeza do DataFrame de Estoque
            if not df_est.empty:
                df_est.columns = df_est.columns.str.strip()
                for col in ['Saldo', 'Custo Unit.', 'Custo Total']:
                     if col in df_est.columns:
                        df_est[col] = pd.to_numeric(df_est[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce').fillna(0)

            return df_mov, df_est
        else:
            return pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo Excel local: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Lógica que escolhe de onde carregar os dados
if MODO_ONLINE:
    st.sidebar.success("Modo: Online ☁️")
    df_movimentacoes, df_estoque = carregar_dados_online()
else:
    st.sidebar.warning("Modo: Local 💻")
    df_movimentacoes, df_estoque = carregar_dados_locais(CAMINHO_EXCEL_LOCAL)

# Define o dataframe principal para os filtros
df = df_movimentacoes

# =================================================================================
# --- BARRA LATERAL (SIDEBAR) ---
# =================================================================================
st.sidebar.image(CAMINHO_LOGO)
st.sidebar.title("Painel de Controle")
st.sidebar.divider()
st.sidebar.header("Filtros de Análise")

df_filtrado = df.copy() if not df.empty else pd.DataFrame()

if not df.empty:
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
else:
    st.sidebar.warning("Nenhum dado carregado.")

# =================================================================================
# --- PÁGINA PRINCIPAL COM DASHBOARD ---
# =================================================================================
st.title("Dashboard de Análise e Estoque")

if not df.empty:
    st.info(f"Exibindo **{len(df_filtrado):,}** de **{len(df):,}** registros totais (movimentações).")
    st.divider()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dashboard Geral", "📈 Entradas vs. Saídas", "🏆 Ranking de Produtos", 
        "👑 Ranking Vendedores", "📋 Consulta Detalhada", "📦 Estoque Atual"
    ])

    with tab1:
        tipo_analise = st.radio("Selecione a visão do Dashboard:", ["Vendas", "Compras"], horizontal=True)
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
        st.header("Consulta Detalhada das Movimentações")
        st.dataframe(df_filtrado, width='stretch',
            column_config={
                "Data Emissão": st.column_config.DateColumn("Data de Emissão", format="DD/MM/YYYY"),
                "Data de Vencimento": st.column_config.DateColumn("Data de Vencimento", format="DD/MM/YYYY"),
                "Valor Unitário": st.column_config.NumberColumn(format="R$ %.2f"),
                "Total do Item": st.column_config.NumberColumn(format="R$ %.2f"),
                "Preço de Venda": st.column_config.NumberColumn(format="R$ %.2f"),
                "Preço de Custo": st.column_config.NumberColumn(format="R$ %.2f"),
                "Custo Total": st.column_config.NumberColumn(format="R$ %.2f"),
            }
        )
    
    with tab6:
        st.header("Consulta de Estoque de Inventário")
        if not df_estoque.empty:
            valor_total_estoque = df_estoque['Custo Total'].sum()
            num_itens_estoque = len(df_estoque)
            col1, col2 = st.columns(2)
            col1.metric("Itens Únicos em Estoque", f"{num_itens_estoque}")
            col2.metric("Valor Total do Estoque (Custo)", f"R$ {valor_total_estoque:,.2f}")
            st.divider()
            
            item_estoque_pesquisado = st.text_input("Pesquisar por item no estoque:", key="pesquisa_estoque")
            df_estoque_filtrado = df_estoque
            if item_estoque_pesquisado:
                df_estoque_filtrado = df_estoque[df_estoque['Descrição'].str.contains(item_estoque_pesquisado, case=False, na=False)]
            
            st.dataframe(df_estoque_filtrado, width='stretch',
                column_config={
                    "Custo Unit.": st.column_config.NumberColumn("Custo Unitário", format="R$ %.2f"),
                    "Custo Total": st.column_config.NumberColumn("Custo Total", format="R$ %.2f"),
                }
            )
        else:
            st.warning("Não foram encontrados dados de estoque na planilha.")
else:
    if MODO_ONLINE:
        st.info("Aguardando dados da nuvem... A planilha online pode estar vazia ou indisponível.")
    else:
        st.info(f"Arquivo '{CAMINHO_EXCEL_LOCAL}' não encontrado. Execute o 'main.py' primeiro para gerar os dados.")