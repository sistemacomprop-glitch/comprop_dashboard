# Mude para False para usar o arquivo Excel local
MODO_ONLINE = True 

# --- Caminhos e Nomes de Arquivos ---
PASTA_RAIZ_RELATORIOS = r'C:\Users\consultor.ale\Desktop\Mamede\Relatórios\MOVIMENTACOES'
PALAVRA_CHAVE_INVENTARIO = 'ppReport1inventario'
NOME_PLANILHA_ONLINE = "COMPROP_Dashboard_Data"
CAMINHO_CREDENCIAS_JSON = "credentials.json"
CAMINHO_EXCEL_LOCAL = r'C:\Users\consultor.ale\Desktop\Mamede\Relatórios\COMPROP_Dashboard_Data_Local.xlsx'
CAMINHO_LOGO = r'C:\Users\consultor.ale\Desktop\Mamede\image_9b00e0.png'

# --- Dicionário de Mapeamento de Movimentação ---

movimentacao_map = {
    # --- VENDAS / DEVOLUÇÕES (RECEITA) ---
    "1-VENDA DE MERCADORIAS - COOPERADO": "Saída",
    "319-VENDA DE MERCADORIAS - NAO COOPERADO": "Saída",
    "316-VENDA DE LEITE COOP": "Saída",
    "454-VENDA DE MERCADORIAS - COOPERADO - AGROTOXICO": "Saída",
    "455-VENDA DE MERCADORIAS - NAO COOPERADO - AGROTOXICO": "Saída",
    "5-REMESSA DE MERC. ENT. FUT - COOPERADO": "Saída",
    "320-REMESSA DE MERC. ENT. FUT - NAO COOPERADO": "Saída",
    "2-DEVOLUCAO DE VENDA NF PROPRIA": "Entrada",
    "3-DEVOLUCAO DE VENDA NF TERCEIROS": "Entrada",
    "6-DEVOLUCAO REMESSA DE ENTREGA FUTURA": "Entrada", # Corrigido typo "REMESSa"

    # --- COMPRAS / DEVOLUÇÕES (CUSTO) ---
    "321-COMPRA PARA COMERCIALIZACAO": "Entrada",
    "314-COMPRA DE LEITE": "Entrada",
    "16-COMPLEMENTO DE PRECO DE COMPRA": "Sem Movimentação",
    "19-DEVOLUCAO DE COMPRA": "Saída",
    
    # --- USO E CONSUMO / DESPESAS ---
    "28-COMPRA DE MATERIAL USO E CONSUMO": "Entrada",
    "29-SAIDA MERCADORIA USO E CONSUMO PROPRIO": "Saída",
    "31-COMPRA DE COMBUSTIVEL": "Entrada",
    "418-AQUISIÇÃO DE SERVIÇOS - CONSULTORIA EMPRESARIAL": "Sem Movimentação",
    "441-AQUISIÇÃO DE SERVIÇOS - RET. FEDERAIS": "Sem Movimentação",
    "53-SAIDA DE MERCADORIA EM BONIFICACAO": "Saída",
    "72-SAIDA TRANSF. USO E CONSUMO": "Saída",
    
    # --- MOVIMENTAÇÕES NEUTRAS (TRANSFERÊNCIA, AJUSTE, CONSIGNAÇÃO) ---
    "20-TRANSFERENCIA DE MERCADORIA SAIDA": "Saída",
    "21-TRANSFERENCIA DE MERCADORIA ENTRADA": "Entrada",
    "315-RECEBIMENTO DE LEITE": "Entrada", # Efeito neutro no DRE, mas é entrada física
    "4-VENDA PARA ENT. FUTURA - COOPERADO": "Sem Movimentação",
    "341-VENDA PARA ENT. FUTURA - NAO COOPERADO": "Sem Movimentação",
    "421-AJUSTE LOTE (SAIDA MATRIZ)": "Sem Movimentação",
    "422-AJUSTE LOTE (ENTRADA MATRIZ)": "Sem Movimentação",
    "324-ENT. MERC. REC. EM CONSIG": "Entrada", # Efeito neutro no DRE, mas é entrada física
    "52-ENTRADA DE MERCADORIA EM BONIFICACAO": "Entrada", # Efeito neutro no DRE, mas é entrada física
    "57-ENTRADA MERCADORIA CONTA ORDEM TERCEIROS": "Entrada", # Efeito neutro no DRE, mas é entrada física
    "327-DEVOLUCAO SIMB. RECEB. EM CONSIG.": "Saída",

    # --- ENTRADAS E SAÍDAS NÃO MAPEADAS ANTERIORMENTE (Mantidas por segurança) ---
    "18-COMPRA PARA INDUSTRIALIZACAO": "Entrada",
    "317-TRANSP. PARA ARMAZENAGEM": "Sem Movimentação",
    "328-ARMAZEM - REMESSA PARA DEPOSITO PRODUTOR": "Entrada",
    "331-ARMAZEM - RETORNO REMESSA MERCADORIA DEPOSITADA": "Saída",
    "338-RECLASSIFICACAO SAIDA": "Saída",
    "339-RECLASSIFICACAO ENTRADA": "Entrada",
    "34-VENDA DE PRESTACAO DE SERVICOS": "Sem Movimentação",
    "365-ARMAZEM - REMESSA SIMB. PARA DEPOSITO COM COBRANÇA": "Entrada",
    "368-IND - VENDA DE PRODUTO INDUSTRIALIZADO - COOPERADO": "Saída",
    "369-IND - VENDA DE PRODUTO INDUSTRIALIZADO - NAO COOPERADO": "Saída",
    "370-IND - VENDA PARA ENT. FUTURA - COOPERADO": "Sem Movimentação",
    "372-IND - REMESSA DE MERC. ENT. FUT - COOPERADO": "Saída",
    "375-ARMAZEM - OUTRAS ENT. - ESTORNO RET. SIMB. MERC. DEPOSITADA": "Saída",
    "398-ARMAZEM - COMPRA COM NF DE PRODUTOR (ESTOQUE DISPONIVEL)": "Entrada",
    "58-ARMAZEM - REMESSA MERC. CONTA ORDEM TERCEIROS": "Saída",
    "73-ENTRADA TRANSF. USO E CONSUMO": "Entrada",
    "390-IND - DEVOLUCAO DE VENDA NF PROPRIA": "Entrada",
    "417-AQUISIÇÃO DE SERVIÇOS - MANUT. MAQU. E EQUIPAMENTOS": "Entrada",
    "6-CONTA MOVIMENTO": "Sem Movimentação",
    "1-À VISTA": "Sem Movimentação",
    "8-À VISTA ENTRADAS": "Sem Movimentação",
    "3-PAGAMENTO A PRAZO": "Sem Movimentação",
}

dre_map = {
    # --- RECEITAS ---
    "1-VENDA DE MERCADORIAS - COOPERADO": "Receita",
    "319-VENDA DE MERCADORIAS - NAO COOPERADO": "Receita",
    "316-VENDA DE LEITE COOP": "Receita",
    "454-VENDA DE MERCADORIAS - COOPERADO - AGROTOXICO": "Receita",
    "455-VENDA DE MERCADORIAS - NAO COOPERADO - AGROTOXICO": "Receita",
    "5-REMESSA DE MERC. ENT. FUT - COOPERADO": "Receita",
    "320-REMESSA DE MERC. ENT. FUT - NAO COOPERADO": "Receita",

    # --- DEDUÇÕES DE RECEITA ---
    "2-DEVOLUCAO DE VENDA NF PROPRIA": "Despesa",
    "3-DEVOLUCAO DE VENDA NF TERCEIROS": "Despesa",
    "6-DEVOLUCAO REMESSA DE ENTREGA FUTURA": "Despesa",

    # --- CUSTOS ---
    "321-COMPRA PARA COMERCIALIZACAO": "Despesa",
    "314-COMPRA DE LEITE": "Despesa",
    "16-COMPLEMENTO DE PRECO DE COMPRA": "Despesa",
    "19-DEVOLUCAO DE COMPRA": "Receita",

    # --- DESPESAS ---
    "28-COMPRA DE MATERIAL USO E CONSUMO": "Despesa",
    "29-SAIDA MERCADORIA USO E CONSUMO PROPRIO": "Despesa",
    "31-COMPRA DE COMBUSTIVEL": "Despesa",
    "418-AQUISIÇÃO DE SERVIÇOS - CONSULTORIA EMPRESARIAL": "Despesa",
    "441-AQUISIÇÃO DE SERVIÇOS - RET. FEDERAIS": "Despesa",
    "53-SAIDA DE MERCADORIA EM BONIFICACAO": "Despesa",
    "72-SAIDA TRANSF. USO E CONSUMO": "Despesa",

    # --- NEUTRO / NÃO AFETA O DRE DIRETAMENTE ---
    "20-TRANSFERENCIA DE MERCADORIA SAIDA": "Neutro",
    "21-TRANSFERENCIA DE MERCADORIA ENTRADA": "Neutro",
    "315-RECEBIMENTO DE LEITE": "Neutro",
    "4-VENDA PARA ENT. FUTURA - COOPERADO": "Neutro",
    "341-VENDA PARA ENT. FUTURA - NAO COOPERADO": "Neutro",
    "421-AJUSTE LOTE (SAIDA MATRIZ)": "Neutro",
    "422-AJUSTE LOTE (ENTRADA MATRIZ)": "Neutro",
    "324-ENT. MERC. REC. EM CONSIG": "Neutro",
    "52-ENTRADA DE MERCADORIA EM BONIFICACAO": "Neutro",
    "57-ENTRADA MERCADORIA CONTA ORDEM TERCEIROS": "Neutro",
    "327-DEVOLUCAO SIMB. RECEB. EM CONSIG.": "Neutro",
}