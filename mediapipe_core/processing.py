import cv2
import mediapipe as mp
import pandas as pd
import math
import json
import os
from collections import Counter
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dataset = os.path.join(BASE_DIR, "data", "dataset.csv")

# --- Configurações do MediaPipe ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils

if not os.path.exists(dataset):
    print(f"ERRO: O arquivo '{dataset}' não foi encontrado.")
    exit()

print("Carregando dataset...")
df = pd.read_csv(dataset)

df['landmarks_list'] = df['landmarks'].apply(json.loads)
print(f"Pronto! {len(df)} sinais carregados na memória.")


"""
 --- Funções relacionadas a calculos ---
 Ancora e Zoom - Tecnicas de Visão Computacional pra "normalizar" as imagens
 prever_sinal - Realiza o calculo de distancia euclidiana (Um pitagoras gigante bem dizer)
 O prever_sinal utiliza do metodo np.linalg.norm ou seja um metodo que calcula a "distancia euclidiana" de forma resumida.
"""
def ancora(lista: list) -> list:
    """Move a mão para que o punho seja o ponto (0,0,0)"""
    ancoras = lista[0]
    limpa = []
    for v in lista:
        l = []
        for i in range(3):
            l.append(v[i] - ancoras[i])
        limpa.append(l)
    return limpa

def zoom(lista: list) -> list:
    """Normaliza o tamanho da mão"""
    s = []
    limpa = []
    for v in lista:
        for i in range(3):
            s.append(v[i] * v[i])
    s = math.sqrt(sum(s))
    
    if s == 0: return lista 
    
    for v in lista:
        l = []
        for i in range(3):
            l.append(v[i] / s)
        limpa.append(l)
    return limpa

def realizar_calculos(lista: list) -> list:
    lista_ancora = ancora(lista)
    lista_zoom = zoom(lista_ancora)
    return lista_zoom

def prever_sinal(pontos_capturados):
    """Compara os pontos capturados com o dataset e retorna a previsão"""
    if pontos_capturados is None:
        return "Desconhecido", 0.0

    resultados = []
    p1 = np.array(pontos_capturados)
    
    for i in range(len(df)):
        p2 = np.array(df['landmarks_list'][i])
        
        distancia_final = np.linalg.norm(p1 - p2)
        resultados.append({'LABEL': df['label'][i], 'DIFFERENCE': distancia_final})

    resultados.sort(key=lambda x: x['DIFFERENCE'])
    
    k = 3
    vizinhos = resultados[:k]
    
    labels = [v['LABEL'] for v in vizinhos]
    contagem = Counter(labels)
    previsao = contagem.most_common(1)[0][0]
    
    media_dif = sum([v['DIFFERENCE'] for v in vizinhos]) / k
    
    if media_dif <= 0.7:
        confianca = 1 / (1 + media_dif) 
        return previsao, confianca
    else:
        return "Desconhecido", 0.0

"""
 --- Teste dos sinais ---
 Apenas um teste não vai pro codigo final.
"""
cap = cv2.VideoCapture(0)

print("Iniciando câmera... Pressione 'q' para sair.")

while cap.isOpened():
    sucesso, imagem = cap.read()
    if not sucesso:
        print("Ignorando frame vazio.")
        continue

    imagem = cv2.flip(imagem, 1)
    
    imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
    
    resultados_mp = hands.process(imagem_rgb)
    
    predicao = ""
    confianca = 0.0

    if resultados_mp.multi_hand_landmarks and resultados_mp.multi_handedness:
        for hand_landmarks, handedness in zip(resultados_mp.multi_hand_landmarks, resultados_mp.multi_handedness):
            
            mp_drawing.draw_landmarks(
                imagem,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=3, circle_radius=5),
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=3)
            )

            lista_bruta = hand_landmarks.landmark
            lista_calculo = []
            
            label_mao = handedness.classification[0].label 

            # Espelha sempre pra mão direita
            if label_mao == 'Left':
                for lm in lista_bruta:
                    lista_calculo.append((1.0 - lm.x, lm.y, lm.z))
            else:
                for lm in lista_bruta:
                    lista_calculo.append((lm.x, lm.y, lm.z))

            # Normaliza
            pontos_normalizados = realizar_calculos(lista_calculo)

            # Faz a previsão
            predicao, confianca = prever_sinal(pontos_normalizados)

            # Escolhe a cor do texto
            cor_texto = (0, 255, 0) if predicao != "Desconhecido" else (0, 0, 255)

            cv2.putText(imagem, f"Sinal: {predicao}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, cor_texto, 2, cv2.LINE_AA)

            cv2.putText(imagem, f"{confianca:.0%}", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.imshow('Reconhecimento de Sinais', imagem)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()