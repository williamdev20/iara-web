from django.urls import path
from . import views

urlpatterns = [
    path('', views.make_login, name="make_login")
]
