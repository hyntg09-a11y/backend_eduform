from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Pregunta, EvaluacionVocacional, RespuestaEvaluacion
from .services import calculate_progress, get_results


def inicio(request):
    preguntas = Pregunta.objects.filter(activa=True).order_by('orden', 'id')
    return render(request, 'inicio.html', {'preguntas': preguntas})


def crear_evaluacion(request):
    if request.method == 'POST':
        evaluacion = EvaluacionVocacional.objects.create(
            estado='en_progreso',
            ip_usuario=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
            metadata={
                'referer': request.META.get('HTTP_REFERER'),
                'accept_language': request.META.get('HTTP_ACCEPT_LANGUAGE'),
            }
        )
        return redirect('responder_pregunta', pk=evaluacion.id)
    return HttpResponse("Método no permitido", status=405)


def responder_pregunta(request, pk):
    evaluacion = EvaluacionVocacional.objects.get(id=pk)
    if request.method == 'POST':
        pregunta_id = request.POST.get('pregunta_id')
        valor_respuesta = request.POST.get('valor_respuesta')
        tiempo_respuesta_ms = request.POST.get('tiempo_respuesta_ms')

        pregunta = Pregunta.objects.get(id=pregunta_id)
        RespuestaEvaluacion.objects.create(
            evaluacion=evaluacion,
            pregunta=pregunta,
            valor_respuesta=valor_respuesta,
            tiempo_respuesta_ms=tiempo_respuesta_ms
        )

        total = Pregunta.objects.filter(activa=True).count()
        if evaluacion.respuestas.count() >= total:
            evaluacion.estado = 'completada'
            evaluacion.completado_en = timezone.now()
            evaluacion.save(update_fields=['estado', 'completado_en'])

        progreso = calculate_progress(evaluacion)
        return render(request, 'resultado.html', {'progreso': progreso, 'completada': evaluacion.estado == 'completada'})

    preguntas = Pregunta.objects.filter(activa=True).order_by('orden', 'id')
    return render(request, 'responder_pregunta.html', {'evaluacion': evaluacion, 'preguntas': preguntas})


def resultado(request, pk):
    evaluacion = EvaluacionVocacional.objects.get(id=pk)
    if evaluacion.estado != 'completada':
        return render(request, 'resultado.html', {'error': 'evaluacion_no_completada', 'progreso': calculate_progress(evaluacion)})

    results = get_results(evaluacion)
    return render(request, 'resultado.html', results)
