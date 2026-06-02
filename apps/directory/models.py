from django.db import models

class Instructor(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    materia = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre