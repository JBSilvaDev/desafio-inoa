from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from ativos_user.models import AtivosUser

import yfinance as yf
import plotly.express as px

acao = 'CIEL3'

msft = yf.Ticker(f'{acao}.SA')
df = msft.history(period="1mo")
df = df.reset_index()

# Create your views here.
def favoritos(request):
  user_id = request.user.id # ID do usuario logado
  if not user_id:
    return HttpResponse("Voce precisa esta logado")
  busca = request.GET.get('cod-ativo')
  if busca:
    ativos = AtivosUser.objects.filter(cod_ativo__icontains = busca).filter(user_id = user_id)
  else:
    ativos = AtivosUser.objects.all().filter(user_id = user_id)
  grafico = px.line(df, x='Date', y='Close', markers=True, title=f'<b>Dados de:</b> {acao}')
  plot_div = grafico.to_html(full_html=True)
  return render(request, 'favoritos.html', {'ativos':ativos, 'plot_div':plot_div})


