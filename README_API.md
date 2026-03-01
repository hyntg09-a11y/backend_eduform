# 🎓 EduForm API - Documentación para Frontend

## 🔗 URL Base
http://127.0.0.1:8000

---

## 📋 Endpoints

### 1. Obtener preguntas
GET /api/preguntas/

### 2. Crear evaluación
POST /api/evaluaciones/

### 3. Responder pregunta
POST /api/evaluaciones/{id}/responder/
Body: { "pregunta": 1, "respuesta": "si" }

### 4. Ver resultado
GET /api/evaluaciones/{id}/resultado/

---

## 🔄 Flujo completo

1. GET /api/preguntas/ → obtener las 50 preguntas
2. POST /api/evaluaciones/ → crear evaluación, guardar el id
3. POST /api/evaluaciones/{id}/responder/ → enviar cada respuesta
4. GET /api/evaluaciones/{id}/resultado/ → mostrar porcentajes

---

## ✅ Valores válidos para respuesta
- "si" → Me interesa
- "no" → No me interesa

# EduForm Vocational Backend

API Django + DRF para cuestionario vocacional.

## Instalación
```bash
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py shell < scripts/seed.py
python manage.py runserver
