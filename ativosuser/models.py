from django.db import models

# Create your models here.
class AtivosUser(models.Model):
    user_id = models.IntegerField()
    nome_empresa = models.CharField(max_length=100)
    codigo_ativo = models.CharField(max_length=5)
    favorito = models.BooleanField()
    em_carteira = models.BooleanField()

    def __str__(self):
        return self.nome_empresa