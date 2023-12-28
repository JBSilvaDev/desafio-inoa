
from django.contrib import admin
from django.urls import include, path

from ativos_global.views import *

urlpatterns = [
    path('', include('ativos_global.urls'), name='inicial-page'),
    path('admin/', admin.site.urls),
    path('auth/', include('auth_user.urls')),
    path('detalhes/<int:id>', detalhes_ativos, name='detalhes_ativos'),
    path('update_data/<int:id>/', update_data, name='update_data'),
]
