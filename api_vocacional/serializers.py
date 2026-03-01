from rest_framework import serializers
from .models import CategoriaVocacional, Pregunta, EvaluacionVocacional, RespuestaEvaluacion


class CategoriaSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaVocacional
        fields = ['id', 'nombre', 'color_hex']


class PreguntaSerializer(serializers.ModelSerializer):
    categoria = CategoriaSimpleSerializer(read_only=True)
    opciones_formateadas = serializers.SerializerMethodField()

    class Meta:
        model = Pregunta
        fields = [
            'id', 'texto', 'categoria', 'tipo_respuesta', 
            'opciones_formateadas', 'orden'
        ]
        read_only_fields = fields

    def get_opciones_formateadas(self, obj):
        """Devuelve opciones listas para usar en el frontend"""
        return obj.get_opciones_dict()


class RespuestaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaEvaluacion
        fields = ['pregunta', 'valor_respuesta', 'tiempo_respuesta_ms']
        extra_kwargs = {
            'pregunta': {'required': True},
            'valor_respuesta': {'required': True}
        }

    def validate_pregunta(self, value):
        """Valida que la pregunta exista y esté activa"""
        if not value.activa:
            raise serializers.ValidationError("Esta pregunta ya no está disponible")
        return value

    def validate(self, data):
        """Validación dinámica según el tipo de respuesta"""
        pregunta = data['pregunta']
        valor = data['valor_respuesta']

        if pregunta.tipo_respuesta == 'boolean':
            if str(valor).lower() not in ['si', 'no', 'true', 'false', True, False]:
                raise serializers.ValidationError("Respuesta booleana inválida")
        elif pregunta.tipo_respuesta == 'escala':
            try:
                val_num = float(valor)
                if not (1 <= val_num <= 5):
                    raise serializers.ValidationError("Escala debe estar entre 1 y 5")
            except (ValueError, TypeError):
                raise serializers.ValidationError("Valor de escala debe ser numérico")
        
        return data


class EvaluacionSerializer(serializers.ModelSerializer):
    progreso_porcentaje = serializers.IntegerField(read_only=True)
    total_preguntas = serializers.SerializerMethodField()
    respuestas_count = serializers.IntegerField(source='respuestas.count', read_only=True)

    class Meta:
        model = EvaluacionVocacional
        fields = [
            'id', 'estado', 'progreso_porcentaje', 
            'total_preguntas', 'respuestas_count', 'iniciado_en'
        ]
        read_only_fields = fields

    def get_total_preguntas(self, obj):
        return Pregunta.objects.filter(activa=True).count()


class EvaluacionResultadoSerializer(serializers.ModelSerializer):
    resultados = serializers.SerializerMethodField()
    resumen = serializers.SerializerMethodField()

    class Meta:
        model = EvaluacionVocacional
        fields = ['id', 'estado', 'completado_en', 'resultados', 'resumen']
        read_only_fields = fields

    def get_resultados(self, obj):
        return obj.calcular_resultados()

    def get_resumen(self, obj):
        """Genera un resumen dinámico con la categoría principal"""
        resultados = obj.calcular_resultados()
        if not resultados:
            return {'mensaje': 'Aún no hay suficientes respuestas para generar recomendaciones'}
        
        top_categoria = resultados[0]
        nombre_categoria = top_categoria.get('nombre', 'Desconocida')
        return {
            'categoria_principal': top_categoria['categoria_id'],
            'nombre_categoria': nombre_categoria,
            'porcentaje_principal': top_categoria['porcentaje'],
            'mensaje_personalizado': f"Tu perfil muestra mayor afinidad con {nombre_categoria}. ¡Explora más oportunidades en este campo!"
        }
