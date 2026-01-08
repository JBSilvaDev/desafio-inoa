from django.urls import path
from .views import carteira, favoritos, update_ativo_config, add_manual_asset # Importar carteira e favoritos

app_name = 'ativos_user'

urlpatterns = [
    path('', carteira, name='carteira'), # Nova URL para a carteira
    path('favoritos/', favoritos, name='favoritos'), # Nova URL para favoritos
    path('update_config/<int:ativo_id>/', update_ativo_config, name='update_ativo_config'),
    path('add_manual/', add_manual_asset, name='add_manual_asset'),
]
