from django.conf import settings
from django.db import models
from django.utils import timezone


class Pregunta(models.Model):
    """Pregunta de la evaluación vocacional"""
    texto = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"Pregunta #{self.id} - {self.texto[:50]}..."


class Carrera(models.Model):
    """Carrera profesional recomendable"""
    nombre = models.CharField(max_length=200, unique=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class EvaluacionVocacional(models.Model):
    """Instancia de una evaluación realizada por un usuario"""
    estado = models.CharField(
        max_length=20,
        choices=[
            ('iniciada', 'Iniciada'),
            ('en_progreso', 'En progreso'),
            ('completada', 'Completada'),
            ('cancelada', 'Cancelada'),
        ],
        default='iniciada'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='evaluaciones'
    )
    ip_usuario = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    iniciado_en = models.DateTimeField(auto_now_add=True)
    completado_en = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True, help_text="Datos extra: navegador, resolución, etc.")

    class Meta:
        ordering = ['-iniciado_en']

    def __str__(self):
        return f"Evaluación #{self.id} - {self.estado}"

    @property
    def progreso_porcentaje(self):
        """Calcula dinámicamente el progreso de la evaluación"""
        total = Pregunta.objects.filter(activa=True).count()
        if total == 0:
            return 100
        respondidas = self.respuestas.count()
        return round((respondidas / total) * 100)


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

    def __str__(self):
        return f"Respuesta a Pregunta #{self.pregunta_id} en Evaluación #{self.evaluacion_id}"


class PerfilAcademico(models.Model):
    """Perfil académico del usuario"""
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfiles_academicos'
    )
    nivel_educativo = models.CharField(max_length=50)
    institucion = models.CharField(max_length=200, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']
        verbose_name_plural = "Perfiles Académicos"

    def __str__(self):
        return f"Perfil académico de {self.usuario} - {self.nivel_educativo}"


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


class RecomendacionPrograma(models.Model):
    """Recomendación de programa estatal generada por una evaluación"""
    evaluacion = models.ForeignKey(
        EvaluacionVocacional,
        on_delete=models.CASCADE,
        related_name='recomendaciones_programa'
    )
    programa = models.ForeignKey(
        ProgramaEstatal,
        on_delete=models.PROTECT,
        related_name='recomendaciones'
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['evaluacion', 'programa']

    def __str__(self):
        return f"Programa: {self.programa} para Evaluación #{self.evaluacion_id}"
