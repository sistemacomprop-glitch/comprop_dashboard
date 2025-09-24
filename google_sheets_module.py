# google_sheets_module.py (Versão Corrigida)
# Este módulo gerencia toda a interação com a API do Google Sheets.

import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe

def buscar_dados_existentes(nome_planilha, credenciais_json):
    """Conecta e busca todos os dados existentes na planilha, retornando um DataFrame."""
    try:
        print("--- LENDO PLANILHA EXISTENTE ---")
        gc = gspread.service_account(filename=credenciais_json)
        spreadsheet = gc.open(nome_planilha)
        worksheet = spreadsheet.sheet1
        df = get_as_dataframe(worksheet, evaluate_formulas=True)
        df.dropna(how='all', inplace=True)

        if not df.empty and 'Data Emissão' in df.columns:
            # --- CORREÇÃO AQUI: Força a leitura no formato Dia/Mês/Ano ---
            df['Data Emissão'] = pd.to_datetime(df['Data Emissão'], format='%d/%m/%Y', errors='coerce')
        
        print(f"  > Encontrados {len(df)} registros existentes.")
        return df
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"  > AVISO: A planilha '{nome_planilha}' não foi encontrada. Uma nova será criada/usada.")
        return pd.DataFrame()
    except Exception as e:
        print(f"  > ERRO ao buscar dados existentes: {e}.")
        return pd.DataFrame()

def atualizar_dados_no_google_sheets(df_novos, df_existentes, nome_planilha, credenciais_json):
    """Junta dados novos e existentes, remove duplicatas e atualiza a planilha."""
    try:
        print("\n--- ETAPA FINAL: Atualizando dados no Google Sheets ---")
        
        df_completo = pd.concat([df_existentes, df_novos], ignore_index=True)
        print(f"  > Total de registros antes da limpeza: {len(df_completo)}")

        colunas_chave = ['Nota', 'Data Emissão', 'Item Descrição', 'Quantidade', 'Total do Item']
        df_completo['Data Emissão'] = pd.to_datetime(df_completo['Data Emissão']).dt.date
        df_final = df_completo.drop_duplicates(subset=colunas_chave, keep='last')
        print(f"  > Total de registros após remover duplicatas: {len(df_final)}")
        
        df_final = df_final.sort_values(by="Data Emissão", ascending=True)

        gc = gspread.service_account(filename=credenciais_json)
        spreadsheet = gc.open(nome_planilha)
        worksheet = spreadsheet.sheet1
        
        print("  > Limpando a planilha para receber os dados atualizados...")
        worksheet.clear()
        
        print("  > Enviando dados atualizados e consolidados...")
        df_final['Data Emissão'] = pd.to_datetime(df_final['Data Emissão']).dt.strftime('%d/%m/%Y')
        set_with_dataframe(worksheet, df_final, include_index=False, include_column_header=True, resize=True)
        
        print("SUCESSO! Dados atualizados no Google Sheets.")
        return True
    except Exception as e:
        print(f"ERRO ao atualizar dados no Google Sheets: {e}")
        return False