# app.py - Versão corrigida com ajustes de layout e limpeza da interface

import streamlit as st
import pandas as pd
import os
from PIL import Image
import time

# Importamos a função principal que faz todo o trabalho pesado do nosso outro arquivo.
from automatizadorstream import executar_processo_completo

# =================================================================================
# --- CONFIGURAÇÃO DE CAMINHOS ---
# =================================================================================
PASTA_RAIZ_RELATORIOS = r'C:\Users\consultor.ale\Desktop\Mamede\Relatórios\MOVIMENTACOES'
PALAVRA_CHAVE_INVENTARIO = 'ppReport1inventario'
CAMINHO_EXCEL_FINAL = r'G:\Meu Drive\Relatorio_Final_App.xlsx'
CAMINHO_LOGO = r'C:\Users\consultor.ale\Desktop\Mamede\image_9b00e0.png'


# =================================================================================
# --- ESTILO E CONFIGURAÇÃO DA PÁGINA ---
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
# --- FUNÇÃO DE CACHE PARA CARREGAR OS DADOS ---
# =================================================================================
@st.cache_data
def carregar_dados(caminho_arquivo):
    if os.path.exists(caminho_arquivo):
        try:
            df = pd.read_excel(caminho_arquivo)
            df['Data Emissão'] = pd.to_datetime(df['Data Emissão'], format='%d/%m/%Y', errors='coerce')
            for col in ['Total do Item', 'Preço de Custo', 'Quantidade', 'Valor Unitário']:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', '').str.replace(',', '.'), errors='coerce').fillna(0)
            return df
        except Exception as e:
            st.error(f"Erro ao carregar ou processar o arquivo Excel: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

df = carregar_dados(CAMINHO_EXCEL_FINAL)

# =================================================================================
# --- BARRA LATERAL (SIDEBAR) ---
# =================================================================================
st.sidebar.image(CAMINHO_LOGO)
st.sidebar.title("Painel de Controle")
st.sidebar.divider()

st.sidebar.header("Executar Automação")
if st.sidebar.button("▶️ Iniciar Extração de Dados", type="primary"):
    with st.spinner('Aguarde... O robô está trabalhando...'):
        try:
            df_resultado = executar_processo_completo(PASTA_RAIZ_RELATORIOS, PALAVRA_CHAVE_INVENTARIO)
            df_resultado.to_excel(CAMINHO_EXCEL_FINAL, index=False)
            st.cache_data.clear()
            st.success("Automação concluída com sucesso! A página será recarregada com os novos dados.")
            st.balloons()
            time.sleep(3)
            st.rerun()
        except Exception as e:
            st.sidebar.error("Ocorreu um erro na automação.")
            st.exception(e)

st.sidebar.divider()
st.sidebar.header("Filtros de Análise")

if not df.empty:
    data_min = df['Data Emissão'].min().date()
    data_max = df['Data Emissão'].max().date()
    data_inicial = st.sidebar.date_input("Data Inicial", data_min, min_value=data_min, max_value=data_max)
    data_final = st.sidebar.date_input("Data Final", data_max, min_value=data_inicial, max_value=data_max)

    clientes_unicos = sorted(df['Cliente'].unique())
    if 'clientes_selecionados' not in st.session_state:
        st.session_state.clientes_selecionados = clientes_unicos

    col1, col2 = st.sidebar.columns(2)
    if col1.button("Selecionar Todos", use_container_width=True):
        st.session_state.clientes_selecionados = clientes_unicos
    if col2.button("Limpar Seleção", use_container_width=True):
        st.session_state.clientes_selecionados = []
    
    # --- CORREÇÃO: O seletor de clientes agora está corretamente na sidebar ---
    clientes_selecionados = st.sidebar.multiselect("Clientes", clientes_unicos, key='clientes_selecionados')
    
    item_pesquisado = st.sidebar.text_input("Pesquisar por nome do Item")

    df_filtrado = df[
        (df['Data Emissão'].dt.date >= data_inicial) &
        (df['Data Emissão'].dt.date <= data_final) &
        (df['Cliente'].isin(clientes_selecionados))
    ]
    if item_pesquisado:
        df_filtrado = df_filtrado[df_filtrado['Item Descrição'].str.contains(item_pesquisado, case=False, na=False)]
else:
    st.sidebar.warning("Execute a automação para habilitar os filtros.")

# =================================================================================
# --- PÁGINA PRINCIPAL COM ABAS ---
# =================================================================================
st.title("Dashboard de Análise de Vendas")

if not df.empty:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard Geral", "📈 Entradas vs. Saídas", "🏆 Ranking de Produtos", 
        "👑 Ranking Vendedores", "📋 Consulta Detalhada"
    ])

    with tab1:
        # --- CORREÇÃO: Título removido e seletor agora é o principal elemento ---
        tipo_analise = st.radio(
            "Selecione a visão do Dashboard:",
            ["Vendas", "Compras"],
            horizontal=True
        )
        st.divider()

        if tipo_analise == "Vendas":
            df_vendas = df_filtrado[df_filtrado['Movimentação'] == 'Saída']
            
            st.subheader("Resumo de Vendas")
            total_vendas = df_vendas['Total do Item'].sum()
            total_custo_vendas = (df_vendas['Preço de Custo'] * df_vendas['Quantidade']).sum()
            lucro_bruto = total_vendas - total_custo_vendas
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Vendas Totais", f"R$ {total_vendas:,.2f}")
            col2.metric("Custo das Vendas", f"R$ {total_custo_vendas:,.2f}")
            col3.metric("Lucro Bruto", f"R$ {lucro_bruto:,.2f}")

            # --- CORREÇÃO: Gráfico de Top Produtos foi removido desta aba ---

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

    # O restante das abas continua o mesmo
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
        
        st.dataframe(ranking_produtos, height=500, use_container_width=True,
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
            st.dataframe(ranking_vendedores, use_container_width=True,
                column_config={"Valor_Total_Vendido": st.column_config.NumberColumn("Valor Total Vendido", format="R$ %.2f")}
            )
        else:
            st.info("Não há dados de vendas por representante para o período e filtros selecionados.")

    with tab5:
        st.header("Consulta Detalhada dos Dados Filtrados")
        st.dataframe(df_filtrado, use_container_width=True,
            column_config={
                "Valor Unitário": st.column_config.NumberColumn(format="R$ %.2f"),
                "Total do Item": st.column_config.NumberColumn(format="R$ %.2f"),
                "Preço de Venda": st.column_config.NumberColumn(format="R$ %.2f"),
                "Preço de Custo": st.column_config.NumberColumn(format="R$ %.2f"),
            }
        )
else:
    st.info("Ainda não há dados para exibir. Por favor, execute a automação na barra lateral.")