from django.urls import include, path

from auth_user.views import *

app_name = 'auth_user' # Adicionar esta linha

urlpatterns = [
    path('cadastro/', cadastro, name='cadastro'),
    path('login/', login, name='login'),
    path("sair", sair, name='sair'),
    path('update_wallet/<int:id>', update_wallet, name='update_wallet'),

]