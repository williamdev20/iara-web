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

df = pd.read_csv(dataset)
df['landmarks_list'] = df['landmarks'].apply(json.loads)

def ancora(lista):
    ancoras = lista[0]
    return [[v[i] - ancoras[i] for i in range(3)] for v in lista]

def zoom(lista):
    s = math.sqrt(sum([v[i] * v[i] for v in lista for i in range(3)]))
    if s == 0: return lista
    return [[v[i] / s for i in range(3)] for v in lista]

def normalizar(lista):
    return zoom(ancora(lista))

def prever_sinal(pontos):
    if pontos is None:
        return "Desconhecido", 0.0

    p1 = np.array(pontos)
    distancias = []

    for i in range(len(df)):
        p2 = np.array(df['landmarks_list'][i])
        d = np.linalg.norm(p1 - p2)
        distancias.append((df['label'][i], d))

    distancias.sort(key=lambda x: x[1])

    k = 3
    vizinhos = distancias[:k]
    labels = [v[0] for v in vizinhos]
    mais_comum = Counter(labels).most_common(1)[0][0]
    media = sum([v[1] for v in vizinhos]) / k

    if media > 0.7:
        return "Desconhecido", 0.0

    confianca = 1 / (1 + media)
    return mais_comum, confianca


def processar_frame(image):
    """
    Recebe um frame BGR (OpenCV) e retorna (sinal, confiança)
    """
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    if not results.multi_hand_landmarks:
        return "Desconhecido", 0.0

    for hand in results.multi_hand_landmarks:
        lista = [(lm.x, lm.y, lm.z) for lm in hand.landmark]
        lista_norm = normalizar(lista)
        return prever_sinal(lista_norm)

    return "Desconhecido", 0.0