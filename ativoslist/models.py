from django.db import models

# Create your models here.

class AtivosTable(models.Model):
  cod_ativo = models.CharField(max_length=4)
  empresa_nome = models.CharField(max_length=100)