from rest_framework import viewsets, status, mixins
from .services import calculate_progress, get_results
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from .models import Pregunta, EvaluacionVocacional, RespuestaEvaluacion
from .serializers import (
    PreguntaSerializer, 
    EvaluacionSerializer, 
    EvaluacionResultadoSerializer,
    RespuestaCreateSerializer
)



class PreguntaViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """ViewSet solo para listar preguntas activas (dinámico con filtros)"""
    queryset = Pregunta.objects.filter(activa=True).select_related('categoria')
    serializer_class = PreguntaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Permite filtrar dinámicamente por categoría, orden, etc."""
        queryset = self.queryset
        categoria_id = self.request.query_params.get('categoria')
        tipo = self.request.query_params.get('tipo')
        
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        if tipo:
            queryset = queryset.filter(tipo_respuesta=tipo)
            
        return queryset.order_by('orden', 'id')

    def list(self, request, *args, **kwargs):
        """Override para añadir metadata útil al frontend"""
        response = super().list(request, *args, **kwargs)
        response.data['metadata'] = {
            'total': self.get_queryset().count(),
            'timestamp': timezone.now().isoformat(),
            'version_api': '1.0'
        }
        return response


class EvaluacionViewSet(viewsets.ModelViewSet):
    """ViewSet principal para gestionar evaluaciones"""
    queryset = EvaluacionVocacional.objects.all()
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post', 'head']  # Solo métodos necesarios

    def get_serializer_class(self):
        """Serializer dinámico según la acción"""
        if self.action == 'resultado':
            return EvaluacionResultadoSerializer
        return EvaluacionSerializer

    def create(self, request, *args, **kwargs):
        """Crear nueva evaluación con metadata dinámica"""
        with transaction.atomic():
            evaluacion = EvaluacionVocacional.objects.create(
                estado='en_progreso',
                ip_usuario=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                metadata={
                    'referer': request.META.get('HTTP_REFERER'),
                    'accept_language': request.META.get('HTTP_ACCEPT_LANGUAGE'),
                }
            )
            
        serializer = self.get_serializer(evaluacion)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='responder')
    def responder(self, request, pk=None):
        """Endpoint dinámico para registrar una respuesta"""
        evaluacion = self.get_object()
        
        if evaluacion.estado == 'completada':
            return Response(
                {'error': 'evaluacion_ya_completada'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RespuestaCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Evitar respuestas duplicadas
            with transaction.atomic():
                RespuestaEvaluacion.objects.filter(
                    evaluacion=evaluacion, 
                    pregunta_id=serializer.validated_data['pregunta'].id
                ).delete()
                
                respuesta = RespuestaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    **serializer.validated_data
                )
                
            # Actualizar estado si completó todas las preguntas
            total = Pregunta.objects.filter(activa=True).count()
            if evaluacion.respuestas.count() >= total:
                evaluacion.estado = 'completada'
                evaluacion.completado_en = timezone.now()
                evaluacion.save(update_fields=['estado', 'completado_en'])
            
            progreso = calculate_progress(evaluacion)
            return Response(
                {
                    'mensaje': 'respuesta_registrada',
                    'progreso': progreso,
                    'completada': evaluacion.estado == 'completada'
                },
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='resultado')
    def resultado(self, request, pk=None):
        """Obtener resultados con cálculos dinámicos"""
        evaluacion = self.get_object()
        
        if evaluacion.estado != 'completada':
            return Response(
                {'error': 'evaluacion_no_completada', 'progreso': calculate_progress(evaluacion)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = get_results(evaluacion)
        return Response(results)

    @staticmethod
    def _get_client_ip(request):
        """Obtener IP real del cliente (soporta proxies)"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
