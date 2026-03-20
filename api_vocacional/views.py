from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import Count  # Añadida esta línea
from django.contrib.auth.decorators import login_required
from .models import Pregunta, EvaluacionVocacional, RespuestaEvaluacion, CategoriaVocacional, Carrera, RecomendacionCarrera


# ─── INICIO ───────────────────────────────────────────────────────────────────

def landing(request):
    return render(request, 'vocacional/landing.html', {})


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
    from django.contrib.auth.models import User
    total_evaluaciones = EvaluacionVocacional.objects.count()
    total_usuarios = User.objects.count()
    total_completadas = EvaluacionVocacional.objects.filter(estado='completada').count()
    datos = RespuestaEvaluacion.objects.values('pregunta__categoria__nombre').annotate(total=Count('id'))
    labels = [d['pregunta__categoria__nombre'] for d in datos]
    values = [d['total'] for d in datos]
    categoria_top = labels[0] if labels else '—'
    ultimas = EvaluacionVocacional.objects.filter(estado='completada').select_related('usuario').order_by('-completado_en')[:5]
    return render(request, 'vocacional/dashboard.html', {
        'labels': labels,
        'values': values,
        'total_evaluaciones': total_evaluaciones,
        'total_usuarios': total_usuarios,
        'total_completadas': total_completadas,
        'categoria_top': categoria_top,
        'ultimas': ultimas,
    })

# ─── AUTENTICACIÓN ────────────────────────────────────────────────────────────

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('login')


# ─── ADMIN PANEL ──────────────────────────────────────────────────────────────

@login_required
def admin_panel(request):
    from django.contrib.auth.models import User
    usuarios = User.objects.prefetch_related(
        'evaluaciones__recomendaciones_carrera__carrera',
        'evaluaciones__recomendaciones_programa__programa',
    ).all()
    data = []
    for u in usuarios:
        eval_completada = u.evaluaciones.filter(estado='completada').first()
        carrera = None
        programa = None
        if eval_completada:
            rec_carrera = eval_completada.recomendaciones_carrera.first()
            rec_programa = eval_completada.recomendaciones_programa.first()
            carrera = rec_carrera.carrera.nombre if rec_carrera else None
            programa = rec_programa.programa.nombre_programa if rec_programa else None
        data.append({
            'id': u.id,
            'username': u.username,
            'nombre': u.first_name or '—',
            'apellido': u.last_name or '—',
            'carrera': carrera or '—',
            'programa': programa or '—',
            'fecha': u.date_joined.strftime('%d/%m/%Y'),
        })
    return render(request, 'vocacional/admin_panel.html', {'usuarios': data})


def admin_eliminar_usuario(request, user_id):
    from django.contrib.auth.models import User
    if request.method == 'POST':
        User.objects.filter(id=user_id).delete()
    return redirect('admin_panel')


def admin_editar_usuario(request, user_id):
    from django.contrib.auth.models import User
    u = get_object_or_404(User, id=user_id)
    error = None
    if request.method == 'POST':
        u.first_name = request.POST.get('nombre', '')
        u.last_name = request.POST.get('apellido', '')
        u.save()
        return redirect('admin_panel')
    return render(request, 'vocacional/admin_editar.html', {'u': u})
