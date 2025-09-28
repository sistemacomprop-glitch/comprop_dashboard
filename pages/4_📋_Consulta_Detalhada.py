# pages/4_📋_Consulta_Detalhada.py

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

st.title("📋_Consulta_Detalhada")
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
