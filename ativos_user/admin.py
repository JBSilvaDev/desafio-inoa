from django.contrib import admin

from ativos_user.models import AtivosUser

class ListaAtivosUser(admin.ModelAdmin):
  list_display = ('id', 'codigo_ativo','nome_empresa','favorito', 'em_carteira', 'variacao_percent')
  list_display_links = ('codigo_ativo','nome_empresa')
  list_filter = ('codigo_ativo','nome_empresa')
  list_per_page = 10


# class ListaCodigosAtivoUser(admin.ModelAdmin):
#   list_display = ('id', 'codigo', 'nome_empresa','favorito', 'em_carteira', 'variacao_percent')
#   list_display_links = ('codigo',)
#   list_filter = ('codigo',)
#   list_per_page = 10

admin.site.register(AtivosUser, ListaAtivosUser)
# admin.site.register(CodigoAtivo, ListaCodigosAtivoUser)