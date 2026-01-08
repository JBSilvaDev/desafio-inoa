from django.urls import path
from .views import carteira, favoritos, home_ativos, detalhes_ativo, update_ativo_config, add_manual_asset # Importar home_ativos

app_name = 'ativos_user'

urlpatterns = [
    path('', home_ativos, name='home_ativos'), # Nova URL para a Home
    path('carteira/', carteira, name='carteira'), # URL para a carteira
    path('favoritos/', favoritos, name='favoritos'), # URL para favoritos
    path('detalhes/<int:ativo_user_id>/', detalhes_ativo, name='detalhes_ativo'),
    path('update_config/<int:ativo_id>/', update_ativo_config, name='update_ativo_config'),
    path('add_manual/', add_manual_asset, name='add_manual_asset'),
]
