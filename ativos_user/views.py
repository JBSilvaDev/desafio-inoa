from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from ativos_user.models import AtivosUser
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required(login_url='login')
def favoritos(request):
  user_id = request.user.id # ID do usuario logado
  busca = request.GET.get('cod-ativo')
  if busca:
    ativos = AtivosUser.objects.filter(cod_ativo__icontains = busca).filter(user_id = user_id)
  else:
    ativos = AtivosUser.objects.all().filter(user_id = user_id)

  return render(request, 'favoritos.html', {'ativos':ativos})


