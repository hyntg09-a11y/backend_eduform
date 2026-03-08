from django.db import models
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
        return self.opciones if isinstance(self.opciones, dict) else {str(i): val for i, val in enumerate(self.opciones)}


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
    ip_usuario = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    iniciado_en = models.DateTimeField(auto_now_add=True)
    completado_en = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True, help_text="Datos extra: navegador, resolución, etc.")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

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

    def calcular_resultados(self):
        """Lógica dinámica para calcular porcentajes por categoría"""
        resultados = {}
        preguntas_respondidas = self.respuestas.select_related('pregunta__categoria')

        # Agrupar respuestas por categoría
        for respuesta in preguntas_respondidas:
            cat = respuesta.pregunta.categoria
            if cat.nombre not in resultados:
                resultados[cat.nombre] = {
                    'categoria_id': cat.id,
                    'nombre': cat.nombre,
                    'puntos': 0,
                    'peso_total': 0,
                    'color': cat.color_hex,
                }
            
            # Lógica flexible según tipo de respuesta
            if respuesta.pregunta.tipo_respuesta == 'boolean':
                valor = 1 if respuesta.valor_respuesta in ['si', 'true', True] else 0
            elif respuesta.pregunta.tipo_respuesta == 'escala':
                valor = float(respuesta.valor_respuesta) if str(respuesta.valor_respuesta).isdigit() else 0
            else:  # opcion_multiple
                valor = 1  # Se puede personalizar según la opción seleccionada

            resultados[cat.nombre]['puntos'] += valor * respuesta.pregunta.peso_categoria
            resultados[cat.nombre]['peso_total'] += respuesta.pregunta.peso_categoria

        # Normalizar a porcentajes
        for cat_data in resultados.values():
            if cat_data['peso_total'] > 0:
                cat_data['porcentaje'] = round((cat_data['puntos'] / cat_data['peso_total']) * 100)
            else:
                cat_data['porcentaje'] = 0
            del cat_data['puntos']
            del cat_data['peso_total']

        return sorted(resultados.values(), key=lambda x: x['porcentaje'], reverse=True)


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
