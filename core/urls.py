from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/register/', include("register.urls")),
    path('accounts/login/', include("login.urls")),
    path('', include("camera.urls"))
]
