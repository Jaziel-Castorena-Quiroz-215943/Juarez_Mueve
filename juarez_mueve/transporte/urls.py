from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UnidadViewSet,
    unidades_con_ubicacion,
    mapa_principal,
    listar_unidades,
    crear_unidad,
    editar_unidad,
    toggle_unidad_activa,
    lista_rutas,
    crear_ruta,
    editar_ruta,
    rutas_mapa,
    api_rutas,
    editar_unidad,
    toggle_unidad  
)

router = DefaultRouter()
router.register(r'unidades', UnidadViewSet, basename='unidades')

urlpatterns = [
    # Mapa principal
    path('', mapa_principal, name='mapa'),

    # API
    path('api/', include(router.urls)),
    path('api/unidades/', unidades_con_ubicacion, name='unidades-list'),

    # Panel de unidades
    path('admin/unidades/', listar_unidades, name='unidades_lista'),
    path('admin/unidades/nueva/', crear_unidad, name='unidades_crear'),
    path('admin/unidades/<int:pk>/editar/', editar_unidad, name='unidades_editar'),
    path('admin/unidades/<int:pk>/toggle/', toggle_unidad_activa, name='unidades_toggle'),
    path('unidades/', listar_unidades, name='listar_unidades'),
    path('unidades/crear/', crear_unidad, name='crear_unidad'),
    path('unidades/<int:pk>/editar/', editar_unidad, name='editar_unidad'),
    path('unidades/<int:pk>/toggle/', toggle_unidad, name='toggle_unidad'),

    # Panel de rutas
    path('admin/rutas/', lista_rutas, name='rutas_lista'),
    path('admin/rutas/nueva/', crear_ruta, name='rutas_crear'),
    path('admin/rutas/<int:pk>/editar/', editar_ruta, name='rutas_editar'),
    path('api/rutas_mapa/', rutas_mapa, name='rutas-mapa'),
    path("api/rutas/", api_rutas, name="api_rutas"),

]
