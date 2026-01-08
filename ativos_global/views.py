from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from ativos_global.models import AtivosList
from ativos_user.models import AtivosUser
from .services import get_stock_history, get_stock_price

def index(request):
    busca = request.GET.get("cod-ativo")
    if busca:
        ativos = AtivosList.objects.filter(Q(cod_ativo__icontains=busca) | Q(nome_empresa__icontains=busca))
    else:
        ativos = AtivosList.objects.all()
    
    # Adicionar informação de monitoramento para cada ativo
    if request.user.is_authenticated:
        monitored_assets_ids = AtivosUser.objects.filter(user=request.user).values_list('ativo__id', flat=True)
        for ativo in ativos:
            ativo.is_monitored = ativo.id in monitored_assets_ids
    else:
        for ativo in ativos:
            ativo.is_monitored = False # Não monitorado se não logado

    paginacao = Paginator(ativos, 15)
    page = request.GET.get('page')
    ativos_por_pagina = paginacao.get_page(page)
    return render(request, "index.html", {"ativos": ativos_por_pagina})

def detalhes_ativos(request, id):
    ativo = get_object_or_404(AtivosList, id=id)
    df = get_stock_history(ativo.cod_ativo)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if df is not None and not df.empty:
            data = {
                'x': df['Datetime'].tolist(),
                'y': df['Close'].tolist(),
                'title': f'<b>Dados de:</b> {ativo.cod_ativo}',
            }
            return JsonResponse(data)
        return JsonResponse({'error': 'Não foi possível obter os dados do ativo.'}, status=404)

    lasts = {}
    if df is not None and not df.empty:
        lasts = {
            "fechamento": f'{df["Close"].iloc[-1]:.2f}',
            "volume": f'{df["Volume"].iloc[-1]}',
        }
    else:
        lasts = {
            "fechamento": "N/D",
            "volume": "N/D",
        }

    # Para uma futura implementação, a variação pode ser calculada com base no histórico de preços.
    lasts['variacao'] = "N/D"

    is_monitored = False
    if request.user.is_authenticated:
        is_monitored = AtivosUser.objects.filter(user=request.user, ativo=ativo).exists()

    context = {
        "ativo": ativo,
        "lasts": lasts,
        "is_monitored": is_monitored
    }

    return render(request, "detalhes.html", context)
