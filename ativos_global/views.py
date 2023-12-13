from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
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

def favoritos_carteira(request, id, args):
  user_id = request.user.id
  ativo = get_object_or_404(AtivosList,id=id)
  ativo_fc = get_object_or_404(AtivosUser,id_ativo_list =  id, user_id=user_id)
  if args == '+f':
    print('Add Favorito')
    ativo_user = AtivosUser(
      user_id = User.objects.get(username=request.user.username),
      id_ativo_list = id,
      cod_ativo = ativo.cod_ativo,
      nome_empresa = ativo.nome_empresa,
      favorito = True,
      em_carteira = False,
      variacao_percent = 0.0
    )
    ativo_user.save()
  elif args == '-f':
    print('Remove favorito')
    ativo_fc.delete()
  elif args == '+c':
    print("ADD carteira")
    ativo_fc.em_carteira = 1
    ativo_fc.save()
  elif args == '-c':
    ativo_fc.em_carteira = 0
    ativo_fc.save()
    print("Remove carteira")
  print(args)
  return None

def update_carteira(request, id):
  ativo = get_object_or_404(AtivosList,id=id)
  ativo_favorito = get_object_or_404(AtivosUser,cod_ativo =  ativo.cod_ativo)
  ativo_favorito.em_carteira = not ativo_favorito.em_carteira
  ativo_favorito.save()
  return render(request, 'detalhes.html', {'ativo':ativo})