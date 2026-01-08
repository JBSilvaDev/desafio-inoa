from django.urls import path
from .views import carteira, favoritos, detalhes_ativo, update_ativo_config, add_manual_asset # Importar detalhes_ativo

app_name = 'ativos_user'

urlpatterns = [
    path('', carteira, name='carteira'),
    path('favoritos/', favoritos, name='favoritos'),
    path('detalhes/<int:ativo_user_id>/', detalhes_ativo, name='detalhes_ativo'), # Nova URL
    path('update_config/<int:ativo_id>/', update_ativo_config, name='update_ativo_config'),
    path('add_manual/', add_manual_asset, name='add_manual_asset'),
]
