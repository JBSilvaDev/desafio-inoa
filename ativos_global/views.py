from django.shortcuts import render
from django.shortcuts import get_object_or_404
from ativos_global.models import AtivosList
from ativos_user.models import AtivosUser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import yfinance as yf
from django.db.models import Q
import plotly.express as px
from django.core.paginator import Paginator
from django.http import JsonResponse

# Create your views here.
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
    plot_grafico = yf.Ticker(f'{ativo.cod_ativo}.SA')
    df = plot_grafico.history(period="1d", interval='15m')
    df = df.reset_index()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Verifica se a solicitação é AJAX
        data = {
            'x': df['Datetime'].tolist(),
            'y': df['Close'].tolist(),
            'title': f'<b>Dados de:</b> {ativo.cod_ativo}',
        }
        return JsonResponse(data)
    
    lasts = {
        "fechamento":f'{df['Close'].tolist()[-1]:.2f}', 
        "volume":f'{df['Volume'].tolist()[-1]}',
    }
    user_id = request.user.id
    ativo_fc = AtivosUser.objects.filter(cod_ativo=ativo.cod_ativo, user_id=user_id).first()

    if ativo_fc:
        variacao_percent_valor = ativo_fc.variacao_percent
        lasts['variacao'] = f'{variacao_percent_valor/100:.1%}'
    else:
        lasts['variacao'] = f'{0:.1%}'


    grafico = px.line(df, x='Datetime', y='Close', markers=True, title=f'<b>Dados de:</b> {ativo.cod_ativo}')
    grafico.update_traces(textposition='top center', textfont_size=10)
    plot_div = grafico.to_html(full_html=True)
    return render(request, "detalhes.html", {"ativo": ativo, "lasts":lasts})


@csrf_exempt
def update_data(request, id):
    ativo = get_object_or_404(AtivosList, id=id)
    plot_grafico = yf.Ticker(f'{ativo.cod_ativo}.SA')
    df = plot_grafico.history(period="1d", interval='15m')
    df = df.reset_index()

    data = {
        'x': df['Datetime'].tolist(),
        'y': df['Close'].tolist(),
        'title': f'<b>Dados de:</b> {ativo.cod_ativo}',
    }

    return JsonResponse(data)
