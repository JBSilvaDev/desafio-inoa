from django.urls import path

from auth_user.views import cadastro

urlpatterns = [
    path('cadastro/', cadastro),
]