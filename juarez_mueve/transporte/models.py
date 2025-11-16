from django.db import models
from django.contrib.auth.models import User
from juarez_mueve.models import Empresa


class Ruta(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='rutas_transporte',
        null=True,
        blank=True
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Unidad(models.Model):
    TIPO_CHOICES = [
        ('transporte', 'Transporte Público'),
        ('basura', 'Recolección de Basura'),
    ]

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='unidades',
        null=True,
        blank=True
    )

    identificador = models.CharField(max_length=50, unique=True)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    ruta = models.ForeignKey(Ruta, on_delete=models.SET_NULL, null=True, blank=True)

    # quién conduce esta unidad
    conductor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='unidades_que_conduce'
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.identificador} ({self.tipo})"


class UbicacionTiempoReal(models.Model):
    unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE, related_name="ubicaciones")
    latitud = models.FloatField()
    longitud = models.FloatField()
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.unidad.identificador} - {self.timestamp}"
