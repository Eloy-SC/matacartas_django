

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.utils.exceptions import RegistrationError
from ..serializers.logro_serializer import LogroSerializer
from ..services import logro_service


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def crear_logro(request):
    serializer = LogroSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    try:
        logro = logro_service.crear_logro(request.user, **serializer.validated_data)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except RegistrationError as e:
        return Response(e.errors, status=400)
    except ValueError as e:
        return Response({"detail": str(e)}, status=400)

    data = {
        "id": logro.id,
        "nombre": logro.nombre,
        "descripcion": logro.descripcion,
        "imagen": logro.imagen,
        "oculto": logro.oculto,
        "progreso_oculto": logro.progreso_oculto,
        "requisitos": [
            {
                "id": requisito.id,
                "requisito": requisito.requisito,
                "una_partida": requisito.una_partida,
                "valor_necesario": requisito.valor_necesario,
            }
            for requisito in logro.requisitologro_set.all()
        ],
    }

    return Response(data, status=status.HTTP_201_CREATED)