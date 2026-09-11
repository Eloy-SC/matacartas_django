from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from api.utils.exceptions import RegistrationError
from ..models.recompensa import Medalla
from ..serializers.medalla_serializer import MedallaSerializer
from ..services import medalla_service


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listar_medallas(request):
    page_param = request.query_params.get("page", "1")
    try:
        page = max(1, int(page_param))
    except (TypeError, ValueError):
        page = 1

    search = (request.query_params.get("search") or "").strip() or None
    nombre = (request.query_params.get("nombre") or "").strip() or None
    categoria = (request.query_params.get("categoria") or "").strip() or None
    ordering_param = (request.query_params.get("ordering") or "nombre").strip()
    order_dir = "desc" if ordering_param.startswith("-") else "asc"
    order_by = ordering_param.lstrip("-") or "nombre"

    try:
        paged = medalla_service.listar_medallas_paginated(
            request.user,
            page=page,
            page_size=10,
            search=search,
            nombre=nombre,
            categoria=categoria,
            order_by=order_by,
            order_dir=order_dir,
        )
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)

    data = [
        {
            "id": medalla["id"],
            "nombre": medalla["nombre"],
            "categoria": medalla["categoria"],
            "imagen": medalla["imagen"],
        }
        for medalla in paged["items"]
    ]

    return Response(
        {
            "items": data,
            "page": paged["page"],
            "page_size": paged["page_size"],
            "total": paged["total"],
            "total_pages": paged["total_pages"],
        },
        status=200,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_medalla(request, medalla_id):
    try:
        medalla = medalla_service.get_medalla(request.user, medalla_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)

    if not medalla:
        return Response({"detail": "Medalla no encontrada"}, status=404)

    data = {
        "id": medalla.id,
        "nombre": medalla.nombre,
        "categoria": medalla.categoria,
        "imagen": medalla.imagen,
    }

    return Response(data, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listar_medallas_usuario(request):
    page_param = request.query_params.get("page", "1")
    try:
        page = max(1, int(page_param))
    except (TypeError, ValueError):
        page = 1

    ordering_param = (request.query_params.get("ordering") or "nombre").strip()
    order_dir = "desc" if ordering_param.startswith("-") else "asc"
    order_by = ordering_param.lstrip("-") or "nombre"

    try:
        paged = medalla_service.listar_medallas_usuario_paginated(
            request.user,
            page=page,
            page_size=10,
            order_by=order_by,
            order_dir=order_dir,
        )
    except PermissionError as e:
        return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

    return Response(paged, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def crear_medalla_admin(request):
    serializer = MedallaSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    try:
        medalla = medalla_service.crear_medalla_admin(request.user, **serializer.validated_data)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except RegistrationError as e:
        return Response(e.errors, status=400)

    return Response(
        {
            "id": medalla.id,
            "nombre": medalla.nombre,
            "detail": "Medalla creada",
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def editar_medalla_admin(request, medalla_id):
    target_medalla = Medalla.objects.filter(id=medalla_id).first()
    if target_medalla is None:
        return Response({"detail": "Medalla no encontrada"}, status=404)

    serializer = MedallaSerializer(data=request.data, context={"medalla": target_medalla})

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    try:
        medalla = medalla_service.editar_medalla_admin(
            request.user, medalla_id, **serializer.validated_data
        )
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except RegistrationError as e:
        return Response(e.errors, status=400)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)

    return Response(
        {
            "id": medalla.id,
            "nombre": medalla.nombre,
            "detail": "Medalla actualizada",
        },
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def eliminar_medalla_admin(request, medalla_id):
    try:
        medalla_service.eliminar_medalla_admin(request.user, medalla_id)
    except PermissionError as e:
        return Response({"detail": str(e)}, status=403)
    except ValueError as e:
        return Response({"detail": str(e)}, status=404)

    return Response({"detail": "Medalla eliminada"}, status=status.HTTP_200_OK)
