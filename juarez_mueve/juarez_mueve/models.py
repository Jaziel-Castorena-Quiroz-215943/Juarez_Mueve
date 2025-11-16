from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ===============================================================
# EMPRESAS
# ===============================================================
class Empresa(models.Model):
    TIPO_CHOICES = [
        ('universidad', 'Universidad'),
        ('gobierno', 'Gobierno'),
        ('maquiladora', 'Maquiladora'),
        ('privado', 'Privado'),
        ('otro', 'Otro'),
    ]

    nombre = models.CharField(max_length=150, unique=True)
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, default='otro')
    correo_contacto = models.EmailField(blank=True, null=True)
    telefono_contacto = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    sitio_web = models.URLField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


# ===============================================================
# PERFIL UNIFICADO
# ===============================================================
class Profile(models.Model):
    ROLES = [
        ('APP_ADMIN', 'Administrador General'),
        ('EMPRESA_ADMIN', 'Administrador de Empresa'),
        ('COORDINADOR_TRANSPORTE', 'Coordinador de Transporte'),
        ('COORDINADOR_BASURA', 'Coordinador de Basura'),
        ('CONDUCTOR', 'Conductor de Transporte'),
        ('RECOLECTOR', 'Personal de Basura'),
        ('CIUDADANO', 'Ciudadano'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    edad = models.PositiveIntegerField(blank=True, null=True)
    genero = models.CharField(
        max_length=20,
        choices=[('Hombre','Hombre'),('Mujer','Mujer'),('Otro','Otro'),('Prefiero no decir','Prefiero no decir')],
        blank=True, null=True
    )
    colonia = models.CharField(max_length=100, blank=True, null=True)
    rol = models.CharField(max_length=40, choices=ROLES, default='CIUDADANO')
    empresa = models.ForeignKey(Empresa, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.user.username} ({self.rol})"


# ===============================================================
# AUTO-CREAR PERFIL
# ===============================================================
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# ===============================================================
# RUTAS
# ===============================================================
class Ruta(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre


# ===============================================================
# CONDUCTORES
# ===============================================================
class Conductor(models.Model):
    nombre = models.CharField(max_length=100)
    licencia = models.CharField(max_length=50)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre


# ===============================================================
# CAMIONES
# ===============================================================
class Camion(models.Model):
    TIPO_CHOICES = [('transporte','Transporte'), ('basura','Basura')]

    identificador = models.CharField(max_length=50)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    ruta = models.ForeignKey(Ruta, on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.identificador


# ===============================================================
# UNIDADES
# ===============================================================
class Unidad(models.Model):
    TIPO_CHOICES = [('transporte','Transporte'), ('basura','Basura')]

    identificador = models.CharField(max_length=50)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    ruta = models.ForeignKey(Ruta, on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.identificador
