import os
import logging
import cv2
import mediapipe as mp
import pandas as pd
import math
import json
from collections import Counter
import numpy as np

# Isso serve pra remover os warnings do tensorflow

# Esconde os warnings do Tensorflow (menores que o nível "3")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# Mostrar apenas erros um mais graves que o nível "2"
os.environ['GLOG_minloglevel'] = '2'
# Colocar apenas os ERROS GRAVES do Mediapipe
logging.getLogger('mediapipe').setLevel(logging.ERROR)
# Colocar apenas os ERROS GRAVES do Tensorflow
logging.getLogger('tensorflow').setLevel(logging.ERROR)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dataset = os.path.join(BASE_DIR, "data", "dataset.csv")

# Carregar dataset
df = pd.read_csv(dataset)
df['landmarks_list'] = df['landmarks'].apply(json.loads)

print(f"Dataset carregado: {len(df)} amostras")
print(f"Classes disponíveis: {df['label'].unique()}")

def ancora(lista):
    """Ancorar landmarks no primeiro ponto"""
    ancoras = lista[0]
    return [[v[i] - ancoras[i] for i in range(3)] for v in lista]

def zoom(lista):
    """Normalizar escala baseado na distância euclidiana total"""
    s = math.sqrt(sum([v[i] * v[i] for v in lista for i in range(3)]))
    if s == 0: 
        return lista
    return [[v[i] / s for i in range(3)] for v in lista]

def normalizar(lista):
    """Aplicar ancoragem e zoom"""
    return zoom(ancora(lista))

def prever_sinal(pontos):
    """KNN para prever o sinal mais próximo"""
    if pontos is None:
        print("ERRO: Pontos são None")
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

    print(f"Top 3 vizinhos: {vizinhos}")
    print(f"Distância média: {media:.4f}")

    # Threshold de confiança
    if media > 0.7:
        print(f"AVISO: Distância muito alta ({media:.4f}) - threshold: 0.7")
        return "Desconhecido", 0.0

    confianca = 1 / (1 + media)
    print(f"Predição: {mais_comum} (confiança: {confianca:.4f})")
    return mais_comum, confianca


def processar_frame(image):
    """
    Recebe um frame BGR (OpenCV) e retorna (sinal, confiança)
    """
    try:
        print(f"\nProcessando frame: shape={image.shape}")
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        with mp.solutions.hands.Hands(
            static_image_mode=True,
            max_num_hands=1,
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3,
            model_complexity=1
        ) as hands_instance:
            results = hands_instance.process(image_rgb)

        if not results.multi_hand_landmarks:
            print("ERRO: Nenhuma mão detectada")
            return "Desconhecido", 0.0

        print(f"Mão detectada! Total de landmarks: {len(results.multi_hand_landmarks[0].landmark)}")

        for hand in results.multi_hand_landmarks:
            lista = [(lm.x, lm.y, lm.z) for lm in hand.landmark]
            print(f"Landmarks originais (primeiros 3): {lista[:3]}")
            
            lista_norm = normalizar(lista)
            print(f"Landmarks normalizados (primeiros 3): {lista_norm[:3]}")
            
            return prever_sinal(lista_norm)

        return "Desconhecido", 0.0
        
    except Exception as e:
        print(f"ERRO ao processar frame: {e}")
        import traceback
        traceback.print_exc()
        return "Desconhecido", 0.0