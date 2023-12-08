from django.urls import path

from ativos_global.views import *


urlpatterns = [
  path('', index),
]