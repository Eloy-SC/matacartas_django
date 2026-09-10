

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.utils.exceptions import RegistrationError
from ..serializers.logro_serializer import LogroSerializer
from ..services import logro_service


def _parse_bool_param(value):
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "si", "y"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False
    return None


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listar_logros(request):
    page_param = request.query_params.get("page", "1")
    try:
        page = max(1, int(page_param))
    except (TypeError, ValueError):
        page = 1

    search = (request.query_params.get("search") or "").strip() or None
    nombre = (request.query_params.get("nombre") or "").strip() or None
    oculto = _parse_bool_param(request.query_params.get("oculto"))
    ordering_param = (request.query_params.get("ordering") or "nombre").strip()
    order_dir = "desc" if ordering_param.startswith("-") else "asc"
    order_by = ordering_param.lstrip("-") or "nombre"

    try:
        paged = logro_service.listar_logros_paginated(
            request.user,
            page=page,
            page_size=10,
            search=search,
            nombre=nombre,
            oculto=oculto,
            order_by=order_by,
            order_dir=order_dir,
        )
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)

    data = [_logro_response(logro) for logro in paged["items"]]
    return Response(
        {
            "items": data,
            "page": paged["page"],
            "page_size": paged["page_size"],
            "total": paged["total"],
            "total_pages": paged["total_pages"],
        },
        status=status.HTTP_200_OK,
    )


def _logro_response(logro):
    return {
        "id": logro.id,
        "nombre": logro.nombre,
        "descripcion": logro.descripcion,
        "imagen": logro.imagen,
        "oculto": logro.oculto,
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