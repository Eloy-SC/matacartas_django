

from django.db import IntegrityError, transaction

from ..models.recompensa import Logro, RequisitoLogro
from ..selectors.logro_selector import get_logros_count, list_logros_paginated
from ..utils.exceptions import RegistrationError


def crear_logro(actor, *, nombre, descripcion, imagen=None, oculto=False, requisitos):
    """
    Crea un nuevo logro en la base de datos.
    """

    if not actor.is_staff:
        raise PermissionError("No tienes permiso para crear un logro")

    if len(requisitos) == 0:
        raise ValueError("Debe proporcionar al menos un requisito para el logro")

    try:
        with transaction.atomic():
            logro = Logro.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                imagen=imagen,
                oculto=oculto,
            )
            RequisitoLogro.objects.bulk_create(
                [
                    RequisitoLogro(
                        logro=logro,
                        requisito=requisito["requisito"],
                        una_partida=requisito.get("una_partida", False),
                        valor_necesario=requisito.get("valor_necesario", 1),
                    )
                    for requisito in requisitos
                ]
            )
    except IntegrityError as e:
        msg = str(e)
        if "nombre" in msg:
            raise RegistrationError({"nombre": ["El nombre ya existe"]})
        raise RegistrationError({"detail": ["No se pudo crear el logro"]})

    return logro


def listar_logros_paginated(
    actor,
    *,
    page,
    page_size,
    search=None,
    nombre=None,
    oculto=None,
    order_by="nombre",
    order_dir="asc",
):
    if not actor.is_active:
        raise PermissionError("No tienes permiso para listar logros")

    allowed_order_fields = {"id", "nombre", "oculto"}
    order_field = order_by if order_by in allowed_order_fields else "nombre"
    ordering = f"{'-' if order_dir == 'desc' else ''}{order_field}"
    total = get_logros_count(search=search, nombre=nombre, oculto=oculto)
    offset = (page - 1) * page_size
    items = list(
        list_logros_paginated(
            offset,
            page_size,
            search=search,
            nombre=nombre,
            oculto=oculto,
            ordering=ordering,
        )
    )

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }

