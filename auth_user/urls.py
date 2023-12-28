from django.urls import include, path

from auth_user.views import *

urlpatterns = [
    path('cadastro/', cadastro, name='cadastro'),
    path('login/', login, name='login'),
    path("sair", sair, name='sair'),
    path('favoritos/', include('ativos_user.urls'), name='favoritos'),
    path('update_wallet/<int:id>', update_wallet, name='update_wallet'),

]