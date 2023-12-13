
from django.contrib import admin
from django.urls import include, path

from ativos_global.views import *

urlpatterns = [
    path('', include('ativos_global.urls'), name='inicial-page'),
    path('admin/', admin.site.urls),
    path('auth/', include('auth_user.urls')),
    path('favoritos/', include('ativos_user.urls'), name='favoritos'),
    path('detalhes/<int:id>', detalhes_ativos, name='detalhes_ativos'),
    path('<int:id>', remove_favorito, name='remove_favorito'),
    path('<int:id>', update_carteira, name='update_carteira'),
]
