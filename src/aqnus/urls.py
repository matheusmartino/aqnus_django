from django.contrib import admin
from django.urls import include, path

# Personalização do Django Admin
admin.site.site_header = 'AQNUS - Gestão Educacional'
admin.site.site_title = 'AQNUS'
admin.site.index_title = 'Painel Administrativo'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('web.urls')),
]
