from django.urls import path
from .views import favoritos, update_ativo_config

urlpatterns = [
    path('', favoritos, name='favoritos'),
    path('update_config/<int:ativo_id>/', update_ativo_config, name='update_ativo_config'),
]
