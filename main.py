# main.py (Versão 7.1 - Salvando múltiplas abas no Excel)

import os
import glob
from datetime import date, timedelta
import pandas as pd

from config import *
from rpa_module import executar_rpa_extracao
from pdf_parser_module import orquestrar_extracao_movimentacoes, orquestrar_extracao_inventario
from data_processor_module import unir_dataframes
from google_sheets_module import buscar_dados_existentes, atualizar_dados_no_google_sheets

MODO_ONLINE = False

def executar_processo_de_dados(pasta_raiz_relatorios, palavra_chave_inventario):
    """
    Processa os PDFs e retorna DOIS DataFrames: o de movimentações final
    e o de inventário bruto.
    """
    print(f"\n--- INICIANDO PROCESSAMENTO DE DADOS DOS PDFs ---")
    print(f"Buscando arquivos na pasta: '{pasta_raiz_relatorios}'...")
    
    padrao_busca_inventario = os.path.join(pasta_raiz_relatorios, f'*{palavra_chave_inventario}*.pdf')
    lista_inventario = glob.glob(padrao_busca_inventario)
    
    if not lista_inventario:
        raise FileNotFoundError(f"Nenhum arquivo de inventário com a palavra '{palavra_chave_inventario}' foi encontrado.")
        
    caminho_pdf_inventario = lista_inventario[0]
    print(f"  > Arquivo de inventário encontrado: '{os.path.basename(caminho_pdf_inventario)}'")

    todos_os_pdfs = glob.glob(os.path.join(pasta_raiz_relatorios, '*.pdf'))
    lista_pdfs_movimentacao = [pdf for pdf in todos_os_pdfs if pdf != caminho_pdf_inventario]
    
    if not lista_pdfs_movimentacao:
        raise FileNotFoundError("Nenhum arquivo de movimentação foi encontrado na pasta.")

    print(f"  > {len(lista_pdfs_movimentacao)} arquivo(s) de movimentação encontrados.")

    df_movs = orquestrar_extracao_movimentacoes(lista_pdfs_movimentacao)
    df_inv = orquestrar_extracao_inventario(caminho_pdf_inventario)
    
    if df_movs is None or df_inv is None:
        raise ValueError("Falha no processamento dos PDFs. Um dos DataFrames está vazio.")
        
    df_final = unir_dataframes(df_movs, df_inv)
    
    # MUDANÇA: Retorna os dois dataframes
    return df_final, df_inv


if __name__ == "__main__":
    if MODO_ONLINE:
        # --- LÓGICA DO MODO ONLINE (INCREMENTAL) ---
        print("Executando em MODO ONLINE...")
        try:
            df_existentes = buscar_dados_existentes(NOME_PLANILHA_ONLINE, CAMINHO_CREDENCIAS_JSON)
            hoje = date.today()
            if not df_existentes.empty and not df_existentes['Data Emissão'].dropna().empty:
                ultima_data = df_existentes['Data Emissão'].dropna().max().date()
                data_inicio_extracao = ultima_data
            else:
                data_inicio_extracao = hoje.replace(day=1)
            data_fim_extracao = hoje

            data_inicial_rpa_str = data_inicio_extracao.strftime('%d%m%y')
            data_final_rpa_str = data_fim_extracao.strftime('%d%m%y')

            sucesso_rpa = executar_rpa_extracao(PASTA_RAIZ_RELATORIOS, data_inicial_rpa_str, data_final_rpa_str)
            if not sucesso_rpa:
                raise RuntimeError("A automação (RPA) falhou.")

            novos_dados_df = executar_processo_de_dados(PASTA_RAIZ_RELATORIOS, PALAVRA_CHAVE_INVENTARIO)
            if novos_dados_df is not None and not novos_dados_df.empty:
                atualizar_dados_no_google_sheets(novos_dados_df, df_existentes, NOME_PLANILHA_ONLINE, CAMINHO_CREDENCIAS_JSON)
            else:
                print("Nenhum dado novo foi encontrado para adicionar à planilha.")
        except Exception as e:
            print(f"\n--- ERRO NA EXECUÇÃO ONLINE ---")
            print(e)
    else:
        # LÓGICA DO MODO LOCAL (SOBRESCRITA)
        print("Executando em MODO LOCAL...")
        try:
            hoje = date.today()
            primeiro_dia_mes = hoje.replace(day=1)
            data_inicial_rpa_str = primeiro_dia_mes.strftime('%d%m%y')
            data_final_rpa_str = hoje.strftime('%d%m%y')

            sucesso_rpa = executar_rpa_extracao(PASTA_RAIZ_RELATORIOS, data_inicial_rpa_str, data_final_rpa_str)
            if not sucesso_rpa:
                raise RuntimeError("A automação (RPA) falhou.")

            # MUDANÇA: Recebe os dois dataframes
            df_movimentacoes_final, df_inventario_bruto = executar_processo_de_dados(PASTA_RAIZ_RELATORIOS, PALAVRA_CHAVE_INVENTARIO)
            
            if df_movimentacoes_final is not None and not df_movimentacoes_final.empty:
                print(f"\n--- MODO LOCAL: Salvando resultado com 2 abas em '{CAMINHO_EXCEL_LOCAL}' ---")
                
                # MUDANÇA: Usa o ExcelWriter para salvar múltiplas abas
                with pd.ExcelWriter(CAMINHO_EXCEL_LOCAL, engine='openpyxl') as writer:
                    df_movimentacoes_final.to_excel(writer, sheet_name='Movimentacoes', index=False)
                    df_inventario_bruto.to_excel(writer, sheet_name='Estoque', index=False)

                print("SUCESSO! Arquivo Excel local com abas 'Movimentacoes' e 'Estoque' foi gerado.")
            else:
                print("Nenhum dado foi gerado para salvar.")
        except Exception as e:
            print(f"\n--- ERRO NA EXECUÇÃO LOCAL ---")
            print(e)