from django.http import HttpResponse
from django.shortcuts import render

from ativos_global.models import AtivosList

# Create your views here.
def index(request):
  busca = request.GET.get('cod-ativo')
  if busca:
    ativos = AtivosList.objects.filter(cod_ativo__icontains = busca)
  else:
    ativos = AtivosList.objects.all()
  return render(request, 'index.html', {'ativos':ativos})