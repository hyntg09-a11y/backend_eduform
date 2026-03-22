# Diccionario de Datos - Modelos de la Aplicación

## CategoriaVocacional

| Campo | Tipo | Longitud | Nulo | Único | Descripción |
|-------|------|----------|------|-------|-------------|
| id | AutoField | - | No | Sí | Identificador único del registro |
| nombre | CharField | 100 | No | Sí | Nombre de la categoría vocacional (ej: Tecnología, Salud, Arte) |
| descripcion | TextField | - | Sí | No | Descripción detallada de la categoría |
| color_hex | CharField | 7 | No | No | Color en formato hexadecimal para visualización |
| orden | PositiveSmallIntegerField | - | No | No | Orden de presentación de la categoría |
| activa | BooleanField | - | No | No | Indica si la categoría está activa |
| creado_en | DateTimeField | - | No | No | Fecha y hora de creación del registro |

## Pregunta

| Campo | Tipo | Longitud | Nulo | Único | Descripción |
|-------|------|----------|------|-------|-------------|
| id | AutoField | - | No | Sí | Identificador único del registro |
| texto | TextField | - | No | No | Texto de la pregunta de la evaluación vocacional |
| categoria | ForeignKey | - | No | No | Relación con CategoriaVocacional |
| tipo_respuesta | CharField | 20 | No | No | Tipo de respuesta (Sí/No, Escala 1-5, Opción múltiple) |
| opciones | JSONField | - | Sí | No | Opciones para tipo 'opcion_multiple' o 'escala' |
| peso_categoria | FloatField | - | No | No | Peso de esta pregunta para su categoría |
| orden | PositiveSmallIntegerField | - | No | No | Orden de presentación de la pregunta |
| activa | BooleanField | - | No | No | Indica si la pregunta está activa |
| creado_en | DateTimeField | - | No | No | Fecha y hora de creación del registro |

## ProgramaEstatal

| Campo | Tipo | Longitud | Nulo | Único | Descripción |
|-------|------|----------|------|-------|-------------|
| id | AutoField | - | No | Sí | Identificador único del registro |
| nombre_programa | CharField | 200 | No | No | Nombre del programa estatal de apoyo vocacional |
| entidad_responsable | CharField | 200 | No | No | Entidad responsable del programa |
| descripcion | TextField | - | Sí | No | Descripción del programa |
| activo | BooleanField | - | No | No | Indica si el programa está activo |
| creado_en | DateTimeField | - | No | No | Fecha y hora de creación del registro |

## Carrera

| Campo | Tipo | Longitud | Nulo | Único | Descripción |
|-------|------|----------|------|-------|-------------|
| id | AutoField | - | No | Sí | Identificador único del registro |
| nombre | CharField | 200 | No | Sí | Nombre de la carrera profesional |
| perfil_vocacional | ForeignKey | - | No | No | Relación con CategoriaVocacional |
| descripcion | TextField | - | Sí | No | Descripción de la carrera |
| activa | BooleanField | - | No | No | Indica si la carrera está activa |

## EvaluacionVocacional

| Campo | Tipo | Longitud | Nulo | Único | Descripción |
|-------|------|----------|------|-------|-------------|
| id | AutoField | - | No | Sí | Identificador único del registro |
| estado | CharField | 20 | No | No | Estado de la evaluación (iniciada, en_progreso, completada, cancelada) |
| usuario | ForeignKey | - | Sí | No | Relación con el modelo de usuario de Django |
| ip_usuario | GenericIPAddressField | - | Sí | No | Dirección IP del usuario que realiza la evaluación |
| user_agent | CharField | 255 | Sí | No | Información del agente de usuario (navegador, sistema operativo) |
| iniciado_en | DateTimeField | - | No | No | Fecha y hora de inicio de la evaluación |
| completado_en | DateTimeField | - | Sí | No | Fecha y hora de finalización de la evaluación |
| metadata | JSONField | - | Sí | No | Datos extra como navegador, resolución, etc. |

## RespuestaEvaluacion

| Campo | Tipo | Longitud | Nulo | Único | Descripción |
|-------|------|----------|------|-------|-------------|
| id | AutoField | - | No | Sí | Identificador único del registro |
| evaluacion | ForeignKey | - | No | No | Relación con EvaluacionVocacional |
| pregunta | ForeignKey | - | No | Sí | Relación con Pregunta (única por evaluación) |
| valor_respuesta | JSONField | - | No | No | Valor de la respuesta (puede ser string, número, boolean o objeto) |
| tiempo_respuesta_ms | PositiveIntegerField | - | Sí | No | Tiempo en milisegundos que tardó en responder |
| respondido_en | DateTimeField | - | No | No | Fecha y hora en que se respondió la pregunta |

## PerfilAcademico

| Campo | Tipo | Longitud | Nulo | Único | Descripción |
|-------|------|----------|------|-------|-------------|
| id | AutoField | - | No | Sí | Identificador único del registro |
| usuario | ForeignKey | - | No | No | Relación con el modelo de usuario de Django |
| nivel_educativo | CharField | 50 | No | No | Nivel educativo del usuario |
| institucion | CharField | 200 | Sí | No | Institución educativa del usuario |
| creado_en | DateTimeField | - | No | No | Fecha y hora de creación del registro |

## FactoresSocioeconomicos

| Campo | Tipo | Longitud | Nulo | Único | Descripción |
|-------|------|----------|------|-------|-------------|
| id | AutoField | - | No | Sí | Identificador único del registro |
| usuario | OneToOneField | - | No | Sí | Relación única con el modelo de usuario de Django |
| id_factor | CharField | 100 | No | No | Identificador del factor socioeconómico |
| influencia_economica | FloatField | - | No | No | Valor numérico que representa la influencia económica |

## RecomendacionCarrera

| Campo | Tipo | Longitud | Nulo | Único | Descripción |
|-------|------|----------|------|-------|-------------|
| id | AutoField | - | No | Sí | Identificador único del registro |
| evaluacion | ForeignKey | - | No | No | Relación con EvaluacionVocacional |
| carrera | ForeignKey | - | No | Sí | Relación con Carrera (única por evaluación) |
| puntaje | FloatField | - | No | No | Puntaje de la recomendación |
| creado_en | DateTimeField | - | No | No | Fecha y hora de creación del registro |

## RecomendacionPrograma

| Campo | Tipo | Longitud | Nulo | Único | Descripción |
|-------|------|----------|------|-------|-------------|
| id | AutoField | - | No | Sí | Identificador único del registro |
| evaluacion | ForeignKey | - | No | No | Relación con EvaluacionVocacional |
| programa | ForeignKey | - | No | Sí | Relación con ProgramaEstatal (único por evaluación) |
| creado_en | DateTimeField | - | No | No | Fecha y hora de creación del registro |

