from django.urls import path
from .views import favoritos, update_ativo_config, add_manual_asset # Importar add_manual_asset

app_name = 'ativos_user' # Adicionar esta linha

urlpatterns = [
    path('', favoritos, name='favoritos'),
    path('update_config/<int:ativo_id>/', update_ativo_config, name='update_ativo_config'),
    path('add_manual/', add_manual_asset, name='add_manual_asset'), # Nova URL
]
