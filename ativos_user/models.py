from django.db import models


# Create your models here.
# class CodigoAtivo(models.Model):
#     user_id = models.IntegerField()
#     codigo = models.CharField(max_length=5, )
#     nome_empresa = models.CharField(max_length=100)
#     favorito = models.BooleanField()
#     em_carteira = models.BooleanField()
#     variacao_percent = models.FloatField()

#     def __str__(self):
#         return self.codigo
    

class AtivosUser(models.Model):
    user_id = models.IntegerField()
    codigo_ativo = models.CharField(max_length=5, )
    nome_empresa = models.CharField(max_length=100)
    favorito = models.BooleanField()
    em_carteira = models.BooleanField()
    variacao_percent = models.FloatField()

    def __str__(self):
        return self.nome_empresa