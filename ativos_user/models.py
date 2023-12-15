from django.db import models
from django.contrib.auth.models import User


   

class AtivosUser(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    id_ativo_list = models.IntegerField()
    cod_ativo = models.CharField(max_length=6, )
    nome_empresa = models.CharField(max_length=100)
    favorito = models.BooleanField()
    em_carteira = models.BooleanField()
    variacao_percent = models.FloatField()

    def __str__(self):
        return self.nome_empresa