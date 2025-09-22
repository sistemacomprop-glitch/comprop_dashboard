# descobrir_coordenadas.py
import pyautogui
import time

print("O programa vai informar a posição do mouse em 5 segundos.")
print("Posicione o cursor sobre o local desejado...")
time.sleep(8)

posicao = pyautogui.position()
print(f"A posição do mouse é: {posicao}")
print("Anote os valores de X e Y.")