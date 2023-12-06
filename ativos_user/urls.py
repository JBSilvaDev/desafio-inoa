from django.urls import path

from ativos_user.views import favoritos

urlpatterns = [
    path('', favoritos),
]
