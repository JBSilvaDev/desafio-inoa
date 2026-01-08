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
