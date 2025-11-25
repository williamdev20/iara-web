from django.urls import path
from . import views

urlpatterns = [
    path('', views.make_register, name="make_register")
]
