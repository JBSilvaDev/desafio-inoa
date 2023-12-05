from django.contrib import admin
from ativoslist.models import AtivosTable

# Register your models here.

class ListaAtivosB3(admin.ModelAdmin):
  list_display = ('id', 'cod_ativo', 'empresa_nome')
  list_display_links = ('cod_ativo',)
  list_filter = ('cod_ativo',)
  list_per_page = 10

admin.site.register(AtivosTable, ListaAtivosB3)