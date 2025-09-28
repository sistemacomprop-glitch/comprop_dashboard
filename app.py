# app.py - Versão 11.0: Versão Estável Definitiva (Estrutura de Arquivo Único)

import streamlit as st
import pandas as pd
import os
from PIL import Image
from datetime import date
import gspread
from gspread_dataframe import get_as_dataframe


# Importa as configurações do arquivo central
from config import CAMINHO_LOGO, CAMINHO_EXCEL_LOCAL, MODO_ONLINE, NOME_PLANILHA_ONLINE

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
# --- FUNÇÕES DE CARREGAMENTO DE DADOS (Agora centralizadas aqui) ---
# =================================================================================
@st.cache_data(ttl=600)
def carregar_dados():
    """
    Função mestra que carrega os dados do local correto (local ou online)
    e retorna dois dataframes: movimentações e estoque.
    """
    df_mov, df_est = pd.DataFrame(), pd.DataFrame() # Inicia dataframes vazios

    if MODO_ONLINE:
        try:
            # Lógica para carregar do Google Sheets
            creds_dict = st.secrets["gcp_service_account"]
            gc = gspread.service_account_from_dict(creds_dict)
            spreadsheet = gc.open(NOME_PLANILHA_ONLINE)
            mov_sheet = spreadsheet.worksheet('Movimentacoes')
            est_sheet = spreadsheet.worksheet('Estoque')
            df_mov = get_as_dataframe(mov_sheet, evaluate_formulas=True)
            df_est = get_as_dataframe(est_sheet, evaluate_formulas=True)
        except Exception as e:
            st.error("Falha ao carregar dados online.")
            st.exception(e)
            
    else: # Modo Local
        try:
            if os.path.exists(CAMINHO_EXCEL_LOCAL):
                dados_excel = pd.read_excel(CAMINHO_EXCEL_LOCAL, sheet_name=None)
                df_mov = dados_excel.get('Movimentacoes', pd.DataFrame())
                df_est = dados_excel.get('Estoque', pd.DataFrame())
            else:
                 st.error(f"Arquivo local não encontrado: {CAMINHO_EXCEL_LOCAL}")
        except Exception as e:
            st.error(f"Erro ao carregar o arquivo Excel local: {e}")

    # --- LIMPEZA DE DADOS CENTRALIZADA ---
    # Limpeza do DataFrame de Movimentações
    if not df_mov.empty:
        df_mov.columns = df_mov.columns.str.strip()
        if 'Data Emissão' in df_mov.columns:
            df_mov['Data Emissão'] = pd.to_datetime(df_mov['Data Emissão'], format='%d/%m/%Y', errors='coerce')
        if 'Data de Vencimento' in df_mov.columns:
            df_mov['Data de Vencimento'] = pd.to_datetime(df_mov['Data de Vencimento'], format='%d/%m/%Y', errors='coerce')

    # Limpeza do DataFrame de Estoque
    if not df_est.empty:
        df_est.columns = df_est.columns.str.strip()
        for col in ['Saldo', 'Custo Unit.', 'Custo Total']:
             if col in df_est.columns:
                df_est[col] = pd.to_numeric(df_est[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce').fillna(0)

    return df_mov, df_est

# Carrega os dados uma única vez no início do script
df_movimentacoes, df_estoque = carregar_dados()
df = df_movimentacoes # Define o df principal para os filtros

# =================================================================================
# --- BARRA LATERAL (SIDEBAR) ---
# =================================================================================
st.sidebar.image(CAMINHO_LOGO)
st.sidebar.title("Painel de Controle")
if MODO_ONLINE:
    st.sidebar.success("Modo: Online ☁️")
else:
    st.sidebar.warning("Modo: Local 💻")
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

    tab_list = [
        "📊 Dashboard Geral", "📈 Entradas vs. Saídas", "🏆 Ranking de Produtos", 
        "👑 Ranking Vendedores", "📋 Consulta Detalhada", "📦 Estoque Atual",
        "📈 DRE Simplificado"
    ]
    
    if 'Classificação DRE' not in df.columns:
        st.error("A coluna 'Classificação DRE' não foi encontrada. A aba de DRE não pode ser gerada.")
        tabs = st.tabs(tab_list[:-1])
    else:
        tabs = st.tabs(tab_list)

    with tabs[0]: # Dashboard Geral
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

    with tabs[1]: # Entradas vs. Saídas
        st.header("Comparativo de Entradas vs. Saídas")
        movimentacao_diaria = df_filtrado.groupby([df_filtrado['Data Emissão'].dt.date, 'Movimentação'])['Total do Item'].sum().unstack(fill_value=0)
        st.bar_chart(movimentacao_diaria)
        st.dataframe(movimentacao_diaria)

    with tabs[2]: # Ranking de Produtos
        st.header("Ranking de Produtos Mais Vendidos")
        ranking_produtos = df_filtrado[df_filtrado['Movimentação'] == 'Saída'].groupby('Item Descrição').agg(
            Quantidade_Vendida=('Quantidade', 'sum'),
            Valor_Total_Vendido=('Total do Item', 'sum')
        ).sort_values(by='Valor_Total_Vendido', ascending=False).reset_index()
        st.dataframe(ranking_produtos, width='stretch',
            column_config={"Valor_Total_Vendido": st.column_config.NumberColumn("Valor Total Vendido", format="R$ %.2f")}
        )

    with tabs[3]: # Ranking Vendedores
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

    with tabs[4]: # Consulta Detalhada
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
    
    with tabs[5]: # Estoque Atual
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
    
    if 'Classificação DRE' in df_filtrado.columns:
        with tabs[6]: # DRE Simplificado
            st.header("Demonstração do Resultado (DRE Simplificado)")
            st.write("Análise financeira baseada na classificação DRE para o período filtrado.")
            
            dre_summary = df_filtrado.groupby('Classificação DRE')['Total do Item'].sum()

            receita = dre_summary.get('Receita', 0)
            deducoes = dre_summary.get('Dedução de Receita', 0)
            custos = dre_summary.get('Custo', 0)
            reducao_custos = dre_summary.get('Redução de Custo', 0)
            despesas = dre_summary.get('Despesa', 0)
            
            receita_liquida = receita - deducoes
            resultado_bruto = receita_liquida - (custos - reducao_custos)
            resultado_final = resultado_bruto - despesas

            st.subheader("Estrutura do Resultado")
            col1, col2 = st.columns([3, 1])
            col1.text("(=) Receita Operacional Bruta")
            col2.metric("", f"R$ {receita:,.2f}")
            col1.text("(-) Deduções da Receita")
            col2.metric("", f"R$ {deducoes:,.2f}")
            col1.markdown("**(=) Receita Operacional Líquida**")
            col2.metric("", f"**R$ {receita_liquida:,.2f}**")
            col1.text("(-) Custo (Mercadorias e Serviços)")
            col2.metric("", f"R$ {custos - reducao_custos:,.2f}")
            col1.markdown("**(=) Resultado Bruto (Lucro Bruto)**")
            col2.metric("", f"**R$ {resultado_bruto:,.2f}**")
            col1.text("(-) Despesas Operacionais")
            col2.metric("", f"R$ {despesas:,.2f}")
            st.divider()
            col1.markdown("### (=) Resultado Líquido do Período")
            col2.metric("", f"### R$ {resultado_final:,.2f}")
            st.divider()
            
            st.subheader("Composição das Despesas")
            df_despesas = df_filtrado[df_filtrado['Classificação DRE'] == 'Despesa']
            if not df_despesas.empty:
                despesas_por_operacao = df_despesas.groupby('Tipo de Operação')['Total do Item'].sum().nlargest(10)
                st.bar_chart(despesas_por_operacao)
            else:
                st.info("Nenhuma despesa registrada no período filtrado.")
else:
    if MODO_ONLINE:
        st.info("Aguardando dados da nuvem... A planilha online pode estar vazia ou indisponível.")
    else:
        st.info(f"Arquivo '{CAMINHO_EXCEL_LOCAL}' não encontrado. Execute o 'main.py' primeiro para gerar os dados.")