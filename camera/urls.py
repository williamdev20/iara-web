from django.urls import path
from . import views

urlpatterns = [
    path("", views.camera, name="camera"),
    path("process-frame/", views.process_frame, name="process-frame")
]
