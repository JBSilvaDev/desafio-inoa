from django.shortcuts import render

from ativos_user.models import AtivosUser, CodigoAtivo

# Create your views here.
def favoritos(request):
  busca = request.GET.get('cod-ativo')
  if busca:
    ativos = CodigoAtivo.objects.filter(codigo__icontains = busca)
  else:
    ativos = CodigoAtivo.objects.all()
  return render(request, 'favoritos.html', {'ativos':ativos})