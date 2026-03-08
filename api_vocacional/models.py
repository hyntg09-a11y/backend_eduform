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


class Carrera(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    perfil_vocacional = models.ForeignKey(CategoriaVocacional, on_delete=models.PROTECT, related_name='carreras')
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
