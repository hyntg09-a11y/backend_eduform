from django.conf import settings
from django.db import models
from django.utils import timezone


class Pregunta(models.Model):
    """Pregunta de la evaluación vocacional"""
    TIPO_RESPUESTA = [
        ('boolean', 'Sí/No'),
        ('escala', 'Escala 1-5'),
        ('opcion_multiple', 'Opción múltiple'),
    ]

    texto = models.TextField()
    categoria = models.ForeignKey(
        CategoriaVocacional,
        on_delete=models.PROTECT,
        related_name='preguntas'
    )
    tipo_respuesta = models.CharField(max_length=20, choices=TIPO_RESPUESTA, default='boolean')
    opciones = models.JSONField(blank=True, default=list, help_text="Opciones para tipo 'opcion_multiple' o 'escala'")
    peso_categoria = models.FloatField(default=1.0, help_text="Peso de esta pregunta para su categoría")
    orden = models.PositiveSmallIntegerField(default=0)
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', 'id']
        indexes = [models.Index(fields=['categoria', 'activa'])]

    def __str__(self):
        return f"[{self.categoria.nombre}] {self.texto[:50]}..."

    def get_opciones_dict(self):
        """Devuelve opciones en formato amigable para el frontend"""
        if not self.opciones:
            return {'si': 'Me interesa', 'no': 'No me interesa'} if self.tipo_respuesta == 'boolean' else {}
        elif self.tipo_respuesta == 'escala':
            return {str(i): str(i) for i in range(1, 6)}
        else:
            return {option: option for option in self.opciones}


class RespuestaEvaluacion(models.Model):
    """Respuesta individual a una pregunta dentro de una evaluación"""
    evaluacion = models.ForeignKey(
        EvaluacionVocacional,
        on_delete=models.CASCADE,
        related_name='respuestas'
    )
    pregunta = models.ForeignKey(Pregunta, on_delete=models.PROTECT)
    valor_respuesta = models.JSONField(help_text="Puede ser string, número, boolean o objeto")
    tiempo_respuesta_ms = models.PositiveIntegerField(null=True, blank=True, help_text="Tiempo que tardó en responder")
    respondido_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['evaluacion', 'pregunta']
        indexes = [models.Index(fields=['evaluacion', 'pregunta'])]

    def __str__(self):
        return f"Respuesta a Pregunta #{self.pregunta_id} en Evaluación #{self.evaluacion_id}"


class Carrera(models.Model):
    """Carrera académica"""
    nombre = models.CharField(max_length=200)
    nivel_educativo = models.CharField(max_length=50)
    institucion = models.CharField(max_length=200, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class RecomendacionCarrera(models.Model):
    """Recomendación de carrera generada por una evaluación"""
    evaluacion = models.ForeignKey(
        EvaluacionVocacional,
        on_delete=models.CASCADE,
        related_name='recomendaciones_carrera'
    )
    carrera = models.ForeignKey(
        Carrera,
        on_delete=models.PROTECT,
        related_name='recomendaciones'
    )
    puntaje = models.FloatField(default=0.0)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['evaluacion', 'carrera']
        ordering = ['-puntaje']

    def __str__(self):
        return f"Recomendación: {self.carrera} para Evaluación #{self.evaluacion_id}"
