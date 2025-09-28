# app.py - Versão 11.0: Versão Estável Definitiva (Estrutura de Arquivo Único)

import streamlit as st
import pandas as pd
import os
from PIL import Image
from datetime import date
import gspread
from gspread_dataframe import get_as_dataframe
import io

# Importa as configurações do arquivo central
from config import CAMINHO_LOGO, CAMINHO_EXCEL_LOCAL, MODO_ONLINE, NOME_PLANILHA_ONLINE

# Adicione esta função no início do seu app.py

def formatar_numero_br(valor):
    """
    Formata um número float para o padrão de moeda brasileira (ex: R$ 1.234,56).
    """
    # 1. Usa um f-string para formatar o número com vírgulas de milhar e 2 casas decimais (padrão US)
    # Ex: 1234.56 -> "1,234.56"
    numero_us = f"{valor:,.2f}"
    
    # 2. Inverte os separadores de forma segura
    #    - Troca ',' por um caractere temporário '#'
    #    - Troca '.' por ','
    #    - Troca o caractere temporário '#' por '.'
    numero_br = numero_us.replace(',', '#').replace('.', ',').replace('#', '.')
    
    return f"R$ {numero_br}"

# =================================================================================
# --- CONFIGURAÇÃO E ESTILO ---
# =================================================================================
st.set_page_config(page_title="COMPROP | Dashboard", layout="wide")

def carregar_css():
    css = """
    <style>
        .stButton>button { background-color: #F37A24; color: white; }
        h1, h2, h3 { color: #004225; }
        .stMetric { 
            background-color: #F0F2F6; /* Cor para o modo claro (padrão) */
            border-radius: 10px; 
            padding: 15px; 
        }

        /* Aplica estes estilos apenas quando o tema do dispositivo/navegador for escuro */
        @media (prefers-color-scheme: dark) {
            .stMetric {
                background-color: #333842; /* Um cinza mais escuro para o fundo */
                color: white;             /* Garante que o texto da métrica seja branco */
            }
            /* Opcional: Garante que o texto do rótulo também seja visível */
            div[data-testid="stMetricLabel"] > div {
                color: #A5A8B1; /* Um cinza claro para o rótulo */
            }
        }
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

    # Limpeza do DataFrame de Estoque com lógica de conversão robusta
    if not df_est.empty:
        df_est.columns = df_est.columns.str.strip()
        
        # Função auxiliar para limpar e converter os números de forma segura
        def clean_and_convert_decimal(series):
            # 1. Garante que tudo é string e troca vírgula por ponto para padronizar o decimal
            temp_series = series.astype(str).str.replace(',', '.', regex=False)

            # 2. Função interna para remover os pontos de milhar, preservando o último ponto (decimal)
            def remove_thousands_separator(value):
                # Ignora valores nulos ou inválidos
                if pd.isna(value) or value is None:
                    return None
                parts = str(value).split('.')
                # Se o número tiver múltiplos pontos (ex: 1.234.56), junta a parte inteira
                if len(parts) > 1:
                    return "".join(parts[:-1]) + "." + parts[-1]
                # Se não tiver ponto ou tiver apenas um, retorna como está
                return value

            # 3. Aplica a limpeza e converte para o formato numérico final
            cleaned_series = temp_series.apply(remove_thousands_separator)
            return pd.to_numeric(cleaned_series, errors='coerce').fillna(0)

        # Aplica a função de limpeza nas colunas numéricas do estoque
        for col in ['Saldo', 'Custo Unit.', 'Custo Total']:
             if col in df_est.columns:
                df_est[col] = clean_and_convert_decimal(df_est[col])

    return df_mov, df_est

# Carrega os dados uma única vez no início do script
df_movimentacoes, df_estoque = carregar_dados()
df = df_movimentacoes # Define o df principal para os filtros

# =================================================================================
# --- BARRA LATERAL (SIDEBAR) ---
# =================================================================================
st.sidebar.image(CAMINHO_LOGO)
st.sidebar.title("Painel de Controle")

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
    # --- BLOCO PARA GERAR XLSX ---
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_filtrado.to_excel(writer, index=False, sheet_name='Dados')
    excel_data = output.getvalue()
    st.sidebar.download_button(
        label="📥 Baixar Dados Filtrados (.xlsx)",
        data=excel_data,
        file_name='dados_comprop_filtrados.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        use_container_width=True
    )
else:
    st.sidebar.warning("Nenhum dado carregado.")

# =================================================================================
# --- PÁGINA PRINCIPAL COM DASHBOARD ---
# =================================================================================
st.title("Dashboard de Análise e Estoque")

if not df.empty:
    st.info(f"Exibindo **{len(df_filtrado):,}** de **{len(df):,}** registros totais (movimentações).")
    st.divider()

    # --- INÍCIO DA CORREÇÃO ---
    # Reordenando a lista de abas para dar destaque ao DRE
    tab_list = [
        "📊 Dashboard Geral", 
        "📈 DRE Simplificado",
        "📈 Entradas vs. Saídas", 
        "🏆 Ranking de Produtos", 
        "👑 Ranking Vendedores", 
        "📋 Consulta Detalhada", 
        "📦 Estoque Atual"
    ]
    # --- FIM DA CORREÇÃO ---
    
    if 'Classificação DRE' not in df.columns:
        st.error("A coluna 'Classificação DRE' não foi encontrada. A aba de DRE não pode ser gerada.")
        # Remove a aba DRE da lista se a coluna não existir
        tab_list.pop(1) 
    
    tabs = st.tabs(tab_list)

    with tabs[0]: # Dashboard Geral
        tipo_analise = st.radio("Selecione a visão do Dashboard:", ["Vendas", "Compras"], horizontal=True)
        if tipo_analise == "Vendas":
            df_vendas = df_filtrado[df_filtrado['Movimentação'] == 'Saída']
            st.subheader("Resumo de Vendas")
            total_vendas = df_vendas['Total do Item'].sum()
            total_custo_vendas = (df_vendas['Custo Total']).sum()
            lucro_bruto = total_vendas - total_custo_vendas
            col1, col2, col3 = st.columns(3)
            col1.metric("Vendas Totais", formatar_numero_br(total_vendas))
            col2.metric("Custo das Vendas", formatar_numero_br(total_custo_vendas))
            col3.metric("Lucro Bruto", formatar_numero_br(lucro_bruto))
            st.subheader("Vendas por Cliente")
            vendas_por_cliente = df_vendas.groupby('Cliente')['Total do Item'].sum().sort_values(ascending=False)
            st.bar_chart(vendas_por_cliente)
        elif tipo_analise == "Compras":
            df_compras = df_filtrado[df_filtrado['Movimentação'] == 'Entrada']
            st.subheader("Resumo de Compras")
            total_compras = df_compras['Total do Item'].sum()
            num_notas_compra = df_compras['Nota'].nunique()
            col1, col2 = st.columns(2)
            col1.metric("Total de Compras", formatar_numero_br(total_compras))
            col2.metric("Notas de Compra", f"{num_notas_compra}")
            st.subheader("Maiores Compras (por Fornecedor/Cliente)")
            compras_por_fornecedor = df_compras.groupby('Cliente')['Total do Item'].sum().sort_values(ascending=False).nlargest(15)
            st.bar_chart(compras_por_fornecedor)

    # A lógica de exibição das abas agora segue a nova ordem
    # A aba DRE será a segunda (índice 1)
    
    if 'Classificação DRE' in df_filtrado.columns:
        with tabs[1]: # DRE Simplificado
            st.header("Demonstração do Resultado (DRE Simplificado)")
            st.write("Análise financeira baseada na classificação DRE para o período filtrado.")
            
            # Calcula os totais para cada categoria do DRE
            dre_summary = df_filtrado.groupby('Classificação DRE')['Total do Item'].sum()

            receita = dre_summary.get('Receita', 0)
            deducoes = dre_summary.get('Dedução de Receita', 0)
            custos = dre_summary.get('Custo', 0)
            reducao_custos = dre_summary.get('Redução de Custo', 0)
            despesas = dre_summary.get('Despesa', 0)
            
            receita_liquida = receita - deducoes
            resultado_bruto = receita_liquida - (custos - reducao_custos)
            resultado_final = resultado_bruto - despesas

            # Exibe os KPIs em colunas, como no Dashboard Geral
            st.subheader("Indicadores Principais do Período")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Receita Líquida", formatar_numero_br(receita_liquida))
            col2.metric("Custos", formatar_numero_br(custos - reducao_custos))
            col3.metric("Despesas", formatar_numero_br(despesas))
            col4.metric("Resultado Líquido", formatar_numero_br(resultado_final))
            
            st.divider()

            # Exibe os gráficos de composição
            col_graf1, col_graf2 = st.columns(2)
            
            with col_graf1:
                st.subheader("Maiores Fontes de Receita")
                df_receitas = df_filtrado[df_filtrado['Classificação DRE'] == 'Receita']
                if not df_receitas.empty:
                    receitas_por_operacao = df_receitas.groupby('Tipo de Operação')['Total do Item'].sum().nlargest(10)
                    st.bar_chart(receitas_por_operacao)
                else:
                    st.info("Nenhuma receita registrada no período filtrado.")

            with col_graf2:
                st.subheader("Maiores Despesas")
                df_despesas = df_filtrado[df_filtrado['Classificação DRE'] == 'Despesa']
                if not df_despesas.empty:
                    despesas_por_operacao = df_despesas.groupby('Tipo de Operação')['Total do Item'].sum().nlargest(10)
                    st.bar_chart(despesas_por_operacao)
                else:
                    st.info("Nenhuma despesa registrada no período filtrado.")

            # Expander para a visualização detalhada em texto
            with st.expander("Ver DRE Detalhado (Formato de Lista)"):
                st.subheader("Estrutura do Resultado")
                dcol1, dcol2 = st.columns([3, 1])
                dcol1.text("(=) Receita Operacional Bruta")
                dcol2.metric("", formatar_numero_br(receita))
                dcol1.text("(-) Deduções da Receita")
                dcol2.metric("", formatar_numero_br(deducoes))
                dcol1.markdown("**(=) Receita Operacional Líquida**")
                dcol2.metric("", f"**{formatar_numero_br(receita_liquida)}**")
                dcol1.text("(-) Custo (Mercadorias e Serviços)")
                dcol2.metric("", formatar_numero_br(custos - reducao_custos))
                dcol1.markdown("**(=) Resultado Bruto (Lucro Bruto)**")
                dcol2.metric("", f"**{formatar_numero_br(resultado_bruto)}**")
                dcol1.text("(-) Despesas Operacionais")
                dcol2.metric("", formatar_numero_br(despesas))
                st.divider()
                dcol1.markdown("### (=) Resultado Líquido do Período")
                dcol2.metric("", f"### {formatar_numero_br(resultado_final)}")

    with tabs[2]: # Entradas vs. Saídas
        st.header("Comparativo de Entradas vs. Saídas")
        movimentacao_diaria = df_filtrado.groupby([df_filtrado['Data Emissão'].dt.date, 'Movimentação'])['Total do Item'].sum().unstack(fill_value=0)
        st.bar_chart(movimentacao_diaria)
        st.dataframe(movimentacao_diaria,
            column_config={
                "Entrada": st.column_config.NumberColumn("Entrada", format="R$ %.2f"),
                "Saída": st.column_config.NumberColumn("Saída", format="R$ %.2f"),
                "Sem Movimentação": st.column_config.NumberColumn("Sem Movimentação", format="R$ %.2f")
            }
        )

    with tabs[3]: # Ranking de Produtos
        st.header("Ranking de Produtos Mais Vendidos")
        ranking_produtos = df_filtrado[df_filtrado['Movimentação'] == 'Saída'].groupby('Item Descrição').agg(
            Quantidade_Vendida=('Quantidade', 'sum'),
            Valor_Total_Vendido=('Total do Item', 'sum')
        ).sort_values(by='Valor_Total_Vendido', ascending=False).reset_index()
        st.dataframe(ranking_produtos, width='stretch',
            column_config={"Valor_Total_Vendido": st.column_config.NumberColumn("Valor Total Vendido", format="R$ %.2f")}
        )

    with tabs[4]: # Ranking Vendedores
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

    with tabs[5]: # Consulta Detalhada
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
                "Total da Nota": st.column_config.NumberColumn(format="R$ %.2f"),
            }
        )
    
    with tabs[6]: # Estoque Atual
        st.header("Consulta de Estoque de Inventário")
        if not df_estoque.empty:
            valor_total_estoque = df_estoque['Custo Total'].sum()
            num_itens_estoque = len(df_estoque)
            col1, col2 = st.columns(2)
            col1.metric("Itens Únicos em Estoque", f"{num_itens_estoque}")
            col2.metric("Valor Total do Estoque (Custo)", formatar_numero_br(valor_total_estoque))
            st.divider()
            
            item_estoque_pesquisado = st.text_input("Pesquisar por item no estoque:", key="pesquisa_estoque")
            df_estoque_filtrado = df_estoque
            if item_estoque_pesquisado:
                df_estoque_filtrado = df_estoque[df_estoque['Descrição'].str.contains(item_estoque_pesquisado, case=False, na=False)]
            
            st.dataframe(df_estoque_filtrado, width='stretch',
                column_config={
                    "Custo Unitário": st.column_config.NumberColumn("Custo Unitário", format="R$ %.2f"),
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


