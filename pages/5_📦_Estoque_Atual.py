# pages/5_📦_Estoque_Atual.py

import streamlit as st
from app_utils import carregar_dados, construir_sidebar

st.set_page_config(page_title="Entradas vs. Saídas", layout="wide")
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

df_movimentacoes, _ = carregar_dados() # Não precisamos do estoque aqui
df_filtrado = construir_sidebar(df_movimentacoes)

st.title("📦_Estoque_Atual")
st.header("Consulta de Estoque de Inventário")
# pages/5_📦_Estoque_Atual.py

import streamlit as st
import pandas as pd
from app_utils import carregar_dados, construir_sidebar

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Estoque Atual", layout="wide")
# (Você pode colar sua função carregar_css() aqui também se quiser o mesmo estilo)

# --- CARREGAMENTO DE DADOS E SIDEBAR ---
# Carregamos os dois dataframes, mas o principal para esta página é o df_estoque
df_movimentacoes, df_estoque = carregar_dados()

# Construímos a sidebar, mas não usaremos o df_filtrado retornado por ela nesta página
construir_sidebar(df_movimentacoes)

# --- CONTEÚDO DA PÁGINA DE ESTOQUE ---
st.title("📦 Estoque Atual")
st.markdown("Consulta do saldo e custo dos itens em estoque com base no último relatório de inventário.")
st.divider()

if not df_estoque.empty:
    # --- MÉTRICAS GERAIS DO ESTOQUE ---
    valor_total_estoque = df_estoque['Custo Total'].sum()
    num_itens_estoque = len(df_estoque)
    
    col1, col2 = st.columns(2)
    col1.metric("Itens Únicos em Estoque", f"{num_itens_estoque}")
    col2.metric("Valor Total do Estoque (Custo)", f"R$ {valor_total_estoque:,.2f}")
    st.divider()

    # --- PESQUISA E EXIBIÇÃO DA TABELA DE ESTOQUE ---
    st.subheader("Pesquisar Itens no Estoque")
    item_estoque_pesquisado = st.text_input(
        "Digite parte do nome do item para pesquisar:", 
        key="pesquisa_estoque"
    )
    
    df_estoque_filtrado = df_estoque
    if item_estoque_pesquisado:
        # Filtra o dataframe de estoque com base na pesquisa
        df_estoque_filtrado = df_estoque[
            df_estoque['Descrição'].str.contains(item_estoque_pesquisado, case=False, na=False)
        ]
    
    st.dataframe(df_estoque_filtrado, width='stretch',
        column_config={
            "Custo Unit.": st.column_config.NumberColumn("Custo Unitário", format="R$ %.2f"),
            "Custo Total": st.column_config.NumberColumn("Custo Total", format="R$ %.2f"),
        }
    )
else:
    st.warning("Não foram encontrados dados de estoque na planilha.")
    st.info("Execute o `main.py` para gerar o arquivo de dados com a aba 'Estoque'.")