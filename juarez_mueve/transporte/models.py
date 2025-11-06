from django.db import models

class Ruta(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre


class Unidad(models.Model):
    TIPO_CHOICES = [
        ('transporte', 'Transporte Público'),
        ('basura', 'Recolección de Basura'),
    ]

    identificador = models.CharField(max_length=50, unique=True)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    ruta = models.ForeignKey(Ruta, on_delete=models.SET_NULL, null=True, blank=True) # transporte puede tener ruta, basura no necesariamente

    def __str__(self):
        return f"{self.identificador} ({self.tipo})"


class UbicacionTiempoReal(models.Model):
    unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE, related_name="ubicaciones")
    latitud = models.FloatField()
    longitud = models.FloatField()
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.unidad.identificador} - {self.timestamp}"
