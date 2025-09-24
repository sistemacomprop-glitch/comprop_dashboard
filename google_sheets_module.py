# google_sheets_module.py - Versão 2.2 (Correção de erro <Response [200]>)
# Este módulo gerencia toda a interação com a API do Google Sheets.

import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe

def buscar_dados_existentes(nome_planilha, credenciais_json):
    """
    Conecta e busca dados das abas 'Movimentacoes' e 'Estoque',
    retornando sempre dois DataFrames.
    """
    try:
        print("--- LENDO PLANILHA EXISTENTE ---")
        gc = gspread.service_account(filename=credenciais_json)
        spreadsheet = gc.open(nome_planilha)
        
        try:
            mov_sheet = spreadsheet.worksheet('Movimentacoes')
            df_mov = get_as_dataframe(mov_sheet, evaluate_formulas=True)
            df_mov.dropna(how='all', inplace=True)
            if 'Data Emissão' in df_mov.columns:
                df_mov['Data Emissão'] = pd.to_datetime(df_mov['Data Emissão'], format='%d/%m/%Y', errors='coerce')
        except gspread.exceptions.WorksheetNotFound:
            print("  > Aba 'Movimentacoes' não encontrada. Assumindo como vazia.")
            df_mov = pd.DataFrame()

        try:
            est_sheet = spreadsheet.worksheet('Estoque')
            df_est = get_as_dataframe(est_sheet, evaluate_formulas=True)
            df_est.dropna(how='all', inplace=True)
        except gspread.exceptions.WorksheetNotFound:
            print("  > Aba 'Estoque' não encontrada. Assumindo como vazia.")
            df_est = pd.DataFrame()

        print(f"  > Encontrados {len(df_mov)} registros de movimentação e {len(df_est)} de estoque.")
        return df_mov, df_est

    except gspread.exceptions.SpreadsheetNotFound:
        print(f"  > AVISO: A planilha '{nome_planilha}' não foi encontrada. Assumindo dados vazios.")
        return pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        print(f"  > ERRO ao buscar dados existentes: {e}.")
        return pd.DataFrame(), pd.DataFrame()

def atualizar_dados_no_google_sheets(df_mov_novos, df_mov_existentes, df_est_novo, nome_planilha, credenciais_json):
    """Junta dados, remove duplicatas e atualiza as abas 'Movimentacoes' e 'Estoque'."""
    try:
        print("\n--- ETAPA FINAL: Atualizando dados no Google Sheets ---")
        
        # --- Processa as Movimentações ---
        df_completo = pd.concat([df_mov_existentes, df_mov_novos], ignore_index=True)
        print(f"  > Total de registros antes da limpeza: {len(df_completo)}")

        colunas_chave = ['Nota', 'Data Emissão', 'Item Descrição', 'Quantidade', 'Total do Item']
        df_completo['Data Emissão'] = pd.to_datetime(df_completo['Data Emissão'], format='%d/%m/%Y', errors='coerce')
        df_completo['Data Emissão'] = df_completo['Data Emissão'].dt.date
        df_final = df_completo.drop_duplicates(subset=colunas_chave, keep='last')
        print(f"  > Total de registros após remover duplicatas: {len(df_final)}")
        
        df_final = df_final.sort_values(by="Data Emissão", ascending=True)

        df_est_final = df_est_novo

        # --- Salva na Planilha ---
        gc = gspread.service_account(filename=credenciais_json)
        spreadsheet = gc.open(nome_planilha)
        
        # --- ATUALIZA ABA MOVIMENTAÇÕES ---
        try:
            mov_sheet = spreadsheet.worksheet('Movimentacoes')
        except gspread.exceptions.WorksheetNotFound:
            mov_sheet = spreadsheet.add_worksheet(title="Movimentacoes", rows="1", cols="1")
        
        mov_sheet.clear()
        
        # --- CORREÇÃO AQUI: Converte tudo para string antes de enviar ---
        df_mov_para_envio = df_final.copy()
        df_mov_para_envio['Data Emissão'] = pd.to_datetime(df_mov_para_envio['Data Emissão']).dt.strftime('%d/%m/%Y')
        # Converte o resto para string, tratando valores vazios (None/NaN) como strings vazias
        df_mov_para_envio = df_mov_para_envio.astype(object).where(pd.notnull(df_mov_para_envio), "")

        set_with_dataframe(mov_sheet, df_mov_para_envio, include_index=False, include_column_header=True, resize=True)
        print(f"  > Aba 'Movimentacoes' atualizada com {len(df_final)} registros.")

        # --- ATUALIZA ABA ESTOQUE ---
        try:
            est_sheet = spreadsheet.worksheet('Estoque')
        except gspread.exceptions.WorksheetNotFound:
            est_sheet = spreadsheet.add_worksheet(title="Estoque", rows="1", cols="1")
        
        est_sheet.clear()
        df_est_para_envio = df_est_final.astype(object).where(pd.notnull(df_est_final), "")
        set_with_dataframe(est_sheet, df_est_para_envio, include_index=False, include_column_header=True, resize=True)
        print(f"  > Aba 'Estoque' atualizada com {len(df_est_final)} registros.")

        print("SUCESSO! Dados atualizados no Google Sheets.")
        return True
    except Exception as e:
        print(f"ERRO ao atualizar dados no Google Sheets: {e}")
        return False