from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required # Adicionar esta linha
from django.core.paginator import Paginator # Adicionar esta linha
from django.db.models import Q # Adicionar esta linha
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.messages import constants

# from ativos_global.models import AtivosList # Removido
from .models import Ativo, AtivosUser # Importar o novo modelo Ativo
from .forms import AtivoUserForm

@login_required(login_url='login')
def carteira(request): # Renomeado de favoritos para carteira
    user = request.user
    busca = request.GET.get('cod-ativo')
    
    # Filtrar apenas ativos que estão "em_carteira"
    if busca:
        ativos_list = AtivosUser.objects.filter(
            Q(ativo__cod_ativo__icontains=busca) | Q(ativo__nome_empresa__icontains=busca),
            user=user,
            em_carteira=True # Filtrar por em_carteira
        )
    else:
        ativos_list = AtivosUser.objects.filter(user=user, em_carteira=True) # Filtrar por em_carteira

    # Para cada ativo, crie uma instância do formulário
    for ativo in ativos_list:
        ativo.form = AtivoUserForm(instance=ativo)

    paginacao = Paginator(ativos_list, 10)
    page = request.GET.get('page')
    ativos_por_pagina = paginacao.get_page(page)
    
    return render(request, 'favoritos.html', {'ativos': ativos_por_pagina, "favorito": True}) # Renderizar o template 'favoritos.html' por enquanto

@login_required(login_url='login')
def favoritos(request): # Nova view para favoritos
    user = request.user
    busca = request.GET.get('cod-ativo')
    
    # Filtrar apenas ativos que estão "favorito"
    if busca:
        ativos_list = AtivosUser.objects.filter(
            Q(ativo__cod_ativo__icontains=busca) | Q(ativo__nome_empresa__icontains=busca),
            user=user,
            favorito=True # Filtrar por favorito
        )
    else:
        ativos_list = AtivosUser.objects.filter(user=user, favorito=True) # Filtrar por favorito

    # Para cada ativo, crie uma instância do formulário
    for ativo in ativos_list:
        ativo.form = AtivoUserForm(instance=ativo)

    paginacao = Paginator(ativos_list, 10)
    page = request.GET.get('page')
    ativos_por_pagina = paginacao.get_page(page)
    
    return render(request, 'favoritos.html', {'ativos': ativos_por_pagina, "favorito": True}) # Renderizar o template 'favoritos.html' por enquanto

@require_POST
@login_required
def update_ativo_config(request, ativo_id):
    ativo_user = get_object_or_404(AtivosUser, id=ativo_id, user=request.user)
    form = AtivoUserForm(request.POST, instance=ativo_user)
    
    if form.is_valid():
        form.save()

        if not ativo_user.favorito and not ativo_user.em_carteira:
            ativo_user.delete()
            messages.add_message(request, constants.SUCCESS, f'Ativo {ativo_user.ativo.cod_ativo} removido do monitoramento.')
        else:
            messages.add_message(request, constants.SUCCESS, f'Configurações do ativo {ativo_user.ativo.cod_ativo} atualizadas com sucesso.')
    else:
        messages.add_message(request, constants.ERROR, 'Erro ao atualizar configurações do ativo.')
        
    return redirect('ativos_user:carteira')

@require_POST
@login_required
def add_manual_asset(request):
    cod_ativo = request.POST.get('cod_ativo').upper()
    nome_empresa = request.POST.get('nome_empresa')
    user = request.user

    favorito = request.POST.get('favorito') == 'on'
    em_carteira = request.POST.get('em_carteira') == 'on'

    if not cod_ativo or not nome_empresa:
        messages.add_message(request, constants.ERROR, 'Código do ativo e nome da empresa não podem ser vazios.')
        return redirect('ativos_user:carteira')

    # Criar ou obter o novo modelo Ativo
    ativo_obj, created_ativo = Ativo.objects.get_or_create( # Alterado para o novo modelo Ativo
        cod_ativo=cod_ativo,
        defaults={'nome_empresa': nome_empresa}
    )
    if not created_ativo and ativo_obj.nome_empresa != nome_empresa:
        ativo_obj.nome_empresa = nome_empresa
        ativo_obj.save()

    # Tenta encontrar ou criar o ativo na lista de monitoramento do usuário
    ativo_user, created_user = AtivosUser.objects.get_or_create(
        user=user,
        ativo=ativo_obj, # Associar ao novo modelo Ativo
        defaults={'favorito': favorito, 'em_carteira': em_carteira}
    )

    if created_user:
        messages.add_message(request, constants.SUCCESS, f'O ativo {cod_ativo} foi adicionado à sua lista de monitoramento.')
    else:
        if ativo_user.favorito != favorito or ativo_user.em_carteira != em_carteira:
            ativo_user.favorito = favorito
            ativo_user.em_carteira = em_carteira
            ativo_user.save()
            messages.add_message(request, constants.SUCCESS, f'O status do ativo {cod_ativo} foi atualizado.')
        else:
            messages.add_message(request, constants.INFO, f'O ativo {cod_ativo} já estava na sua lista de monitoramento com os mesmos status.')
    
    return redirect('ativos_user:carteira')
