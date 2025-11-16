from django.contrib import admin
from django.urls import path, include

from juarez_mueve.views import (
    index,
    login_view,
    signup,
    panel_conductor,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Landing y auth principal
    path("", index, name="index"),
    path("login/", login_view, name="login"),
    path("signup/", signup, name="signup"),

    # Panel del conductor
    path("conductor/panel/", panel_conductor, name="panel_conductor"),

    # Allauth (login/registro social, etc.)
    path("accounts/", include("allauth.urls")),

    # Panel administrativo
    path("panel/", include("panel.urls")),

    # Módulo de transporte (mapa, rutas, etc.)
    path("transporte/", include("transporte.urls")),
]
