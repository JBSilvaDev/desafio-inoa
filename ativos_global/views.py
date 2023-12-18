from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from ativos_global.models import AtivosList
from ativos_user.models import AtivosUser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import yfinance as yf
import plotly.express as px


# Create your views here.
def index(request):
    busca = request.GET.get("cod-ativo")
    if busca:
        ativos = AtivosList.objects.filter(cod_ativo__icontains=busca)
    else:
        ativos = AtivosList.objects.all()
    return render(request, "index.html", {"ativos": ativos})


from django.http import JsonResponse

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
    
    user_id = request.user.id
    ativo_fc = AtivosUser.objects.filter(cod_ativo=ativo.cod_ativo).filter(
        user_id=user_id
    )
    ativos_favoritos = AtivosUser.objects.all().filter(user_id=user_id)

    grafico = px.line(df, x='Datetime', y='Close', markers=True, title=f'<b>Dados de:</b> {ativo.cod_ativo}')
    grafico.update_traces(textposition='top center', textfont_size=10)
    plot_div = grafico.to_html(full_html=True)
    return render(request, "detalhes.html", {"ativo": ativo, 'plot_div': plot_div})


from django.http import JsonResponse

@csrf_exempt
def update_data(request, id):
    ativo = get_object_or_404(AtivosList, id=id)
    plot_grafico = yf.Ticker(f'{ativo.cod_ativo}.SA')
    df = plot_grafico.history(period="1d", interval='5m')
    df = df.reset_index()

    print(df['Close'].tolist()[-1])
    data = {
        'x': df['Datetime'].tolist(),
        'y': df['Close'].tolist(),
        'title': f'<b>Dados de:</b> {ativo.cod_ativo}',
    }

    return JsonResponse(data)
