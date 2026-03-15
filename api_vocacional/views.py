from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import Count  # Añadida esta línea
from django.contrib.auth.decorators import login_required
from .models import Pregunta, EvaluacionVocacional, RespuestaEvaluacion, CategoriaVocacional, Carrera, RecomendacionCarrera


# ─── INICIO ───────────────────────────────────────────────────────────────────

@login_required
def inicio(request):
    """Página de bienvenida con estadísticas"""
    total_preguntas = Pregunta.objects.filter(activa=True).count()
    total_categorias = CategoriaVocacional.objects.filter(activa=True).count()
    return render(request, 'vocacional/inicio.html', {
        'total_preguntas': total_preguntas,
        'total_categorias': total_categorias,
    })


# ─── EVALUACIÓN ───────────────────────────────────────────────────────────────

@login_required
def crear_evaluacion(request):
    """Crea una nueva evaluación y redirige a la primera pregunta"""
    if request.method == 'POST':
        evaluacion = EvaluacionVocacional.objects.create(
            estado='en_progreso',
            ip_usuario=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
        )
        # Guardamos el id en sesión para recuperarlo siempre
        request.session['evaluacion_id'] = evaluacion.id
        return redirect('responder_pregunta', evaluacion_id=evaluacion.id, pregunta_num=1)

    return redirect('inicio')


@login_required
def responder_pregunta(request, evaluacion_id, pregunta_num):
    """Muestra y procesa una pregunta a la vez"""
    evaluacion = get_object_or_404(EvaluacionVocacional, id=evaluacion_id)
    preguntas = list(Pregunta.objects.filter(activa=True).select_related('categoria').order_by('orden', 'id'))
    total = len(preguntas)

    # Validar número de pregunta
    if pregunta_num < 1 or pregunta_num > total:
        return redirect('resultado', evaluacion_id=evaluacion_id)

    pregunta_actual = preguntas[pregunta_num - 1]
    progreso = round((evaluacion.respuestas.count() / total) * 100) if total > 0 else 0

    if request.method == 'POST':
        valor = request.POST.get('respuesta')
        if valor:
            with transaction.atomic():
                # Permite re-responder (elimina si ya existe)
                RespuestaEvaluacion.objects.filter(
                    evaluacion=evaluacion,
                    pregunta=pregunta_actual
                ).delete()
                RespuestaEvaluacion.objects.create(
                    evaluacion=evaluacion,
                    pregunta=pregunta_actual,
                    valor_respuesta=valor,
                )

            # Si es la última pregunta → completar
            if pregunta_num >= total:
                evaluacion.estado = 'completada'
                evaluacion.completado_en = timezone.now()
                evaluacion.save(update_fields=['estado', 'completado_en'])
                return redirect('resultado', evaluacion_id=evaluacion_id)

            return redirect('responder_pregunta',
                            evaluacion_id=evaluacion_id,
                            pregunta_num=pregunta_num + 1)

    # Respuesta previa si existe (para mostrar seleccionada)
    respuesta_previa = RespuestaEvaluacion.objects.filter(
        evaluacion=evaluacion, pregunta=pregunta_actual
    ).first()

    return render(request, 'vocacional/pregunta.html', {
        'evaluacion': evaluacion,
        'pregunta': pregunta_actual,
        'pregunta_num': pregunta_num,
        'total': total,
        'progreso': progreso,
        'opciones': pregunta_actual.get_opciones_dict(),
        'respuesta_previa': respuesta_previa.valor_respuesta if respuesta_previa else None,
        'puede_volver': pregunta_num > 1,
        'pregunta_anterior': pregunta_num - 1,
    })


@login_required
def resultado(request, evaluacion_id):
    """Muestra los resultados finales de la evaluación"""
    evaluacion = get_object_or_404(EvaluacionVocacional, id=evaluacion_id)

    if evaluacion.estado != 'completada':
        total = Pregunta.objects.filter(activa=True).count()
        respondidas = evaluacion.respuestas.count()
        siguiente = respondidas + 1
        return redirect('responder_pregunta',
                        evaluacion_id=evaluacion_id,
                        pregunta_num=siguiente)

    resultados = evaluacion.calcular_resultados()

    for r in resultados:
        carrera = Carrera.objects.filter(perfil_vocacional_id=r['categoria_id'], activa=True).first()
        if carrera:
            RecomendacionCarrera.objects.get_or_create(
                evaluacion=evaluacion,
                carrera=carrera,
                defaults={'puntaje': r['porcentaje']}
            )

    # El primero es el de mayor porcentaje (ya vienen ordenados)
    categoria_principal = resultados[0] if resultados else None

    return render(request, 'vocacional/resultado.html', {
        'evaluacion': evaluacion,
        'resultados': resultados,
        'categoria_principal': categoria_principal,
    })


# ─── HELPER ───────────────────────────────────────────────────────────────────

def _get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')                                                                     
# ─── AUTENTICACIÓN ────────────────────────────────────────────────────────────

def registro(request):
    from django.contrib.auth.models import User
    from django.contrib.auth import login
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            error = 'El usuario ya existe'
        elif username and password:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('inicio')
    return render(request, 'vocacional/registro.html', {'error': error})


def login_view(request):
    from django.contrib.auth import authenticate, login
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('inicio')
        error = 'Usuario o contraseña incorrectos'
    return render(request, 'vocacional/login.html', {'error': error})

# ─── DASHBOARD ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    from django.db.models import Count
    total_evaluaciones = EvaluacionVocacional.objects.count()
    datos = RespuestaEvaluacion.objects.values('pregunta__categoria__nombre').annotate(total=Count('id'))
    labels = [d['pregunta__categoria__nombre'] for d in datos]
    values = [d['total'] for d in datos]
    return render(request, 'vocacional/dashboard.html', {
        'labels': labels,
        'values': values,
        'total_evaluaciones': total_evaluaciones,
    })
