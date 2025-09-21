# -----------------------------------------------------------------------------
# |           AUTOMATIZADOR DE RELATÓRIOS (V4 - Refatorado para App)          |
# |                                                                           |
# | Descrição: Script ajustado para ser modular. A lógica principal foi       |
# |            encapsulada em uma função para ser chamada por outros scripts, |
# |            como a nossa futura interface em Streamlit.                    |
# -----------------------------------------------------------------------------

import pandas as pd
import openpyxl
from PyPDF2 import PdfReader
import pdfplumber
import re
import os
import glob
import pyautogui
import time
from datetime import date

# =================================================================================
# TODAS AS SUAS FUNÇÕES DE LÓGICA PERMANECEM AQUI (RPA, EXTRAÇÃO, ETC.)
# O conteúdo delas não muda.
# =================================================================================

def executar_rpa_extracao(pasta_destino):
    # ... (SEU CÓDIGO RPA COMPLETO VAI AQUI, SEM NENHUMA MUDANÇA)
    print("--- ETAPA 0: Iniciando Automação (RPA) para Extrair os PDFs ---")
    # --- CONTAGEM REGRESSIVA ---
    # Dando a você tempo para mudar para a tela do software de gestão.
    print("Mude para a tela do seu software agora!")
    for i in range(5, 0, -1):
        print(f"Iniciando em {i} segundos...")
        time.sleep(1)
    print("Iniciando automação!")
    
    try:
        # --- Lógica para obter as datas dinâmicas ---
        hoje = date.today()
        primeiro_dia_mes = hoje.replace(day=1)
        data_inicial = primeiro_dia_mes.strftime('%d%m%y')
        data_final = hoje.strftime('%d%m%y')
        
        print(f"Data inicial que seria digitada: {data_inicial}")
        print(f"Data final que seria digitada: {data_final}")
        # -------------------------------------------

        pyautogui.PAUSE = 1.0
        
        # Abrir o software
        pyautogui.click(x=1395, y=15) #minimiza o navegador
        pyautogui.doubleClick(x=34, y=432) 
        time.sleep(3) # Pausa longa para o programa abrir

        # Clicar no Login
        pyautogui.click(x=566, y=620) 
        pyautogui.write('Unique@nail2025', interval=0.1)
        pyautogui.press('enter')
        time.sleep(7)

        # Selecionar Estabelecimento
        pyautogui.click(x=740, y=610) 
        time.sleep(6) # Pausa longa para o programa abrir

        # Relatorios de entradas
        pyautogui.click(x=921, y=34) 
        pyautogui.click(x=1000, y=133) 
        pyautogui.click(x=1164, y=133) 
        pyautogui.click(x=962, y=186)
        time.sleep(4) # Pausa

        #Colocando a data e visualizando impressao
        pyautogui.click(x=558, y=287) # Clica no campo da data inicial
        pyautogui.write(data_inicial, interval=0.2)
        pyautogui.click(x=784, y=287) # Clica no campo da data final
        pyautogui.write(data_final, interval=0.2)
        pyautogui.press('enter')
        pyautogui.click(x=534, y=101)
        time.sleep(6) # Pausa

        #Salvando pdf
        pyautogui.click(x=559, y=35)
        time.sleep(2) # Pausa
        pyautogui.click(x=675, y=555)
        pyautogui.write('Entrada')
        pyautogui.press('enter')
        time.sleep(2) # Pausa
        pyautogui.click(x=809, y=468)
        time.sleep(5) # Pausa

        #Fechando janelas
        pyautogui.click(x=1395, y=15) #minimiza o navegador
        time.sleep(1) # Pausa
        pyautogui.click(x=1488, y=6)
        time.sleep(1) # Pausa
        pyautogui.click(x=1062, y=69)
        time.sleep(1) # Pausa

        # Relatorios de saidas
        pyautogui.click(x=942, y=32) 
        pyautogui.click(x=1067, y=137) 
        pyautogui.click(x=1182, y=157) 
        pyautogui.click(x=1008, y=163)
        time.sleep(4) # Pausa

        #Colocando a data e visualizando impressao
        pyautogui.click(x=558, y=287) # Clica no campo da data inicial
        pyautogui.write(data_inicial, interval=0.2)
        pyautogui.click(x=784, y=287) # Clica no campo da data final
        pyautogui.write(data_final, interval=0.2)
        pyautogui.press('enter')
        pyautogui.click(x=534, y=101)
        time.sleep(6) # Pausa

        #Salvando pdf
        pyautogui.click(x=559, y=35)
        time.sleep(2) # Pausa
        pyautogui.click(x=675, y=555)
        pyautogui.write('Saidas')
        pyautogui.press('enter')
        time.sleep(2) # Pausa
        pyautogui.click(x=809, y=468)
        time.sleep(30) # Pausa

        #Fechando janelas
        pyautogui.click(x=1395, y=15) #minimiza o navegador
        time.sleep(1) # Pausa
        pyautogui.click(x=1488, y=6)
        time.sleep(1) # Pausa
        pyautogui.click(x=1062, y=69)
        time.sleep(1) # Pausa

        # inventario
        pyautogui.click(x=949, y=34) 
        pyautogui.click(x=1061, y=111) 
        pyautogui.click(x=1177, y=110)
        time.sleep(3) # Pausa 

        #Colocando a data e visualizando impressao
        pyautogui.write(data_final, interval=0.2)
        pyautogui.click(x=589, y=289) # Clica no campo da data final
        pyautogui.write(data_final, interval=0.2)
        pyautogui.press('enter')
        pyautogui.click(x=559, y=154)
        time.sleep(1) # Pausa
        pyautogui.click(x=928, y=542)
        time.sleep(20) # Pausa

        #Salvando pdf
        pyautogui.click(x=562, y=34)
        time.sleep(2) # Pausa
        pyautogui.click(x=713, y=559)
        pyautogui.write('inventario')
        pyautogui.press('enter')
        time.sleep(2) # Pausa
        pyautogui.click(x=805, y=467)
        time.sleep(20) # Pausa

        #Volta para o Stream
        pyautogui.click(x=354, y=21) #vai para a aba do streamlit

        print("--- ETAPA 0: Automação Concluída com Sucesso! ---\n")
        return True

    except Exception as e:
        pyautogui.alert(f"Ocorreu um erro durante a automação RPA: {e}")
        return False
        
movimentacao_map = { "1-VENDA DE MERCADORIAS - COOPERADO": "Saída", "18-COMPRA PARA INDUSTRIALIZACAO": "Entrada", "20-TRANSFERENCIA DE MERCADORIA SAIDA": "Saída", "21-TRANSFERENCIA DE MERCADORIA ENTRADA": "Entrada", "317-TRANSP. PARA ARMAZENAGEM": "Sem Movimentação", "319-VENDA DE MERCADORIAS - NAO COOPERADO": "Saída", "320-REMESSA DE MERC. ENT. FUT - NAO COOPERADO": "Saída", "328-ARMAZEM - REMESSA PARA DEPOSITO PRODUTOR": "Entrada", "329-ARMAZEM - RETORNO SIMBOLICO MERC. DEPOSITADA": "Saída", "331-ARMAZEM - RETORNO REMESSA MERCADORIA DEPOSITADA": "Saída", "338-RECLASSIFICACAO SAIDA": "Saída", "339-RECLASSIFICACAO ENTRADA": "Entrada", "34-VENDA DE PRESTACAO DE SERVICOS": "Sem Movimentação", "341-VENDA PARA ENT. FUTURA - NAO COOPERADO": "Saída", "342-ARMAZEM - RETORNO SIMBOLICO QUEBRA TECNICA": "Saída", "365-ARMAZEM - REMESSA SIMB. PARA DEPOSITO COM COBRANÇA": "Entrada", "368-IND - VENDA DE PRODUTO INDUSTRIALIZADO - COOPERADO": "Saída", "369-IND - VENDA DE PRODUTO INDUSTRIALIZADO - NAO COOPERADO": "Saída", "370-IND - VENDA PARA ENT. FUTURA - COOPERADO": "Sem Movimentação", "372-IND - REMESSA DE MERC. ENT. FUT - COOPERADO": "Saída", "375-ARMAZEM - OUTRAS ENT. - ESTORNO RET. SIMB. MERC. DEPOSITADA": "Saída", "398-ARMAZEM - COMPRA COM NF DE PRODUTOR (ESTOQUE DISPONIVEL)": "Entrada", "4-VENDA PARA ENT. FUTURA - COOPERADO": "Sem Movimentação", "5-REMESSA DE MERC. ENT. FUT - COOPERADO": "Saída", "53-SAIDA DE MERCADORIA EM BONIFICACAO": "Saída", "58-ARMAZEM - REMESSA MERC. CONTA ORDEM TERCEIROS": "Saída", "28-COMPRA DE MATERIAL USO E CONSUMO": "Entrada", "418-AQUISIÇÃO DE SERVIÇOS - CONSULTORIA EMPRESARIAL": "Entrada", "73-ENTRADA TRANSF. USO E CONSUMO": "Entrada", "390-IND - DEVOLUCAO DE VENDA NF PROPRIA": "Entrada", "2-DEVOLUCAO DE VENDA NF PROPRIA": "Entrada", "417-AQUISIÇÃO DE SERVIÇOS - MANUT. MAQU. E EQUIPAMENTOS": "Entrada", "441-AQUISIÇÃO DE SERVIÇOS - RET. FEDERAIS": "Entrada", "6-CONTA MOVIMENTO": "Sem Movimentação", "1-À VISTA": "Sem Movimentação", "8-À VISTA ENTRADAS": "Sem Movimentação", "3-PAGAMENTO A PRAZO": "Sem Movimentação", }
def extrair_texto_pdf_movimentacao(caminho_arquivo_pdf):
    try:
        texto_completo = ""
        with open(caminho_arquivo_pdf, 'rb') as f:
            leitor = PdfReader(f)
            for pagina in leitor.pages:
                texto_completo += pagina.extract_text() or ""
        return texto_completo
    except Exception as e:
        print(f"  [ERRO] Não foi possível ler o arquivo '{os.path.basename(caminho_arquivo_pdf)}'. Erro: {e}")
        return ""
def analisar_relatorio_movimentacao(texto, nome_arquivo_origem):
    dados_finais = []
    padrao_bloco = r'((?:[\d-]+-?NFSE|[\d-]+)\s*Nota.*?)(?=(?:[\d-]+-?NFSE|[\d-]+)\s*Nota|Total do Dia|Total do Estabelecimento|T o t a l  G e r a l|$)'
    blocos = re.findall(padrao_bloco, texto, re.DOTALL)
    for bloco in blocos:
        padrao_nota_cliente = re.search(r'([\d-]+(?:-?NFSE)?)\s*Nota(.*?)\s*Cli-', bloco)
        padrao_operacao = re.search(r'Carga:(.*?)\n', bloco)
        padrao_cpf_cnpj = re.search(r'(CPF|CNPJ):\s*([\d\.\-\/]+)', bloco)
        padrao_cidade_data = re.search(r'Cidade:\s*(.*?)\s*UF:\s*(\w{2})Data Emissão:\s*(\d{2}/\d{2}/\d{4})', bloco)
        padrao_total_nota = re.search(r'Total da Nota\s+[\d.,]+\s+[\d.,]+\s+([\d.,]+)', bloco)
        padrao_representante = re.search(r'Repre\s*-\s*((?!Unid\.).*?)\n', bloco)
        padrao_pagamento_com_data = re.search(r'Forma Pagto.*?\n.*?\s(\d{2}/\d{2}/\d{4})\s+[\d-]+\s+\d+\s+([^\n]*)', bloco, re.DOTALL)
        padrao_pagamento_sem_valor = re.search(r'Forma Pagto.*?\n[\d.,\s]+(\d+\s+Sem valor comercial)', bloco, re.DOTALL)
        padrao_pagamento_a_vista = re.search(r'Forma Pagto.*?\n.*?\s(\d+\s+À vista.*)', bloco, re.DOTALL)
        padrao_pagamento_cartao = re.search(r'Forma Pagto.*?\n.*?\s(\d+\s+Cartão[^\n]*)', bloco, re.DOTALL)
        nota = padrao_nota_cliente.group(1).strip() if padrao_nota_cliente else 'N/A'
        cliente = padrao_nota_cliente.group(2).strip() if padrao_nota_cliente else 'N/A'
        tipo_operacao = padrao_operacao.group(1).strip() if padrao_operacao else 'N/A'
        cpf_cnpj = padrao_cpf_cnpj.group(2).strip() if padrao_cpf_cnpj else 'N/A'
        representante = padrao_representante.group(1).strip() if padrao_representante and padrao_representante.group(1).strip() else 'N/A'
        cidade, uf, data_emissao = ('N/A', 'N/A', 'N/A')
        if padrao_cidade_data: cidade, uf, data_emissao = [s.strip() for s in padrao_cidade_data.groups()]
        total_nota = padrao_total_nota.group(1).strip() if padrao_total_nota else 'N/A'
        forma_pagto, data_vencimento = ('N/A', 'N/A')
        if padrao_pagamento_com_data:
            data_vencimento = padrao_pagamento_com_data.group(1).strip()
            forma_pagto = padrao_pagamento_com_data.group(2).strip()
        elif padrao_pagamento_sem_valor: forma_pagto = padrao_pagamento_sem_valor.group(1).strip()
        elif padrao_pagamento_a_vista: forma_pagto = padrao_pagamento_a_vista.group(1).strip()
        elif padrao_pagamento_cartao: forma_pagto = padrao_pagamento_cartao.group(1).strip()
        if forma_pagto != 'N/A':
            if 'Emissão:' in forma_pagto: forma_pagto = forma_pagto.split('Emissão:')[0]
            if 'Entradas' in forma_pagto: forma_pagto = forma_pagto.split('Entradas')[0]
            forma_pagto = re.sub(r'^\d+\s*', '', forma_pagto).strip()
        padrao_itens = re.compile(r'(\d{7,}-.*?)\s+(KG|SC|UN|GL)\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s+(\d{4})\s+Item:\s+\d+\s+([\d.,]+)')
        itens_encontrados = padrao_itens.findall(bloco)
        if not itens_encontrados: continue
        for item in itens_encontrados:
            dados_item = {
                'Arquivo Origem': nome_arquivo_origem, 'Nota': nota, 'Tipo de Operação': tipo_operacao, 'Cliente': cliente,
                'CPF/CNPJ': cpf_cnpj, 'Representante': representante, 'Cidade': cidade, 'UF': uf, 'Data Emissão': data_emissao,
                'Item Descrição': item[0].strip(), 'Unidade': item[1], 'Valor Unitário': item[2], 'Total do Item': item[3],
                'Preço de Venda': item[4], 'CFOP': item[5], 'Peso Bruto': 'N/A', 'Quantidade': item[6],
                'Total da Nota': total_nota, 'Data Vencimento': data_vencimento, 'Forma de Pagto': forma_pagto
            }
            dados_finais.append(dados_item)
    return dados_finais
def orquestrar_extracao_movimentacoes(lista_arquivos_pdf):
    todos_os_dados = []
    print("--- ETAPA 1: Iniciando Extração das Movimentações (Entradas/Saídas) ---")
    for caminho_completo_pdf in lista_arquivos_pdf:
        nome_arquivo = os.path.basename(caminho_completo_pdf)
        print(f"  > Lendo arquivo: '{nome_arquivo}'")
        texto_extraido = extrair_texto_pdf_movimentacao(caminho_completo_pdf)
        if texto_extraido:
            dados_do_arquivo = analisar_relatorio_movimentacao(texto_extraido, nome_arquivo)
            if dados_do_arquivo:
                print(f"    -> {len(dados_do_arquivo)} registros encontrados.")
                todos_os_dados.extend(dados_do_arquivo)
            else:
                print("    -> Nenhum registro encontrado com os padrões atuais.")
    if not todos_os_dados:
        return None
    for item in todos_os_dados:
        item['Movimentação'] = movimentacao_map.get(item.get('Tipo de Operação', ''), 'Outros')
    print("--- ETAPA 1: Concluída com Sucesso! ---\n")
    return pd.DataFrame(todos_os_dados)
def processar_texto_inventario_para_tabela(texto):
    dados_processados = []
    linhas = texto.strip().split('\n')
    for numero_linha, linha in enumerate(linhas):
        linha_limpa = linha.strip()
        partes = linha_limpa.split()
        if len(partes) < 5 or not partes[0].isdigit(): continue
        try:
            custo_total = partes[-1]
            custo_unitario = partes[-2]
            saldo = partes[-3]
            unidade = partes[-4]
            codigo_item = partes[0]
            descricao = ' '.join(partes[1:-4])
            dados_processados.append([codigo_item, descricao, unidade, saldo, custo_unitario, custo_total])
        except IndexError:
            print(f"  -> Linha {numero_linha + 1} do inventário ignorada (formato inesperado): '{linha_limpa}'")
    return dados_processados
def orquestrar_extracao_inventario(caminho_pdf):
    print("--- ETAPA 2: Iniciando Extração do Inventário ---")
    if not os.path.exists(caminho_pdf):
        print(f"  [ERRO FATAL] O arquivo de inventário '{caminho_pdf}' não foi encontrado.")
        return None
    dados_completos = []
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            print(f"  > Lendo o arquivo: '{os.path.basename(caminho_pdf)}'...")
            for i, pagina in enumerate(pdf.pages):
                texto_da_pagina = pagina.extract_text(layout=True, x_tolerance=2)
                if texto_da_pagina:
                    dados_da_pagina = processar_texto_inventario_para_tabela(texto_da_pagina)
                    dados_completos.extend(dados_da_pagina)
        if not dados_completos:
            print("  -> Nenhum dado de inventário foi extraído.")
            return None
        cabecalhos = ['Item', 'Descrição', 'UN', 'Saldo', 'Custo Unit.', 'Custo Total']
        df_inventario = pd.DataFrame(dados_completos, columns=cabecalhos)
        print("--- ETAPA 2: Concluída com Sucesso! ---\n")
        return df_inventario
    except Exception as e:
        print(f"  [ERRO INESPERADO] Ocorreu um erro ao processar o PDF de inventário: {e}")
        return None

# =================================================================================
# NOVA ESTRUTURA MODULAR
# =================================================================================

def unir_dataframes(df_movimentacoes, df_inventario):
    """
    Recebe os DataFrames de movimentações e inventário, une as informações
    e retorna o DataFrame final consolidado.
    """
    print("--- ETAPA 3: Unindo Movimentações com Custos do Inventário ---")
    
    df_movimentacoes.columns = [col.strip().replace('.', '') for col in df_movimentacoes.columns]
    df_inventario.columns = [col.strip().replace('.', '') for col in df_inventario.columns]

    df_movimentacoes['DESCRICAO_LIMPA'] = df_movimentacoes['Item Descrição'].astype(str).str.replace(r'^\d+-\s*', '', regex=True)
    df_movimentacoes['DESCRICAO_LIMPA'] = df_movimentacoes['DESCRICAO_LIMPA'].str.strip().str.replace(r'\s+', ' ', regex=True)
    
    df_inventario['Descrição'] = df_inventario['Descrição'].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
    
    print("  > Colunas padronizadas para o cruzamento de dados.")
    
    df_final = pd.merge(
        df_movimentacoes,
        df_inventario[['Descrição', 'Custo Unit']],
        left_on='DESCRICAO_LIMPA',
        right_on='Descrição',
        how='left'
    )
    print("  > Cruzamento de dados ('merge') realizado.")

    df_final = df_final.rename(columns={'Custo Unit': 'Preço de Custo'})
    df_final = df_final.drop(columns=['DESCRICAO_LIMPA', 'Descrição'])
    
    print("--- ETAPA 3: Concluída com Sucesso! ---")
    return df_final

def executar_processo_completo(pasta_raiz_relatorios, palavra_chave_inventario):
    """
    Função principal que orquestra todo o processo de automação, desde a extração
    dos PDFs até a entrega do DataFrame final.
    """
    print("=====================================================")
    print("==        INICIANDO PROCESSO COMPLETO DE DADOS      ==")
    print("=====================================================\n")

    # ETAPA 0: Executar a automação RPA para extrair os PDFs do servidor
    sucesso_rpa = executar_rpa_extracao(pasta_raiz_relatorios)
    if not sucesso_rpa:
        # Lança um erro que pode ser capturado pelo Streamlit
        raise RuntimeError("A automação (RPA) para extração dos PDFs falhou.")

    # Busca de arquivos pós-RPA
    print(f"Buscando arquivos na pasta: '{pasta_raiz_relatorios}'...")
    padrao_busca_inventario = os.path.join(pasta_raiz_relatorios, f'*{palavra_chave_inventario}*.pdf')
    lista_inventario = glob.glob(padrao_busca_inventario)
    
    if len(lista_inventario) == 0:
        raise FileNotFoundError(f"Nenhum arquivo de inventário com a palavra '{palavra_chave_inventario}' foi encontrado.")
    if len(lista_inventario) > 1:
        raise FileNotFoundError(f"Mais de um arquivo de inventário com a palavra '{palavra_chave_inventario}' foi encontrado.")
        
    caminho_pdf_inventario = lista_inventario[0]
    print(f"  > Arquivo de inventário encontrado: '{os.path.basename(caminho_pdf_inventario)}'")

    todos_os_pdfs = glob.glob(os.path.join(pasta_raiz_relatorios, '*.pdf'))
    lista_pdfs_movimentacao = [pdf for pdf in todos_os_pdfs if pdf != caminho_pdf_inventario]
    
    if not lista_pdfs_movimentacao:
        raise FileNotFoundError("Nenhum arquivo de movimentação foi encontrado na pasta.")

    print(f"  > {len(lista_pdfs_movimentacao)} arquivo(s) de movimentação encontrados.")

    # ETAPAS 1, 2 e 3
    df_movs = orquestrar_extracao_movimentacoes(lista_pdfs_movimentacao)
    df_inv = orquestrar_extracao_inventario(caminho_pdf_inventario)
    
    if df_movs is None or df_inv is None:
        raise ValueError("Falha no processamento dos PDFs. Um dos DataFrames está vazio.")
        
    df_final = unir_dataframes(df_movs, df_inv)
    
    print("\n=====================================================")
    print("==        PROCESSO DE DADOS FINALIZADO COM SUCESSO    ==")
    print("=====================================================")
    
    return df_final

# Este bloco abaixo permite que o script ainda seja executado de forma independente
if __name__ == "__main__":
    # --- CONFIGURAÇÃO PARA EXECUÇÃO INDEPENDENTE ---
    PASTA_RAIZ_RELATORIOS = r'C:\Users\consultor.ale\Desktop\Mamede\Relatórios\MOVIMENTACOES'
    PALAVRA_CHAVE_INVENTARIO = 'inventario' # Ajuste se o nome do seu arquivo de inventário for diferente
    CAMINHO_EXCEL_FINAL = r'C:\Users\consultor.ale\Desktop\Mamede\Relatorio_Final_Standalone.xlsx'
    
    try:
        # Chama a função principal que faz todo o trabalho
        dataframe_resultado = executar_processo_completo(PASTA_RAIZ_RELATORIOS, PALAVRA_CHAVE_INVENTARIO)
        
        # Ação de salvar o arquivo, agora separada da lógica principal
        dataframe_resultado.to_excel(CAMINHO_EXCEL_FINAL, index=False)
        print(f"\nProcesso standalone concluído! Arquivo salvo em: '{CAMINHO_EXCEL_FINAL}'")
        
    except (RuntimeError, FileNotFoundError, ValueError) as e:
        print(f"\n--- ERRO NA EXECUÇÃO STANDALONE ---")
        print(e)