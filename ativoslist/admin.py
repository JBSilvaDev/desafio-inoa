from django.contrib import admin
from ativoslist.models import AtivosTable

# Register your models here.

class ListaAtivosB3(admin.ModelAdmin):
  list_display = ('id', 'cod_ativo', 'empresa_nome')
  list_display_links = ('cod_ativo',)

admin.site.register(AtivosTable, ListaAtivosB3)