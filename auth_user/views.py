from asyncio import constants
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from django.contrib.messages import constants
from ativos_global.models import AtivosList
from django.core.paginator import Paginator
from ativos_user.models import AtivosUser


# Create your views here.
def cadastro(request):
    if request.user.is_authenticated:
        return redirect('index')
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
    if request.user.is_authenticated:
        return redirect('index')
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

from django.views.decorators.http import require_POST

@require_POST
def update_wallet(request, id):
    ativo_global = get_object_or_404(AtivosList, id=id)
    user = request.user

    # Tenta encontrar o ativo na lista de monitoramento do usuário
    ativo_user, created = AtivosUser.objects.get_or_create(
        user=user,
        ativo=ativo_global,
        # O get_or_create usará os defaults do modelo para os outros campos
    )

    if created:
        messages.add_message(request, constants.SUCCESS, f'O ativo {ativo_global.cod_ativo} foi adicionado à sua lista de monitoramento.')
    else:
        # Se o objeto não foi criado, significa que ele já existia e deve ser removido.
        ativo_user.delete()
        messages.add_message(request, constants.SUCCESS, f'O ativo {ativo_global.cod_ativo} foi removido da sua lista de monitoramento.')

    return redirect('detalhes_ativos', id=id)
