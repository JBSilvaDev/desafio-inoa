from django.db import models

# Create your models here.

class AtivosList(models.Model):
  cod_ativo = models.CharField(max_length=5)
  empresa_nome = models.CharField(max_length=100)

  def __str__(self):
    return f'{self.cod_ativo} - {self.empresa_nome}'