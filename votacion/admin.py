from django.contrib import admin
from .models import Ciudadano, Candidato, Voto

@admin.register(Ciudadano)
class CiudadanoAdmin(admin.ModelAdmin):
    list_display = ['nombre_completo', 'cedula', 'ha_votado']
    list_filter = ['ha_votado']
    search_fields = ['nombre_completo', 'cedula']

@admin.register(Candidato)
class CandidatoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'nombre_completo', 'partido_politico', 'votos']
    ordering = ['numero']

@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ['ciudadano', 'candidato', 'fecha_hora']
    list_filter = ['fecha_hora', 'candidato']
