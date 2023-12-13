from django.shortcuts import render
from django.shortcuts import get_object_or_404

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
  ativo = get_object_or_404(AtivosList,id=id)
  return render(request, 'detalhes.html', {'ativo':ativo})

def remove_favorito(request, id):
  print(id)
  ativo = get_object_or_404(AtivosList,id=id)
  ativo_favorito = get_object_or_404(AtivosUser,cod_ativo =  ativo.cod_ativo)
  ativo_favorito.delete()
  return render(request, 'detalhes.html', {'ativo':ativo})

def update_carteira(request, id):
  ativo = get_object_or_404(AtivosList,id=id)
  ativo_favorito = get_object_or_404(AtivosUser,cod_ativo =  ativo.cod_ativo)
  ativo_favorito.em_carteira = not ativo_favorito.em_carteira
  ativo_favorito.save()
  return render(request, 'detalhes.html', {'ativo':ativo})