from django.contrib import admin
from django.urls import include, path
from auth_user.views import login # Importar a view de login
# from ativos_global.views import detalhes_ativos # Removido

urlpatterns = [
    path('', login, name='home'), # Nova home page é o login
    path('admin/', admin.site.urls),
    path('auth/', include('auth_user.urls', namespace='auth')),
    # path('detalhes/<int:id>', detalhes_ativos, name='detalhes_ativos'), # Removido
    # path('ativos/', include('ativos_global.urls', namespace='ativos')),
    path('favoritos/', include('ativos_user.urls', namespace='ativos_user')), # Adicionar aqui
]
