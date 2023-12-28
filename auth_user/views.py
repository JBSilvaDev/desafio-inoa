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

def update_wallet(request, id):
    ativo = get_object_or_404(AtivosList, id=id)
    user_id = request.user.id
    ativo_fc = AtivosUser.objects.filter(cod_ativo=ativo.cod_ativo).filter(
        user_id=user_id)
    ativos_favoritos = AtivosUser.objects.all().filter(user_id=user_id)
    paginacao = Paginator(ativos_favoritos, 10)
    page = request.GET.get('page')
    ativos_por_pagina = paginacao.get_page(page)
    if request.method == "POST":
            if "+f" in request.POST:
                if len(ativo_fc) == 0:
                    ativo_user = AtivosUser(
                        user_id=User.objects.get(username=request.user.username),
                        id_ativo_list=id,
                        cod_ativo=ativo.cod_ativo,
                        nome_empresa=ativo.nome_empresa,
                        favorito=True,
                        em_carteira=False,
                        variacao_percent=0.0,
                    )
                    ativo_user.save()
                    return render(request, "favoritos.html", {"ativos": ativos_por_pagina})
            elif "-f" in request.POST:
                ativo_fc.first().delete()
                return render(request, "favoritos.html", {"ativos": ativos_por_pagina})
            else:
                if len(ativo_fc) == 0:
                    ativo_user = AtivosUser(
                        user_id=User.objects.get(username=request.user.username),
                        id_ativo_list=id,
                        cod_ativo=ativo.cod_ativo,
                        nome_empresa=ativo.nome_empresa,
                        favorito=True,
                        em_carteira=True,
                        variacao_percent=0.0,
                    )
                    ativo_user.save()
                else:
                    ativo_user = ativo_fc.first()
                    ativo_user.em_carteira = not ativo_user.em_carteira
                    ativo_user.save()
                return render(request, "favoritos.html", {"ativos": ativos_por_pagina})

    return render(request, "detalhes.html", {"ativo": ativo})
