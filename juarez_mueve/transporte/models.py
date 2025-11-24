from django.db import models
from django.contrib.auth.models import User
from juarez_mueve.models import Empresa



class Ruta(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    origen = models.CharField(max_length=255, null=True, blank=True)
    destino = models.CharField(max_length=255, null=True, blank=True)

    origen_lat = models.FloatField(null=True, blank=True)
    origen_lng = models.FloatField(null=True, blank=True)
    destino_lat = models.FloatField(null=True, blank=True)
    destino_lng = models.FloatField(null=True, blank=True)

    color = models.CharField(max_length=7, default="#2563eb")

    def __str__(self):
        return self.nombre


class PuntoRuta(models.Model):
    ruta = models.ForeignKey(
        Ruta,
        on_delete=models.CASCADE,
        related_name="puntos"
    )
    orden = models.PositiveIntegerField(help_text="Orden del punto en la ruta")
    latitud = models.FloatField()
    longitud = models.FloatField()

    class Meta:
        ordering = ["orden"] 

    def __str__(self):
        return f"{self.ruta.nombre} #{self.orden}"

class Camion(models.Model):
    TIPO_CHOICES = [
        ('transporte', 'Transporte público'),
        ('basura', 'Recolección de basura'),
    ]

    identificador = models.CharField(max_length=50, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    ruta = models.ForeignKey(Ruta, on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.identificador


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
        
class Queja(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    unidad = models.ForeignKey(
        Unidad,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Unidad relacionada con la queja (si aplica)."
    )

    ruta = models.ForeignKey(
        Ruta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Queja #{self.id} - {self.usuario}"