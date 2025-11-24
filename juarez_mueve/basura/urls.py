from django.urls import path
from .views import api_unidades_basura
from .views import mapa_basura, posiciones_camiones
from . import views

urlpatterns = [
    
    path("api/unidades/", api_unidades_basura, name="api_unidades_basura"),
    path("mapa/", views.mapa_basura, name="basura_mapa"),
    path("api/posiciones/", posiciones_camiones, name="api_posiciones"),

]
