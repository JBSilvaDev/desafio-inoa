from django.contrib import admin

from ativos_user.models import AtivosUser

class ListaAtivosUser(admin.ModelAdmin):
  list_display = ('user_id', 'cod_ativo','nome_empresa','favorito', 'em_carteira', 'variacao_percent')
  list_display_links = ('cod_ativo','nome_empresa')
  list_filter = ('cod_ativo','nome_empresa')
  list_per_page = 10



admin.site.register(AtivosUser, ListaAtivosUser)
