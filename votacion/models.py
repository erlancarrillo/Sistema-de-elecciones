
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Ciudadano(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cedula = models.CharField(max_length=20, unique=True)
    nombre_completo = models.CharField(max_length=200)
    fecha_nacimiento = models.DateField()
    direccion = models.TextField()
    ha_votado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "Ciudadanos"
    
    def __str__(self):
        return f"{self.nombre_completo} - {self.cedula}"

class Candidato(models.Model):
    nombre_completo = models.CharField(max_length=200)
    partido_politico = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='candidatos/', blank=True, null=True)
    propuesta = models.TextField()
    numero = models.IntegerField(unique=True)
    votos = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Candidatos"
        ordering = ['numero']
    
    def __str__(self):
        return f"{self.numero} - {self.nombre_completo} ({self.partido_politico})"

class Voto(models.Model):
    ciudadano = models.ForeignKey(Ciudadano, on_delete=models.CASCADE)
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Votos"
        unique_together = ('ciudadano',)
    
    def __str__(self):
        return f"Voto de {self.ciudadano.nombre_completo} - {self.fecha_hora}"
