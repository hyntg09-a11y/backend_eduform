from django.conf import settings
from django.db import models
from django.utils import timezone


class CategoriaVocacional(models.Model):
    """Categoría de orientación vocacional (ej: Tecnología, Salud, Arte)"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    color_hex = models.CharField(max_length=7, default='#3498db', help_text="Color para visualización")
    orden = models.PositiveSmallIntegerField(default=0)
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name_plural = "Categorías Vocacionales"

    def __str__(self):
        return self.nombre

    def to_dict(self):
        """Método útil para respuestas rápidas sin serializer"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'color': self.color_hex,
        }


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
    respondido_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-respondido_en']

    def __str__(self):
        return f"Pregunta #{self.id} - {self.texto}"


class EvaluacionVocacional(models.Model):
    """Evaluación del usuario"""
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


class PerfilAcademico(models.Model):
    """Perfil académico del usuario"""
    evaluacion = models.ForeignKey(
        EvaluacionVocacional,
        on_delete=models.CASCADE,
        related_name='perfiles_academicos',
        null=True,
        blank=True
    )
    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name='perfiles_academicos',
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-evaluacion__iniciado_en']
        verbose_name_plural = "Perfiles Académicos"

    def __str__(self):
        return f"Perfil académico para Evaluación #{self.evaluacion_id} - Pregunta #{self.pregunta_id}"
