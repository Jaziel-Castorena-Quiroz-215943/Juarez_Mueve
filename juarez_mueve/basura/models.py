from django.db import models
from django.contrib.auth.models import User
from juarez_mueve.models import Empresa


class ZonaBasura(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='zonas_basura',
        null=True,
        blank=True
    )

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

    # conductor asignado
    conductor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='unidades_basura_que_conduce'
    )

    def __str__(self):
        return self.identificador
