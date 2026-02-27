"""
Utilidades para la API vocacional.
Funciones reutilizables, handlers personalizados y helpers.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Handler personalizado para devolver errores consistentes y amigables.
    Útil para que el frontend maneje errores de forma predecible.
    """
    # Primero, dejamos que DRF maneje lo que ya conoce
    response = exception_handler(exc, context)
    
    if response is not None:
        # Estructura uniforme de error
        error_data = {
            'error': True,
            'codigo': response.status_code,
            'mensaje': 'Error en la solicitud',
            'detalles': {}
        }
        
        # Mapear errores específicos de DRF
        if 'non_field_errors' in response.data:
            error_data['detalles'] = {'general': response.data['non_field_errors']}
        elif isinstance(response.data, dict):
            error_data['detalles'] = {
                campo: errores[0] if isinstance(errores, list) else errores 
                for campo, errores in response.data.items()
            }
        
        response.data = error_data
        return response
    
    # Manejar excepciones no capturadas por DRF
    if isinstance(exc, IntegrityError):
        return Response({
            'error': True,
            'codigo': status.HTTP_409_CONFLICT,
            'mensaje': 'Conflicto de datos',
            'detalles': {'general': 'Este registro ya existe o viola una restricción'}
        }, status=status.HTTP_409_CONFLICT)
    
    if isinstance(exc, ObjectDoesNotExist):
        return Response({
            'error': True,
            'codigo': status.HTTP_404_NOT_FOUND,
            'mensaje': 'Recurso no encontrado',
            'detalles': {'general': 'El elemento solicitado no existe'}
        }, status=status.HTTP_404_NOT_FOUND)
    
    if isinstance(exc, ValidationError):
        return Response({
            'error': True,
            'codigo': status.HTTP_400_BAD_REQUEST,
            'mensaje': 'Datos inválidos',
            'detalles': exc.message_dict if hasattr(exc, 'message_dict') else {'general': str(exc)}
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Loggear error inesperado para debugging
    logger.error(f'Error no manejado: {type(exc).__name__} - {str(exc)}', exc_info=True)
    
    # Respuesta genérica para errores 500 (en producción no mostrar detalles)
    return Response({
        'error': True,
        'codigo': status.HTTP_500_INTERNAL_SERVER_ERROR,
        'mensaje': 'Error interno del servidor',
        'detalles': {'general': 'Por favor, intenta más tarde'}
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def calcular_afinidad_categoria(respuestas, categoria_id):
    """
    Calcula el porcentaje de afinidad para una categoría específica.
    Función pura que puede usarse en tests o en otras partes del sistema.
    """
    preguntas_categoria = [r for r in respuestas if r['pregunta__categoria_id'] == categoria_id]
    if not preguntas_categoria:
        return 0
    
    puntos = sum(
        1 if str(r['valor_respuesta']).lower() in ['si', 'true', '1'] else 0 
        for r in preguntas_categoria
    )
    return round((puntos / len(preguntas_categoria)) * 100)


def formatear_respuesta_api(data, metadata=None, success=True):
    """
    Envuelve cualquier respuesta de API con estructura consistente.
    Opcional: usar si quieres estandarizar aún más las respuestas.
    """
    response = {
        'success': success,
        'data': data,
        'timestamp': __import__('django.utils.timezone').utils.timezone.now().isoformat()
    }
    if metadata:
        response['metadata'] = metadata
    return response


def limpiar_input_texto(texto, max_length=500):
    """
    Limpia y sanitiza texto de entrada del usuario.
    Previene XSS básico y normaliza espacios.
    """
    if not texto:
        return ""
    # Eliminar tags HTML básicos
    import re
    texto_limpio = re.sub(r'<[^>]+>', '', str(texto))
    # Normalizar espacios
    texto_limpio = ' '.join(texto_limpio.split())
    # Truncar si es necesario
    return texto_limpio[:max_length].strip()