from asyncio import constants
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from django.contrib.messages import constants


# Create your views here.
def cadastro(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        if User.objects.filter(username=nome).exists():
            messages.add_message(request, constants.WARNING, f'Usuário {nome} ja cadastrado, faça login, ou um novo cadastro')
            return redirect('login')
        elif User.objects.filter(email=email).exists():
            messages.add_message(request, constants.WARNING, f'Usuário {email} ja cadastrado, faça login, ou um novo cadastro')
            return redirect('login')
        if len(nome.strip()) == 0 or len(email.strip()) == 0:
            messages.add_message(request, constants.ERROR, 'Nome e E-mail não podem ser vazios')
            return render(request, "cadastro.html")
        usuario = User.objects.create_user(username=nome, email=email, password=senha)
        usuario.save()
        messages.add_message(request, constants.SUCCESS, f'Cadastro realizado com sucesso, {nome}, faça login para acesso total')
        return redirect("login")
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
            messages.add_message(request, constants.SUCCESS, 'Login realizado com sucesso')
            return redirect("index")
        else:
            messages.add_message(request, constants.WARNING, 'Usuário ou senha invalidos, faça cadastro caso nao tenha conta registrada')
            return redirect('cadastro')
    return render(request, "login.html")


def sair(request):
    if not request.user.is_authenticated:
        return redirect("login")
    auth.logout(request)
    return redirect("index")
