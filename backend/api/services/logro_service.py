

from django.db import IntegrityError, transaction

from ..models.recompensa import Logro, RequisitoLogro
from ..utils.exceptions import RegistrationError


def crear_logro(actor, *, nombre, descripcion, imagen=None, oculto=False, progreso_oculto=False, requisitos):
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
                progreso_oculto=progreso_oculto,
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

