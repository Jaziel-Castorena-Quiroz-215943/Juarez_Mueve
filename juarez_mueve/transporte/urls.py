from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    mapa_principal,
    mapa_ciudad,
    api_unidades,
    unidades_con_ubicacion,
    rutas_mapa,
    gestionar_rutas,
    UnidadViewSet,
)

router = DefaultRouter()
router.register(r'unidades', UnidadViewSet, basename='unidad')

urlpatterns = [
    # 👉 Alias con el nombre que te pide el dashboard
    path('mapa/', mapa_principal, name='mapa'),

    # (opcional) si quieres conservar también el nombre anterior
    path('mapa-principal/', mapa_principal, name='mapa_principal'), 
    path('rutas/gestionar/', gestionar_rutas, name='gestionar_rutas'),


    path('mapa-ciudad/', mapa_ciudad, name='mapa_ciudad'),
    path('api/unidades/', api_unidades, name='api_unidades'),
    path('api/unidades-con-ubicacion/', unidades_con_ubicacion, name='unidades_con_ubicacion'),
    path('api/rutas/', rutas_mapa, name='rutas_mapa'),
]

urlpatterns += router.urls
