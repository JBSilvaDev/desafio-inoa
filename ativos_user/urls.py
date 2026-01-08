from django.urls import path
from .views import carteira, favoritos, home_ativos, detalhes_ativo, update_ativo_config, add_manual_asset, excluir_ativo # Importar excluir_ativo

app_name = 'ativos_user'

urlpatterns = [
    path('', home_ativos, name='home_ativos'),
    path('carteira/', carteira, name='carteira'),
    path('favoritos/', favoritos, name='favoritos'),
    path('detalhes/<int:ativo_user_id>/', detalhes_ativo, name='detalhes_ativo'),
    path('update_config/<int:ativo_id>/', update_ativo_config, name='update_ativo_config'),
    path('add_manual/', add_manual_asset, name='add_manual_asset'),
    path('excluir/<int:ativo_user_id>/', excluir_ativo, name='excluir_ativo'), # Nova URL
]
