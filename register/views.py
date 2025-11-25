from django.shortcuts import render, redirect
from users.models import User
from django.db import IntegrityError

def make_register(request):
    error = ""
    error_password_confirm = ""

    if request.method == "POST":
        try:
            username = request.POST.get("username")
            email = request.POST.get("email")
            password = request.POST.get("password")
            password_confirm = request.POST.get("password_confirm")

            if password != password_confirm:
                error_password_confirm = "As senhas não coincidem!"
            else:
                User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                return redirect("make_login")

        except IntegrityError as e:
            error = "Essa conta já existe!"
            print(f"ERROR: Erro ao tentar criar uma conta: {e}")

    return render(request, "register/register.html", {
        "error": error,
        "error_password_confirm": error_password_confirm
    })