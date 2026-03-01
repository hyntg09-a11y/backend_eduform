from django.db import transaction
from .models import Pregunta, EvaluacionVocacional, RespuestaEvaluacion
from .serializers import EvaluacionResultadoSerializer

def calculate_progress(evaluacion):
    total_preguntas = Pregunta.objects.filter(activa=True).count()
    preguntas_respondidas = evaluacion.respuestas.count()
    return (preguntas_respondidas / total_preguntas) * 100 if total_preguntas > 0 else 0

def get_results(evaluacion):
    evaluacion.calcular_resultados()
    return EvaluacionResultadoSerializer(evaluacion).data
