from graphviz import Digraph
import re

# Función para extraer los campos de un modelo
def extract_fields(model):
    fields = []
    for field in model._meta.get_fields():
        if not field.auto_created and not isinstance(field, models.AutoField):
            field_name = field.name
            field_type = str(field.__class__.__name__)
            if isinstance(field, models.ForeignKey):
                related_model = field.related_model._meta.label_lower
                fields.append(f"{field_name} ({field_type}) -> {related_model}")
            else:
                fields.append(f"{field_name} ({field_type})")
    return fields

# Función para generar el contenido del archivo DOT
def generate_dot_content(models):
    dot = Digraph(comment='Modelos de la base de datos')
    dot.graph_attr['rankdir'] = 'TB'
    dot.node_attr['shape'] = 'record'

    for model_name, model in models.items():
        fields = extract_fields(model)
        field_str = '|'.join(fields)
        dot.node(model_name, f'{model_name} | {field_str}')

    return dot.source

# Función para leer los modelos de un archivo
def read_models_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        models = {}
        current_model = None
        for line in content.split('\n'):
            if re.match(r'^class\s+(\w+)\(models\.Model\):', line):
                current_model = line.strip().split()[1]
                models[current_model] = []
            elif current_model and not line.startswith('    class '):
                models[current_model].append(line.strip())
        return models

# Ruta al archivo models.py
file_path = 'api_vocacional/models.py'

# Leer los modelos del archivo
models = read_models_from_file(file_path)

# Generar el contenido del archivo DOT
dot_content = generate_dot_content(models)

# Guardar el contenido en un archivo diccionario.dot
with open('diccionario.dot', 'w') as dot_file:
    dot_file.write(dot_content)
