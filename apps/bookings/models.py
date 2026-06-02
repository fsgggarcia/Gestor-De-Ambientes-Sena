from django.db import models
from django.contrib.auth.models import User
from apps.infrastructure.models import Ambiente

class Reserva(models.Model):
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)
    instructor = models.CharField(max_length=150)
    materia = models.CharField(max_length=150)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    jornada = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ambiente.nombre} - {self.instructor}"