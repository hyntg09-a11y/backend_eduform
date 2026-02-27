#!/usr/bin/env python
"""
Script para poblar la BD con 50 preguntas vocacionales reales.
Ejecutar: python manage.py shell < scripts/seed.py
"""
import os, sys, django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_eduform.settings')
django.setup()

from api_vocacional.models import CategoriaVocacional, Pregunta

def crear_categorias():
    """Crea categorías base si no existen"""
    categorias_data = [
        {'nombre': 'Tecnología e Informática', 'color_hex': '#3498db', 'orden': 1},
        {'nombre': 'Salud y Bienestar', 'color_hex': '#e74c3c', 'orden': 2},
        {'nombre': 'Arte y Diseño', 'color_hex': '#9b59b6', 'orden': 3},
        {'nombre': 'Negocios y Administración', 'color_hex': '#2ecc71', 'orden': 4},
        {'nombre': 'Ciencias e Investigación', 'color_hex': '#f39c12', 'orden': 5},
        {'nombre': 'Educación y Sociales', 'color_hex': '#1abc9c', 'orden': 6},
    ]
    
    categorias = {}
    for cat_data in categorias_data:
        cat, _ = CategoriaVocacional.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults={k: v for k, v in cat_data.items() if k != 'nombre'}
        )
        categorias[cat.nombre] = cat
        print(f"✓ Categoría: {cat.nombre}")
    
    return categorias


def crear_preguntas(categorias):
    """Crea 50 preguntas distribuidas dinámicamente"""
    preguntas_data = [
        # Tecnología (8 preguntas)
        ("¿Te gusta resolver problemas lógicos o de programación?", "Tecnología e Informática"),
        ("¿Disfrutas aprendiendo sobre nuevas tecnologías y gadgets?", "Tecnología e Informática"),
        ("¿Te interesaría crear aplicaciones o sitios web?", "Tecnología e Informática"),
        ("¿Te sientes cómodo trabajando con datos y análisis?", "Tecnología e Informática"),
        ("¿Te atrae la idea de trabajar en ciberseguridad?", "Tecnología e Informática"),
        ("¿Te gustaría automatizar tareas mediante código?", "Tecnología e Informática"),
        ("¿Te interesa el desarrollo de videojuegos?", "Tecnología e Informática"),
        ("¿Disfrutas configurando o reparando equipos tecnológicos?", "Tecnología e Informática"),
        
        # Salud (8 preguntas)
        ("¿Te interesa ayudar a las personas a mejorar su salud?", "Salud y Bienestar"),
        ("¿Te sientes cómodo en entornos médicos o clínicos?", "Salud y Bienestar"),
        ("¿Te gustaría investigar sobre enfermedades y tratamientos?", "Salud y Bienestar"),
        ("¿Te interesa la nutrición y el bienestar físico?", "Salud y Bienestar"),
        ("¿Te atrae la psicología y el comportamiento humano?", "Salud y Bienestar"),
        ("¿Te gustaría trabajar en emergencias médicas?", "Salud y Bienestar"),
        ("¿Te interesa la salud pública y prevención?", "Salud y Bienestar"),
        ("¿Te ves trabajando en laboratorios de análisis?", "Salud y Bienestar"),
        
        # Arte (8 preguntas)
        ("¿Te gusta expresar ideas mediante dibujos o diseños?", "Arte y Diseño"),
        ("¿Disfrutas creando contenido visual o audiovisual?", "Arte y Diseño"),
        ("¿Te interesa la fotografía, el cine o la edición?", "Arte y Diseño"),
        ("¿Te atrae el diseño de moda, interiores o productos?", "Arte y Diseño"),
        ("¿Te gusta escribir historias, guiones o poesía?", "Arte y Diseño"),
        ("¿Te interesa la música o la producción sonora?", "Arte y Diseño"),
        ("¿Disfrutas trabajando con colores y composición?", "Arte y Diseño"),
        ("¿Te gustaría crear experiencias interactivas o UX?", "Arte y Diseño"),
        
        # Negocios (9 preguntas)
        ("¿Te gusta liderar equipos o proyectos?", "Negocios y Administración"),
        ("¿Te interesa el mundo de las finanzas y la inversión?", "Negocios y Administración"),
        ("¿Disfrutas analizando mercados y oportunidades comerciales?", "Negocios y Administración"),
        ("¿Te atrae el emprendimiento y crear tu propio negocio?", "Negocios y Administración"),
        ("¿Te interesa la gestión de recursos humanos?", "Negocios y Administración"),
        ("¿Te gusta negociar y cerrar acuerdos?", "Negocios y Administración"),
        ("¿Te interesa el marketing digital y las redes sociales?", "Negocios y Administración"),
        ("¿Te ves trabajando en logística o cadena de suministro?", "Negocios y Administración"),
        ("¿Te interesa la consultoría estratégica?", "Negocios y Administración"),
        
        # Ciencias (9 preguntas)
        ("¿Te gusta experimentar y comprobar hipótesis?", "Ciencias e Investigación"),
        ("¿Te interesa la biología, química o física?", "Ciencias e Investigación"),
        ("¿Disfrutas investigando sobre el medio ambiente?", "Ciencias e Investigación"),
        ("¿Te atrae la astronomía o las ciencias espaciales?", "Ciencias e Investigación"),
        ("¿Te interesa la genética o la biotecnología?", "Ciencias e Investigación"),
        ("¿Te gustaría trabajar en conservación de especies?", "Ciencias e Investigación"),
        ("¿Te interesa la ciencia de materiales o nanotecnología?", "Ciencias e Investigación"),
        ("¿Disfrutas analizando datos científicos complejos?", "Ciencias e Investigación"),
        ("¿Te atrae la investigación académica o universitaria?", "Ciencias e Investigación"),
        
        # Educación (8 preguntas)
        ("¿Te gusta enseñar o explicar conceptos a otros?", "Educación y Sociales"),
        ("¿Te interesa el desarrollo infantil o adolescente?", "Educación y Sociales"),
        ("¿Disfrutas trabajando en comunidades o proyectos sociales?", "Educación y Sociales"),
        ("¿Te atrae la psicología educativa o orientación?", "Educación y Sociales"),
        ("¿Te interesa la creación de contenidos educativos?", "Educación y Sociales"),
        ("¿Te gustaría trabajar en políticas públicas o gobierno?", "Educación y Sociales"),
        ("¿Te interesa la sociología o antropología?", "Educación y Sociales"),
        ("¿Te ves mediando conflictos o facilitando diálogos?", "Educación y Sociales"),
    ]

    creadas = 0
    for texto, categoria_nombre in preguntas_data:
        cat = categorias.get(categoria_nombre)
        if not cat:
            print(f"⚠ Categoría no encontrada: {categoria_nombre}")
            continue
            
        Pregunta.objects.get_or_create(
            texto=texto,
            categoria=cat,
            defaults={
                'tipo_respuesta': 'boolean',
                'orden': Pregunta.objects.filter(categoria=cat).count() + 1,
                'peso_categoria': 1.0
            }
        )
        creadas += 1
        print(f"✓ Pregunta [{creadas}/50]: {texto[:40]}...")
    
    print(f"\n🎉 Seed completado: {creadas} preguntas creadas")


if __name__ == '__main__':
    print("🌱 Iniciando seed de datos vocacionales...")
    categorias = crear_categorias()
    crear_preguntas(categorias)
    print("✅ Proceso terminado. ¡Listo para desarrollar!")