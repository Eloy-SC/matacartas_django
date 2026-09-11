from ..models.medalla_torneo import MedallaTorneo

from ..models.recompensa import Medalla, RecompensaUsuario
from django.db.models import Q, Subquery



def get_medalla_by_id(medalla_id):
    return Medalla.objects.filter(id=medalla_id).first()


def get_medalla_by_nombre(nombre):
    return Medalla.objects.filter(nombre=nombre).first()


def list_medallas():
    return Medalla.objects.all().values("id", "nombre", "categoria", "imagen").order_by("nombre")

def get_medalla_by_id(medalla_id):
    return Medalla.objects.filter(id=medalla_id).first()

def get_medallas_by_torneo_id(torneo_id):
    medallas_torneo = MedallaTorneo.objects.filter(torneo__id=torneo_id).order_by("puesto")
    medallas = [medalla_torneo.medalla for medalla_torneo in medallas_torneo]
    return medallas

def _build_medallas_queryset(search=None, nombre=None, categoria=None):
    queryset = Medalla.objects.all()

    if search:
        search = search.strip()
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | Q(categoria__icontains=search)
            )

    if nombre:
        queryset = queryset.filter(nombre__icontains=nombre.strip())

    if categoria:
        queryset = queryset.filter(categoria=categoria)

    return queryset


def list_medallas_paginated(offset, limit, *, search=None, nombre=None, categoria=None, ordering=None):
    queryset = _build_medallas_queryset(search=search, nombre=nombre, categoria=categoria)
    order_fields = [ordering or "nombre"]
    if (ordering or "nombre").lstrip("-") != "id":
        order_fields.append("id")

    return queryset.values("id", "nombre", "categoria", "imagen").order_by(*order_fields)[offset:offset + limit]


def get_medallas_count(*, search=None, nombre=None, categoria=None):
    return _build_medallas_queryset(search=search, nombre=nombre, categoria=categoria).count()


def _build_medallas_usuario_queryset(usuario_id):
    return Medalla.objects.filter(
        id__in=Subquery(
            RecompensaUsuario.objects.filter(
                usuario_id=usuario_id,
                medalla__isnull=False,
            ).values("medalla_id")
        )
    )


def list_medallas_usuario_paginated(usuario_id, offset, limit, *, ordering=None):
    ordering = ordering or "nombre"
    queryset = _build_medallas_usuario_queryset(usuario_id)
    order_fields = [ordering]
    if ordering.lstrip("-") != "id":
        order_fields.append("id")
    return queryset.values("id", "nombre", "categoria", "imagen").order_by(*order_fields)[offset:offset + limit]


def get_medallas_usuario_count(usuario_id):
    return _build_medallas_usuario_queryset(usuario_id).count()