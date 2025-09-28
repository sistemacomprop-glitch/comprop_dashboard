# app.py (Nova versão - Página Principal)

import streamlit as st
from app_utils import carregar_dados, construir_sidebar

st.set_page_config(page_title="COMPROP | Dashboard Geral", layout="wide")
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

df_movimentacoes, df_estoque = carregar_dados()
df_filtrado = construir_sidebar(df_movimentacoes)

st.title("📊 Dashboard Geral")
st.info(f"Exibindo **{len(df_filtrado):,}** de **{len(df_movimentacoes):,}** registros totais (movimentações).")
st.divider()

# --- Conteúdo do Dashboard Geral (antiga Tab 1) ---
# (Cole aqui o código da sua antiga "tab1", com o seletor de Vendas/Compras, métricas e gráficos)
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