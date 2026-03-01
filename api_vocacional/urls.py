from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PreguntaViewSet, EvaluacionViewSet

router = DefaultRouter(trailing_slash=False)  # URLs más limpias
router.register(r'preguntas', PreguntaViewSet, basename='pregunta')
router.register(r'evaluaciones', EvaluacionViewSet, basename='evaluacion')

urlpatterns = [
    path('', include(router.urls)),
]