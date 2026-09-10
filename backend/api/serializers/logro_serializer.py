from rest_framework import serializers

from ..models.recompensa import Logro, RequisitoLogro


class RequisitoLogroSerializer(serializers.Serializer):
    requisito = serializers.ChoiceField(choices=RequisitoLogro.Requisito.choices)
    una_partida = serializers.BooleanField(required=False, default=False)
    valor_necesario = serializers.IntegerField(required=False, min_value=1, default=1)


def _nombre_field() -> serializers.CharField:
    return serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=40,
        error_messages={
            "required": "Falta el nombre",
            "blank": "Falta el nombre",
            "max_length": "El nombre es demasiado largo (max. 40 caracteres)",
        },
    )

class LogroSerializer(serializers.Serializer):
    nombre = _nombre_field()
    imagen = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        max_length=1000,
        error_messages={
            "max_length": "La imagen es demasiado larga (max. 1000 caracteres)",
        },
    )

    descripcion = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=1000,
        error_messages={
            "required": "Falta la descripcion",
            "blank": "Falta la descripcion",
            "max_length": "La descripcion es demasiado larga (max. 1000 caracteres)",
        },
    )
    oculto = serializers.BooleanField(
        required=False,
        default=False,
    )
    progreso_oculto = serializers.BooleanField(
        required=False,
        default=False,
    )
    requisitos = serializers.ListField(
        child=RequisitoLogroSerializer(),
        required=True,
        allow_empty=False,
        error_messages={
            "required": "Faltan los requisitos",
            "allow_empty": "Debe proporcionar al menos un requisito",
        },
    )

    def validate_nombre(self, value: str) -> str:
        qs = Logro.objects.filter(nombre=value)
        logro = self.context.get("logro")
        if logro is not None:
            qs = qs.exclude(id=logro.id)
        if qs.exists():
            raise serializers.ValidationError("El nombre ya existe")
        return value