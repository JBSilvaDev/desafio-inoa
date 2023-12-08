from django.urls import path

from ativos_user.views import *

urlpatterns = [
    path('', favoritos, name='favoritos'),
]
