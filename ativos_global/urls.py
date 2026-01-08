from django.urls import path

from ativos_global.views import *

app_name = 'ativos_global' # Adicionar esta linha

urlpatterns = [
  path('', index, name='index'),
]