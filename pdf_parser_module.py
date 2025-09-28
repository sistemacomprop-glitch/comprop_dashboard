# pdf_parser_module.py (Versão anterior com extração baseada em 'Carga:')

import pandas as pd
from PyPDF2 import PdfReader
import pdfplumber
import re
import os
from config import movimentacao_map

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
        # A regra de extração antiga e menos confiável
        padrao_operacao = re.search(r'Carga:(.*?)\n', bloco)
        
        padrao_nota_cliente = re.search(r'([\d-]+(?:-?NFSE)?)\s*Nota(.*?)\s*Cli-', bloco)
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
        
        padrao_itens = re.compile(r'(\d{7,}-.*?)\s+([A-Z]{2,4})\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)\s+(\d{4})\s+Item:\s+\d+\s+([\d.,]+)')
        
        itens_encontrados = padrao_itens.findall(bloco)
        if not itens_encontrados: continue
        for item in itens_encontrados:
            dados_item = {
                'Arquivo Origem': nome_arquivo_origem, 'Nota': nota, 'Tipo de Operação': tipo_operacao, 'Cliente': cliente,
                'CPF/CNPJ': cpf_cnpj, 'Representante': representante, 'Cidade': cidade, 'UF': uf, 
                'Data Emissão': data_emissao,
                'Item Descrição': item[0].strip(), 'Unidade': item[1], 'Valor Unitário': item[2], 
                'Total do Item': item[3], 'Preço de Venda': item[4], 'CFOP': item[5], 
                'Quantidade': item[6], 'Total da Nota': total_nota, 
                'Data de Vencimento': data_vencimento, 'Forma de Pagto': forma_pagto
            }
            dados_finais.append(dados_item)
    return dados_finais

def orquestrar_extracao_movimentacoes(lista_arquivos_pdf):
    todos_os_dados = []
    print("--- ETAPA 1: Iniciando Extração das Movimentações (Entradas/Saídas) ---")
    for caminho_completo_pdf in lista_arquivos_pdf:
        nome_arquivo = os.path.basename(caminho_completo_pdf)
        print(f"  > Lendo arquivo: '{nome_arquivo}'...")
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
        item['Movimentação'] = movimentacao_map.get(item.get('Tipo de Operação'), 'Outros')
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