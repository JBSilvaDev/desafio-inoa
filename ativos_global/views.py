from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from ativos_global.models import AtivosList
from ativos_user.models import AtivosUser


# Create your views here.
def index(request):
    busca = request.GET.get("cod-ativo")
    if busca:
        ativos = AtivosList.objects.filter(cod_ativo__icontains=busca)
    else:
        ativos = AtivosList.objects.all()
    return render(request, "index.html", {"ativos": ativos})


def detalhes_ativos(request, id):
    ativo = get_object_or_404(AtivosList, id=id)
    user_id = request.user.id
    ativo_fc = AtivosUser.objects.filter(cod_ativo=ativo.cod_ativo).filter(
        user_id=user_id
    )
    ativos_favoritos = AtivosUser.objects.all().filter(user_id=user_id)
    if request.method == "POST":
        if "+f" in request.POST:
            if len(ativo_fc) == 0:
                ativo_user = AtivosUser(
                    user_id=User.objects.get(username=request.user.username),
                    id_ativo_list=id,
                    cod_ativo=ativo.cod_ativo,
                    nome_empresa=ativo.nome_empresa,
                    favorito=True,
                    em_carteira=False,
                    variacao_percent=0.0,
                )
                ativo_user.save()
                return render(request, "favoritos.html", {"ativos": ativos_favoritos})
        elif "-f" in request.POST:
            ativo_fc.first().delete()
            return render(request, "favoritos.html", {"ativos": ativos_favoritos})
        else:
            if len(ativo_fc) == 0:
                ativo_user = AtivosUser(
                    user_id=User.objects.get(username=request.user.username),
                    id_ativo_list=id,
                    cod_ativo=ativo.cod_ativo,
                    nome_empresa=ativo.nome_empresa,
                    favorito=True,
                    em_carteira=True,
                    variacao_percent=0.0,
                )
                ativo_user.save()
            else:
                ativo_user = ativo_fc.first()
                ativo_user.em_carteira = not ativo_user.em_carteira
                ativo_user.save()
            return render(request, "favoritos.html", {"ativos": ativos_favoritos})

    return render(request, "detalhes.html", {"ativo": ativo})
