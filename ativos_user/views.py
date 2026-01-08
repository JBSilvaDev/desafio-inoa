from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_POST
from .models import AtivosUser
from .forms import AtivoUserForm

@login_required(login_url='login')
def favoritos(request):
    user = request.user
    busca = request.GET.get('cod-ativo')
    
    if busca:
        ativos_list = AtivosUser.objects.filter(
            Q(cod_ativo__icontains=busca) | Q(nome_empresa__icontains=busca),
            user_id=user
        )
    else:
        ativos_list = AtivosUser.objects.filter(user_id=user)

    # Para cada ativo, crie uma instância do formulário
    for ativo in ativos_list:
        ativo.form = AtivoUserForm(instance=ativo)

    paginacao = Paginator(ativos_list, 10)
    page = request.GET.get('page')
    ativos_por_pagina = paginacao.get_page(page)
    
    return render(request, 'favoritos.html', {'ativos': ativos_por_pagina, "favorito": True})

@require_POST
@login_required
def update_ativo_config(request, ativo_id):
    ativo_user = get_object_or_404(AtivosUser, id=ativo_id, user_id=request.user)
    form = AtivoUserForm(request.POST, instance=ativo_user)
    
    if form.is_valid():
        form.save()
        # Adicione uma mensagem de sucesso se desejar
    else:
        # Adicione uma mensagem de erro se desejar
        pass
        
    return redirect('favoritos')

@require_POST
@login_required
def add_manual_asset(request):
    cod_ativo = request.POST.get('cod_ativo').upper() # Converter para maiúsculas
    nome_empresa = request.POST.get('nome_empresa')
    user = request.user

    if not cod_ativo or not nome_empresa:
        messages.add_message(request, constants.ERROR, 'Código do ativo e nome da empresa não podem ser vazios.')
        return redirect('favoritos')

    # Tenta encontrar ou criar o ativo na lista global
    ativo_global, created_global = AtivosList.objects.get_or_create(
        cod_ativo=cod_ativo,
        defaults={'nome_empresa': nome_empresa}
    )
    if not created_global and ativo_global.nome_empresa != nome_empresa:
        # Se o ativo já existe mas o nome da empresa é diferente, atualiza
        ativo_global.nome_empresa = nome_empresa
        ativo_global.save()

    # Tenta encontrar ou criar o ativo na lista de monitoramento do usuário
    ativo_user, created_user = AtivosUser.objects.get_or_create(
        user=user,
        ativo=ativo_global,
        # O get_or_create usará os defaults do modelo para os outros campos
    )

    if created_user:
        messages.add_message(request, constants.SUCCESS, f'O ativo {cod_ativo} foi adicionado à sua lista de monitoramento.')
    else:
        messages.add_message(request, constants.INFO, f'O ativo {cod_ativo} já estava na sua lista de monitoramento.')
    
    return redirect('favoritos')
