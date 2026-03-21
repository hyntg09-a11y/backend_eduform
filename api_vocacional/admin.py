from django.contrib import admin
from .models import CategoriaVocacional, Pregunta, EvaluacionVocacional, RespuestaEvaluacion, Carrera, ProgramaEstatal, RecomendacionCarrera, RecomendacionPrograma, PerfilAcademico, FactoresSocioeconomicos

# Register your models here.

class CategoriaVocacionalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'color_hex', 'activa')

admin.site.register(CategoriaVocacional, CategoriaVocacionalAdmin)

class PreguntaAdmin(admin.ModelAdmin):
    list_display = ('texto', 'categoria', 'activa')
    list_filter = ('categoria', 'activa')

admin.site.register(Pregunta, PreguntaAdmin)

admin.site.register(EvaluacionVocacional)
admin.site.register(RespuestaEvaluacion)
admin.site.register(Carrera)
admin.site.register(ProgramaEstatal)
admin.site.register(RecomendacionCarrera)
admin.site.register(RecomendacionPrograma)
admin.site.register(PerfilAcademico)
admin.site.register(FactoresSocioeconomicos)
