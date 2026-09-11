

from django.db import IntegrityError, transaction

from backend.api.selectors.resumen_mano_selector import get_resumen_mano_by_mano_id

from ..selectors.mano_selector import get_manos_de_partida

from ..selectors.partida_selector import get_partida_usuario_by_partida_and_color

from ..models.recompensa import Logro, RecompensaUsuario, RequisitoLogro, RequisitoLogroUsuario
from ..selectors.logro_selector import (
    get_logros,
    get_logros_count,
    get_logros_ocultos_pendientes_count,
    get_logros_usuario_count,
    list_logros_paginated,
    list_logros_usuario_paginated,
)
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
    admin=False,
):
    if admin and not actor.is_staff:
        raise PermissionError("No tienes permiso para listar logros")
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


def eliminar_logro_admin(actor, logro_id):
    if not actor.is_staff:
        raise PermissionError("No tienes permiso para eliminar un logro")

    logro = Logro.objects.filter(id=logro_id).first()
    if logro is None:
        raise ValueError("No se encontró el logro a eliminar")

    logro.delete()


def listar_logros_usuario_paginated(actor, *, page, page_size, order_by="nombre", order_dir="asc"):
    if not actor.is_active:
        raise PermissionError("No tienes permiso para listar logros")

    allowed_order_fields = {"id", "nombre", "oculto"}
    order_field = order_by if order_by in allowed_order_fields else "nombre"
    ordering = f"{'-' if order_dir == 'desc' else ''}{order_field}"
    total = get_logros_usuario_count(actor.id)
    offset = (page - 1) * page_size
    items = list(list_logros_usuario_paginated(actor.id, offset, page_size, ordering=ordering))
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


def contar_logros_ocultos_pendientes(actor):
    if not actor.is_active:
        raise PermissionError("No tienes permiso para consultar logros")
    return get_logros_ocultos_pendientes_count(actor.id)

def obtener_requisitos_logro(actor, logro_id):
    if not actor.is_staff:
        raise PermissionError("No tienes permiso para obtener los requisitos de un logro")

    logro = Logro.objects.filter(id=logro_id).first()
    if logro is None:
        raise ValueError("No se encontró el logro")

    requisitos = RequisitoLogro.objects.filter(logro=logro).values(
        "id", "requisito", "una_partida", "valor_necesario"
    )
    return list(requisitos)

def asignar_logros_a_usuario(partida_usuario):

    logros = get_logros()
    usuario = partida_usuario.usuario
    partida = partida_usuario.partida
    
    for logro in logros:
        requisitos = RequisitoLogro.objects.filter(logro=logro)
        cumplidos = 0
        for req in requisitos:
            progreso = calcular_progreso_en_partida(req.requisito, partida.id, partida_usuario.color)
            if not req.una_partida:
                reqlogusuario = RequisitoLogroUsuario.objects.filter(
                    usuario=usuario, requisito_logro=req
                ).first()
                if reqlogusuario:
                    reqlogusuario.progreso += progreso
                    reqlogusuario.save(update_fields=["progreso"])
                else:
                    reqlogusuario = RequisitoLogroUsuario(usuario=usuario, requisito_logro=req, progreso=progreso)
                    reqlogusuario.save()
                # Una vez guardado el progreso, se comprueba si se ha cumplido el requisito
                if reqlogusuario.progreso >= req.valor_necesario:
                    cumplidos += 1
            else:
                if progreso >= req.valor_necesario:
                    cumplidos += 1
        if cumplidos == requisitos.count():
            recompensa_usuario = RecompensaUsuario(
                usuario=usuario,
                logro=logro
            )
            recompensa_usuario.save()
            for reqlogusuario in RequisitoLogroUsuario.objects.filter(usuario=usuario, requisito_logro__in=requisitos):
                reqlogusuario.delete()


def calcular_progreso_en_partida(requisito, partida_id, color):
    progreso = 0
    
    if requisito == "puntos_ganados_partida":
        progreso = aux_calcular_puntos_ganados_partida(partida_id, color)
    elif requisito == "puntuacion_acumulada":
        progreso = aux_calcular_puntuacion_acumulada(partida_id, color)
    elif requisito == "puntos_ganados_mercader":
        progreso = aux_calcular_puntos_ganados_carta(partida_id, color, "MERCADER")
    elif requisito == "puntos_ganados_rebelde":
        progreso = aux_calcular_puntos_ganados_carta(partida_id, color, "REBELDE")
    elif requisito == "puntos_ganados_segador":
        progreso = aux_calcular_puntos_ganados_carta(partida_id, color, "SEGADOR")
    elif requisito == "cartas_victimas_segador":
        progreso = aux_calcular_cartas_victimas_segador(partida_id, color)
    elif requisito == "puntos_ganados_joyas_reales":
        progreso = aux_calcular_puntos_ganados_carta(partida_id, color, "JOYAS_REALES")
    elif requisito == "puntos_ganados_vinos_viejos":
        progreso = aux_calcular_puntos_ganados_vinos_viejos(partida_id, color)
    elif requisito == "muertes_corrompidas_corruptor":
        progreso = aux_calcular_muertes_corrompidas_corruptor(partida_id, color)
    elif requisito == "tumbas_saqueadas_saqueador":
        progreso = aux_calcular_tumbas_saqueadas_saqueador(partida_id, color)
    elif requisito == "partidas_ganadas":
        progreso = aux_calcular_partidas_ganadas(partida_id, color)
    elif requisito == "cartas_kills":
        progreso = aux_calcular_cartas_kills(partida_id, color)
    elif requisito == "cartas_deaths":
        progreso = aux_calcular_cartas_deaths(partida_id, color)
    elif requisito == "rondas_ganadas":
        progreso = aux_calcular_rondas_ganadas(partida_id, color)
    elif requisito == "rondas_comodin_ganadas":
        progreso = aux_calcular_rondas_comodin_ganadas(partida_id, color)
    elif requisito == "manos_ganadas":
        progreso = aux_calcular_manos_ganadas(partida_id, color)
    elif requisito == "retiradas":
        progreso = aux_calcular_retiradas(partida_id, color)
    elif requisito == "manos_ganadas_unica":
        progreso = aux_calcular_manos_ganadas_unica(partida_id, color)
    elif requisito == "contraataques_bastos_punt":
        progreso = aux_calcular_contraataques_bastos_punt(partida_id, color)
    elif requisito == "tickets_usados":
        progreso = aux_calcular_tickets_usados(partida_id, color)

    return progreso


def aux_calcular_puntos_ganados_partida(partida_id, color):
    pu = get_partida_usuario_by_partida_and_color(partida_id, color)
    return pu.puntos

def aux_calcular_puntuacion_acumulada(partida_id, color):
    pu = get_partida_usuario_by_partida_and_color(partida_id, color)
    partida = pu.partida
    puntuacion = partida.puntuacion_asignada_final[color] if partida.puntuacion_asignada_final else 0
    if pu.abandono or puntuacion < 0:
        return 0
    return puntuacion

def aux_calcular_puntos_ganados_carta(partida_id, color, carta):
    manos = get_manos_de_partida(partida_id)
    puntos = 0
    for mano in manos:
        resumen = get_resumen_mano_by_mano_id(mano.id)
        for beneficiado, efecto in resumen.efectos_extra_fin_mano:
            if carta != "JOYAS_REALES" and beneficiado == color and efecto == carta:
                if carta == "MERCADER":
                    puntos_anadir = resumen.puntos_mercader if resumen.puntos_mercader else 0
                elif carta == "REBELDE":
                    puntos_anadir = resumen.puntos_rebelde if resumen.puntos_rebelde else 0
                elif carta == "SEGADOR":
                    puntos_anadir = resumen.puntos_segador if resumen.puntos_segador else 0
                puntos += puntos_anadir
            elif carta == "JOYAS_REALES" and beneficiado == color:
                if efecto == "JOYAS_REALES_2":
                    puntos_anadir = 2
                elif efecto == "JOYAS_REALES_3":
                    puntos_anadir = 3
                else:
                    puntos_anadir = 0
                puntos += puntos_anadir
    return puntos

def aux_calcular_cartas_victimas_segador(partida_id, color):
    manos = get_manos_de_partida(partida_id)
    cartas = 0
    for mano in manos:
        resumen = get_resumen_mano_by_mano_id(mano.id)
        for beneficiado, efecto in resumen.efectos_extra_fin_mano:
            if efecto == "SEGADOR" and beneficiado == color:
                cartas += resumen.puntos_segador/2
    return cartas

def aux_calcular_puntos_ganados_vinos_viejos(partida_id, color):
    manos = get_manos_de_partida(partida_id)
    puntos = 0
    for mano in manos:
        resumen = get_resumen_mano_by_mano_id(mano.id)
        for beneficiado, efecto in resumen.efectos_inmediatos_ronda.values():
            if efecto == "VINOS_VIEJOS" and beneficiado == color:
                puntos += 2
    return puntos

def aux_calcular_muertes_corrompidas_corruptor(partida_id, color):
    manos = get_manos_de_partida(partida_id)
    muertes_corrompidas = 0
    for mano in manos:
        resumen = get_resumen_mano_by_mano_id(mano.id)
        for jugador, tipo_victoria in resumen.victorias.values():
            if tipo_victoria == "CORRUPTOR" and jugador == color:
                muertes_corrompidas += 1
    return muertes_corrompidas

def aux_calcular_tumbas_saqueadas_saqueador(partida_id, color):
    manos = get_manos_de_partida(partida_id)
    tumbas_saqueadas = 0
    for mano in manos:
        resumen = get_resumen_mano_by_mano_id(mano.id)
        for beneficiado, efecto in resumen.efectos_inmediatos_ronda.values():
            if efecto == "SAQUEADOR" and beneficiado == color:
                tumbas_saqueadas += 1
    return tumbas_saqueadas

def aux_calcular_partidas_ganadas(partida_id, color):
    pu = get_partida_usuario_by_partida_and_color(partida_id, color)
    partida = pu.partida
    mayor_puntuacion = max(partida.puntuacion_asignada_final.values()) if partida.puntuacion_asignada_final else 0
    if pu.abandono or partida.puntuacion_asignada_final[color] < mayor_puntuacion:
        return 0
    return 1

def aux_calcular_cartas_kills(partida_id, color):
    manos = get_manos_de_partida(partida_id)
    kills = 0
    for mano in manos:
        resumen = get_resumen_mano_by_mano_id(mano.id)
        for jugador_matador, jugador_matado in resumen.muertes.values():
            if jugador_matador == color:
                kills += 1
    return kills

def aux_calcular_cartas_deaths(partida_id, color):
    manos = get_manos_de_partida(partida_id)
    deaths = 0
    for mano in manos:
        resumen = get_resumen_mano_by_mano_id(mano.id)
        for jugador_matador, jugador_matado in resumen.muertes.values():
            if jugador_matado == color:
                deaths += 1
    return deaths

def aux_calcular_rondas_ganadas(partida_id, color):
    manos = get_manos_de_partida(partida_id)
    victorias = 0
    for mano in manos:
        resumen = get_resumen_mano_by_mano_id(mano.id)
        for jugador, tipo_victoria in resumen.victorias.values():
            if jugador == color:
                victorias += 1
    return victorias

def aux_calcular_rondas_comodin_ganadas(partida_id, color):
    manos = get_manos_de_partida(partida_id)
    victorias = 0
    for mano in manos:
        resumen = get_resumen_mano_by_mano_id(mano.id)
        victoria_ronda_comodin = resumen.victorias.get(4)
        if victoria_ronda_comodin and victoria_ronda_comodin[0] == color:
            victorias += 1
    return victorias

def aux_calcular_manos_ganadas(partida_id, color):
    manos = get_manos_de_partida(partida_id)
    victorias = 0
    for mano in manos:
        if mano.ganador == color:
            victorias += 1
    return victorias

def aux_calcular_retiradas(partida_id, color):
    manos = get_manos_de_partida(partida_id)
    retiradas = 0
    for mano in manos:
        resumen = get_resumen_mano_by_mano_id(mano.id)
        for jugadores_retirados in resumen.retiradas.values():
            if color in jugadores_retirados:
                retiradas += 1
    return retiradas

def aux_calcular_manos_ganadas_unica(partida_id, color):
    manos = get_manos_de_partida(partida_id)
    victorias = 0
    for mano in manos:
        resumen = get_resumen_mano_by_mano_id(mano.id)
        for beneficiado, efecto in resumen.efectos_extra_fin_mano:
            if efecto == "CARTA_UNICA" and beneficiado == color:
                victorias += 1
    return victorias

def aux_calcular_contraataques_bastos_punt(partida_id, color):
    manos = get_manos_de_partida(partida_id)
    contras = 0
    for mano in manos:
        resumen = get_resumen_mano_by_mano_id(mano.id)
        for jugador, tipo_victoria in resumen.victorias.values():
            if tipo_victoria == "CONTRAATAQUE" and jugador == color:
                contras += 1
    return contras

def aux_calcular_tickets_usados(partida_id, color):
    manos = get_manos_de_partida(partida_id)
    tickets_usados = 0
    for mano in manos:
        resumen = get_resumen_mano_by_mano_id(mano.id)
        for tickets in resumen.tickets_usados.values():
            for jugador, ticket in tickets:
                if jugador == color:
                    tickets_usados += 1
    return tickets_usados