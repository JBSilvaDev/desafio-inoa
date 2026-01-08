from django.db import models
from django.contrib.auth.models import User
# from ativos_global.models import AtivosList # Removido

class Ativo(models.Model): # Novo modelo Ativo
    cod_ativo = models.CharField(max_length=10, unique=True)
    nome_empresa = models.CharField(max_length=100)

    def __str__(self):
        return self.cod_ativo

class AtivosUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ativo = models.ForeignKey(Ativo, on_delete=models.CASCADE) # Alterado para o novo modelo Ativo
    limite_superior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    limite_inferior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    intervalo_verificacao = models.IntegerField(default=60)  # in minutes
    favorito = models.BooleanField(default=False)
    em_carteira = models.BooleanField(default=False)
    last_alert_sent = models.DateTimeField(null=True, blank=True) # Novo campo

    def __str__(self):
        return f'{self.user.username} - {self.ativo.cod_ativo}'

class PrecoAtivo(models.Model):
    ativo = models.ForeignKey(Ativo, on_delete=models.CASCADE) # Alterado para o novo modelo Ativo
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.ativo.cod_ativo} - {self.preco} - {self.data_hora}'