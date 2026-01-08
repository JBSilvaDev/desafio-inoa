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

    user_id = request.user.id
    ativo_fc = AtivosUser.objects.filter(cod_ativo=ativo.cod_ativo, user_id=user_id).first()

    if ativo_fc and ativo_fc.variacao_percent is not None:
        lasts['variacao'] = f'{ativo_fc.variacao_percent/100:.1%}'
    else:
        lasts['variacao'] = f'{0:.1%}'

    return render(request, "detalhes.html", {"ativo": ativo, "lasts": lasts})
