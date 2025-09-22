# -----------------------------------------------------------------------------
# |                      SCRIPT DE TESTES PARA AUTOMAÇÃO (RPA)                |
# |                                                                           |
# | Use este arquivo para construir e testar sua sequência de automação       |
# | passo a passo.                                                            |
# -----------------------------------------------------------------------------

import pyautogui
import time
from datetime import date # Já vamos importar para testar as datas

print("--- INICIANDO TESTE DE AUTOMAÇÃO (RPA) ---")

# --- CONTAGEM REGRESSIVA ---
# Dando a você tempo para mudar para a tela do software de gestão.
print("Mude para a tela do seu software agora!")
for i in range(5, 0, -1):
    print(f"Iniciando em {i} segundos...")
    time.sleep(1)
print("Iniciando automação!")

try:
    # Define uma pausa padrão entre cada comando do pyautogui.
    # Aumente se o software for lento (ex: 1.5 ou 2.0).
    pyautogui.PAUSE = 1.0

    # =======================================================================
    # --- COLOQUE SEUS PASSOS DE AUTOMAÇÃO AQUI ---Z
    # Adicione seus comandos um por um e teste.
    
    # Pegando datas
    hoje = date.today()
    primeiro_dia_mes = hoje.replace(day=1)
    data_inicial = primeiro_dia_mes.strftime('%d%m%y')
    data_final = hoje.strftime('%d%m%y')
    
    print(f"Data inicial que seria digitada: {data_inicial}")
    print(f"Data final que seria digitada: {data_final}")
    
    # Abrir o software
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
    pyautogui.click(x=1478, y=24)
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
    pyautogui.click(x=1478, y=24)
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

    

    # ... continue adicionando seus passos aqui ...
    
    # =======================================================================

    print("\n--- SUCESSO! ---")
    print("A sequência de automação de teste foi concluída sem erros.")

except Exception as e:
    print(f"\n--- ERRO! ---")
    print(f"Ocorreu um erro durante a automação: {e}")