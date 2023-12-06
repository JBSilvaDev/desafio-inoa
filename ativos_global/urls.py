from django.urls import path

from ativos_global.views import index

urlpatterns = [
  path('', index)
]