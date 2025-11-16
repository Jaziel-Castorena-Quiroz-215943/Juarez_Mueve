from django.contrib import admin
from .models import Empresa, Profile


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'correo_contacto', 'telefono_contacto', 'activo')
    list_filter = ('tipo', 'activo')
    search_fields = ('nombre',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol', 'empresa', 'telefono', 'colonia')
    list_filter = ('rol', 'empresa')
    search_fields = (
        'user__username', 'user__email',
        'user__first_name', 'user__last_name'
    )
