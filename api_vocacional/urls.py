from django.urls import path
from .views import inicio, crear_evaluacion, responder_pregunta, resultado

urlpatterns = [
    path('', inicio, name='inicio'),
    path('evaluaciones/', crear_evaluacion, name='crear_evaluacion'),
    path('evaluaciones/<int:pk>/responder/', responder_pregunta, name='responder_pregunta'),
    path('evaluaciones/<int:pk>/resultado/', resultado, name='resultado'),
]
