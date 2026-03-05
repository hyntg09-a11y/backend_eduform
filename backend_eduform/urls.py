from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

def api_root(request):
    """Endpoint raíz con documentación dinámica"""
    return JsonResponse({
        'api_name': 'EduForm Vocational API',
        'version': '1.0',
        'endpoints': {
            'preguntas': '/api/preguntas',
            'evaluaciones': {
                'crear': 'POST /api/evaluaciones',
                'responder': 'POST /api/evaluaciones/{id}/responder',
                'resultado': 'GET /api/evaluaciones/{id}/resultado'
            }
        },
        'docs': 'Consulta README_API.md para más detalles'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root),  # Root de la API
    path('api/', include('api_vocacional.urls')),
]
