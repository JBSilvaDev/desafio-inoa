from django.contrib import admin
from .models import AtivosUser, PrecoAtivo

class AtivosUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'ativo', 'limite_superior', 'limite_inferior', 'intervalo_verificacao')
    list_display_links = ('user', 'ativo')
    search_fields = ('user__username', 'ativo__cod_ativo')
    list_per_page = 10

class PrecoAtivoAdmin(admin.ModelAdmin):
    list_display = ('ativo', 'preco', 'data_hora')
    list_display_links = ('ativo',)
    search_fields = ('ativo__cod_ativo',)
    list_per_page = 10

admin.site.register(AtivosUser, AtivosUserAdmin)
admin.site.register(PrecoAtivo, PrecoAtivoAdmin)