from django.db import models
from django.contrib.auth.models import User
from ativos_global.models import AtivosList


class AtivosUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ativo = models.ForeignKey(AtivosList, on_delete=models.CASCADE)
    limite_superior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    limite_inferior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    intervalo_verificacao = models.IntegerField(default=60)  # in minutes

    def __str__(self):
        return f'{self.user.username} - {self.ativo.cod_ativo}'

class PrecoAtivo(models.Model):
    ativo = models.ForeignKey(AtivosList, on_delete=models.CASCADE)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.ativo.cod_ativo} - {self.preco} - {self.data_hora}'