# pages/2_🏆_Ranking_de_Produtos.py

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

st.title("🏆_Ranking_de_Produtos")
st.header("Ranking de Produtos Mais Vendidos")
ranking_produtos = df_filtrado[df_filtrado['Movimentação'] == 'Saída'].groupby('Item Descrição').agg(
    Quantidade_Vendida=('Quantidade', 'sum'),
    Valor_Total_Vendido=('Total do Item', 'sum')
    ).sort_values(by='Valor_Total_Vendido', ascending=False).reset_index()
st.dataframe(ranking_produtos, width='stretch',
    column_config={"Valor_Total_Vendido": st.column_config.NumberColumn("Valor Total Vendido", format="R$ %.2f")}
    )
# --- Conteúdo da antiga Tab ---
