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
