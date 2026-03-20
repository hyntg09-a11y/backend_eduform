from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('inicio/', views.inicio, name='inicio'),
    path('evaluacion/nueva/', views.crear_evaluacion, name='crear_evaluacion'),
    path('evaluacion/<int:evaluacion_id>/pregunta/<int:pregunta_num>/', views.responder_pregunta, name='responder_pregunta'),
    path('evaluacion/<int:evaluacion_id>/resultado/', views.resultado, name='resultado'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/eliminar/<int:user_id>/', views.admin_eliminar_usuario, name='admin_eliminar_usuario'),
]
