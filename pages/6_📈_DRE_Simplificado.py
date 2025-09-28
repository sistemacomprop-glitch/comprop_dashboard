# pages/6_📈_DRE_Simplificado.py

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

st.title("📈_DRE_Simplificado")
st.header("Demonstração do Resultado (DRE Simplificado)")
st.write("Análise financeira baseada na classificação DRE para o período filtrado.")

# Calcula os totais para cada categoria do DRE
dre_summary = df_filtrado.groupby('Classificação DRE')['Total do Item'].sum()

# Pega os valores, usando .get(chave, 0) para evitar erros se uma categoria não existir
receita = dre_summary.get('Receita', 0)
deducoes = dre_summary.get('Dedução de Receita', 0)
custos = dre_summary.get('Custo', 0)
reducao_custos = dre_summary.get('Redução de Custo', 0)
despesas = dre_summary.get('Despesa', 0)

# Calcula os resultados
receita_liquida = receita - deducoes
resultado_bruto = receita_liquida - (custos - reducao_custos)
resultado_final = resultado_bruto - despesas

# Exibe o DRE
st.subheader("Estrutura do Resultado")
col1, col2 = st.columns([3, 1]) # Coluna do valor um pouco menor

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

# Gráfico de pizza para a composição das despesas
st.subheader("Composição das Despesas")
df_despesas = df_filtrado[df_filtrado['Classificação DRE'] == 'Despesa']
if not df_despesas.empty:
    despesas_por_operacao = df_despesas.groupby('Tipo de Operação')['Total do Item'].sum().nlargest(10)
    st.bar_chart(despesas_por_operacao)
else:
    st.info("Nenhuma despesa registrada no período filtrado.")