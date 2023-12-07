from django.db import models


# Create your models here.
class CodigoAtivo(models.Model):
    codigo = models.CharField(max_length=5, )
    favorito = models.BooleanField()
    em_carteira = models.BooleanField()

    def __str__(self):
        return self.codigo
    

class AtivosUser(models.Model):
    user_id = models.IntegerField()
    nome_empresa = models.CharField(max_length=100)
    codigo_ativo = models.ForeignKey('CodigoAtivo', related_name = 'cod_ativos', on_delete=models.CASCADE)

    def __str__(self):
        return self.nome_empresa