from django.db import IntegrityError

from ..models.recompensa import Medalla
from ..selectors.medalla_selector import (
    get_medalla_by_id,
    get_medalla_by_nombre,
    get_medallas_count,
    list_medallas,
    list_medallas_paginated,
)
from ..utils.exceptions import RegistrationError


def listar_medallas(actor):
    if not actor.is_active:
        raise PermissionError("No tienes permiso para listar medallas")

    return list_medallas()


def listar_medallas_paginated(
    actor,
    *,
    page,
    page_size,
    search=None,
    nombre=None,
    categoria=None,
    order_by="nombre",
    order_dir="asc",
):
    if not actor.is_active:
        raise PermissionError("No tienes permiso para listar medallas")

    allowed_order_fields = {"id", "nombre", "categoria"}
    order_field = order_by if order_by in allowed_order_fields else "nombre"
    ordering = f"{'-' if order_dir == 'desc' else ''}{order_field}"
    total = get_medallas_count(search=search, nombre=nombre, categoria=categoria)
    offset = (page - 1) * page_size
    items = list(list_medallas_paginated(
        offset,
        page_size,
        search=search,
        nombre=nombre,
        categoria=categoria,
        ordering=ordering,
    ))

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


def get_medalla(actor, medalla_id):
    if not actor.is_active:
        raise PermissionError("No tienes permiso para obtener la medalla")

    return get_medalla_by_id(medalla_id)


def crear_medalla_admin(actor, *, nombre, categoria, imagen=None):
    if not actor.is_staff:
        raise PermissionError("No tienes permiso para crear una medalla")

    if get_medalla_by_nombre(nombre) is not None:
        raise RegistrationError({"nombre": ["El nombre ya existe"]})

    medalla = Medalla(nombre=nombre, categoria=categoria, imagen=imagen)

    try:
        medalla.save()
    except IntegrityError as e:
        msg = str(e)
        if "nombre" in msg:
            raise RegistrationError({"nombre": ["El nombre ya existe"]})
        raise RegistrationError({"detail": ["No se pudo crear la medalla"]})

    return medalla


def editar_medalla_admin(actor, medalla_id, *, nombre, categoria, imagen=None):
    if not actor.is_staff:
        raise PermissionError("No tienes permiso para editar una medalla")

    medalla = get_medalla_by_id(medalla_id)
    if medalla is None:
        raise ValueError("No se encontró la medalla a editar")

    medalla_nombre_repetido = get_medalla_by_nombre(nombre)
    if medalla_nombre_repetido is not None and medalla_nombre_repetido.id != medalla_id:
        raise RegistrationError({"nombre": ["El nombre ya existe"]})

    medalla.nombre = nombre
    medalla.categoria = categoria
    medalla.imagen = imagen

    try:
        medalla.save()
    except IntegrityError as e:
        msg = str(e)
        if "nombre" in msg:
            raise RegistrationError({"nombre": ["El nombre ya existe"]})
        raise RegistrationError({"detail": ["No se pudo editar la medalla"]})

    return medalla


def eliminar_medalla_admin(actor, medalla_id):
    if not actor.is_staff:
        raise PermissionError("No tienes permiso para eliminar una medalla")

    medalla = get_medalla_by_id(medalla_id)
    if medalla is None:
        raise ValueError("No se encontró la medalla a eliminar")

    try:
        medalla.delete()
    except Exception:
        raise ValueError("No se pudo eliminar la medalla")
