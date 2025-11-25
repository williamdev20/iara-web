from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from mediapipe_core import processing
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
        return JsonResponse({"erro": "Use POST, amiguinho."}, status=405)

    try:
        data = json.loads(request.body)
        frame_base64 = data["frame"].split(",")[1]

        img_bytes = base64.b64decode(frame_base64)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        print("Recebi frame:", frame.shape)

        # aqui você roda a IA dps
        # resultado = modelo.predict(frame)

        return JsonResponse({"status": "ok", "msg": "frame recebido!"})

    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=400)
