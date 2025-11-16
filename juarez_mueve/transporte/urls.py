from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UnidadViewSet, unidades_con_ubicacion, mapa_principal

router = DefaultRouter()
router.register(r'unidades', UnidadViewSet, basename='unidades')

urlpatterns = [
    path('', mapa_principal, name='mapa'),
    path('api/unidades_mapa/', unidades_con_ubicacion, name='unidades_mapa'),
    path('api/', include(router.urls)),
]
