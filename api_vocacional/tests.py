from rest_framework.test import APITestCase
from rest_framework import status
from api_vocacional.models import CategoriaVocacional, Pregunta

class PreguntaViewSetTests(APITestCase):
    def setUp(self):
        self.categoria = CategoriaVocacional.objects.create(nombre="Tecnología", orden=1)
        self.pregunta = Pregunta.objects.create(
            texto="¿Cuál es tu nivel de conocimiento en Python?",
            categoria=self.categoria,
            tipo_respuesta='boolean',
            activa=True
        )

    def test_list_preguntas(self):
        response = self.client.get('/api/preguntas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class EvaluacionViewSetTests(APITestCase):
    def test_crear_evaluacion(self):
        data = {
            "estado": "iniciada",
            "ip_usuario": "127.0.0.1",
            "user_agent": "Mozilla/5.0"
        }
        response = self.client.post('/api/evaluaciones/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
