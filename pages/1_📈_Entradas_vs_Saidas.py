# pages/1_📈_Entradas_vs_Saidas.py

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

st.title("📈 Entradas vs. Saídas")
st.header("Comparativo de Entradas vs. Saídas")

# --- Conteúdo da antiga Tab 2 ---
movimentacao_diaria = df_filtrado.groupby([df_filtrado['Data Emissão'].dt.date, 'Movimentação'])['Total do Item'].sum().unstack(fill_value=0)
st.bar_chart(movimentacao_diaria)
st.dataframe(movimentacao_diaria)