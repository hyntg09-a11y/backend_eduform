from .models import EvaluacionVocacional, RespuestaEvaluacion
from .utils import calcular_afinidad_categoria


def calculate_progress(evaluacion):
    total = EvaluacionVocacional.objects.filter(activa=True).count()
    return (evaluacion.respuestas.count() / total) * 100 if total > 0 else 0


def get_results(evaluacion):
    # Lógica para calcular resultados
    pass
