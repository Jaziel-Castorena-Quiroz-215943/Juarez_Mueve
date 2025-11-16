from django.db import models


class ZonaBasura(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    horario_inicio = models.TimeField()
    horario_fin = models.TimeField()
    colonias = models.TextField(help_text="Colonias cubiertas en esta zona")

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


class UnidadBasura(models.Model):
    zona = models.ForeignKey(ZonaBasura, on_delete=models.CASCADE, related_name="unidades")
    identificador = models.CharField(max_length=50, unique=True)
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.identificador


class UnidadRecoleccion(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('FUERA_SERV', 'Fuera de servicio'),
    ]

    nombre = models.CharField(max_length=100)
    codigo_unidad = models.CharField(max_length=20, unique=True)
    zona = models.CharField(max_length=100, blank=True)
    latitud = models.FloatField()
    longitud = models.FloatField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.codigo_unidad} - {self.zona or self.nombre}"
