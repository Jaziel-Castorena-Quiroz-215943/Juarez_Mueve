from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Empresa(models.Model):
    TIPO_CHOICES = [
        ('TRANSPORTE', 'Transporte'),
        ('BASURA', 'Recolección de basura'),
        ('MIXTA', 'Mixta'),
    ]

    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, default='MIXTA')
    correo_contacto = models.EmailField(blank=True, null=True)
    telefono_contacto = models.CharField(max_length=20, blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Profile(models.Model):
    ROL_CHOICES = [
        ('CIUDADANO', 'Ciudadano'),
        ('CONDUCTOR', 'Conductor'),
        ('COORDINADOR', 'Coordinador de empresa'),
        ('EMPRESA_ADMIN', 'Administrador de empresa'),
        ('APP_ADMIN', 'Administrador general'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    edad = models.PositiveIntegerField(blank=True, null=True)
    genero = models.CharField(
        max_length=20,
        choices=[
            ('Hombre', 'Hombre'),
            ('Mujer', 'Mujer'),
            ('Otro', 'Otro'),
            ('Prefiero no decir', 'Prefiero no decir'),
        ],
        blank=True,
        null=True
    )
    colonia = models.CharField(max_length=100, blank=True, null=True)

    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='CIUDADANO')

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfiles'
    )

    def __str__(self):
        return self.user.first_name or self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
