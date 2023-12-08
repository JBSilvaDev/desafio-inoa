from django.http import HttpResponse
from django.shortcuts import render

from ativos_global.models import AtivosList
from ativos_user.models import AtivosUser

# Create your views here.
def index(request):
  busca = request.GET.get('cod-ativo')
  if busca:
    ativos = AtivosList.objects.filter(cod_ativo__icontains = busca)
  else:
    ativos = AtivosList.objects.all()
  return render(request, 'index.html', {'ativos':ativos})

def detalhes_ativos(request, id):
  ativo = AtivosUser.objects.get(id=id)
  return render(request, 'detalhes.html', {'ativo':ativo})