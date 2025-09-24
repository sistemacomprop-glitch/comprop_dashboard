# data_processor_module.py
# Este módulo é responsável por receber os DataFrames brutos e realizar
# a limpeza, união (merge) e cálculos finais.

import pandas as pd

def unir_dataframes(df_movimentacoes, df_inventario):
    """
    Recebe os DataFrames, une as informações, calcula o Custo Total e
    reorganiza as colunas para o layout final.
    """
    print("--- ETAPA 3: Unindo, Calculando e Reorganizando ---")
    
    df_movimentacoes.columns = [col.strip().replace('.', '') for col in df_movimentacoes.columns]
    df_inventario.columns = [col.strip().replace('.', '') for col in df_inventario.columns]
    df_movimentacoes['DESCRICAO_LIMPA'] = df_movimentacoes['Item Descrição'].astype(str).str.replace(r'^\d+-\s*', '', regex=True).str.strip().str.replace(r'\s+', ' ', regex=True)
    df_inventario['Descrição'] = df_inventario['Descrição'].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
    
    df_final = pd.merge(
        df_movimentacoes,
        df_inventario[['Descrição', 'Custo Unit']],
        left_on='DESCRICAO_LIMPA',
        right_on='Descrição',
        how='left'
    )
    df_final = df_final.rename(columns={'Custo Unit': 'Preço de Custo'})
    
    # Bloco de limpeza e conversão de colunas numéricas
    print("  > Limpando e convertendo colunas de valores...")
    colunas_de_valores = ['Preço de Custo', 'Quantidade', 'Valor Unitário', 'Total do Item', 'Preço de Venda']
    
    for col in colunas_de_valores:
        if col in df_final.columns:
            df_final[col] = df_final[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0)

    # Cálculo do Custo Total
    print("  > Calculando o Custo Total...")
    df_final['Custo Total'] = df_final['Preço de Custo'] * df_final['Quantidade']

    # Define a ordem final e exata das colunas
    print("  > Reorganizando as colunas...")
    ordem_final_colunas = [
        'Movimentação', 'Nota', 'Data Emissão', 'Tipo de Operação', 'Cliente', 
        'CPF/CNPJ', 'Representante', 'Cidade', 'UF', 'Item Descrição', 'Unidade', 
        'Quantidade', 'Valor Unitário', 'Total do Item', 'Preço de Venda', 
        'Preço de Custo', 'Custo Total', 'CFOP', 'Total da Nota', 
        'Data de Vencimento', # --- CORREÇÃO AQUI ---
        'Forma de Pagto', 'Arquivo Origem'
    ]
    
    # Adiciona colunas que possam faltar (caso um PDF não gere alguma) para evitar erros
    for col in ordem_final_colunas:
        if col not in df_final.columns:
            df_final[col] = None

    df_final = df_final[ordem_final_colunas]
    
    print("--- ETAPA 3: Concluída com Sucesso! ---")
    return df_final