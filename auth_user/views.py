from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import auth


# Create your views here.
def cadastro(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        if User.objects.filter(username=nome).exists():
            return HttpResponse("<h1> Usuario ja cadastrado </h1>")
        elif User.objects.filter(email=email).exists():
            return HttpResponse("<h1> Email ja cadastrado </h1>")
        usuario = User.objects.create_user(username=nome, email=email, password=senha)
        usuario.save()
    return render(request, "cadastro.html")


def login(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        senha = request.POST.get("senha")
        usuario = auth.authenticate(
            request,
            username=nome,
            password=senha,
        )
        if usuario is not None:
            auth.login(request, usuario)
            return redirect("index")
        else:
            return HttpResponse("<h1> Usuario ou senha invalidos </h1>")
    return render(request, "login.html")


def sair(request):
    if not request.user.is_authenticated:
        return redirect("login")
    auth.logout(request)
    return redirect("favoritos")
