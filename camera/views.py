from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from mediapipe_core import processing
from gtts import gTTS
import io # Biblioteca para não precisar salvar os áudios em disco, mas sim em RAM
import json
import base64
import numpy as np
import cv2


@login_required(login_url="/accounts/login/")
def camera(request):
    return render(request, "camera/camera.html")

@csrf_exempt
@login_required(login_url="/accounts/login/")
def process_frame(request):
    if request.method != "POST":
        return JsonResponse({"erro": "Usa POST, amiguinho."}, status=405)

    try:
        data = json.loads(request.body) # Converte o json para dicionário python
        frame_base64 = data["frame"].split(",")[1] # Pega apenas os dados da imagem em base64

        img_bytes = base64.b64decode(frame_base64) # Converte o a string base64 para base64 da imagem
        np_arr = np.frombuffer(img_bytes, np.uint8) # Transformar os bytes em um array do Numpy, pois é o formato que o OpenCV usa
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR) # Transforma o array de bytes em uma imagem colorida (RGB)
        frame = cv2.flip(frame, 1) # Tipo, se você colocar a mão esquerda na foto, ele faz a sua mão virar a direita


        sinal, confianca = processing.processar_frame(frame)

        voice_url = f"/tts/{sinal}/"


        return JsonResponse({
            "sinal": sinal,
            "confianca": float(confianca),
            "voice_url": voice_url
        })

    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=400)


@csrf_exempt
@login_required(login_url="/accounts/login/")
def tts_voice(request, sinal):
    if request.method == "GET":
        voice_file = io.BytesIO()
        voice = gTTS(text=sinal, lang="pt-br")
        voice.write_to_fp(voice_file)
        voice_file.seek(0)
        
        return HttpResponse(voice_file, content_type="audio/mpeg")
