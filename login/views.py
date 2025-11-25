from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def make_login(request):
    error = ""

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("camera")
        else:
            error = "Email ou senha incorretos!"

    return render(request, "login/login.html", {
        "error": error
    })
