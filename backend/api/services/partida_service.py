import random
from sqlite3 import IntegrityError
from django.utils import timezone

from ..selectors.torneo_selector import get_partida_torneo_by_partida_id

from ..selectors.ronda_selector import get_rondas_de_mano

from ..services.resumen_mano_service import create_resumen_mano

from ..selectors.mano_selector import get_mano_actual, get_manos_de_partida

from ..services.mano_service import repartir_cartas

from ..models.partida_usuario import PartidaUsuario

from ..selectors.rango_selector import get_rango_by_id
from ..utils.exceptions import RegistrationError

from ..models.partida import Partida
from ..models.mano import Mano
from ..models.ronda import Ronda
from ..selectors.partida_selector import *
from ..utils.funciones_aux import aux_almacenar_posiciones_finales_partida_torneo, aux_fin_partida_mod_puntos, aux_fin_partida_posiciones, aux_generar_baraja_inicial, aux_generar_disposicion_jugadores, aux_siguiente_turno, obtener_primer_jugador_activo


def listar_partidas_publicas(
        actor, 
        *, 
        page, 
        page_size,
    search=None,
        nombre=None,
        num_jugadores=None,
        rango_minimo_id=None,
        rango_maximo_id=None,
        empezada=None,
        order_by="id",
        order_dir="asc",
        ):
    """
    Devuelve una lista paginada de partidas públicas en juego o en sala de espera.
    """

    if not actor.is_authenticated:
        raise PermissionError("No tienes permiso para listar las partidas públicas")
    
    allowed_order_fields = {"id", "nombre", "num_jugadores", "rango_minimo_id", "rango_maximo_id", "fecha_creacion", "fecha_inicio", "fecha_fin"}
    order_field = order_by if order_by in allowed_order_fields else "id"
    order_prefix = "-" if order_dir == "desc" else ""
    ordering = f"{order_prefix}{order_field}"
    
    total = get_partidas_publicas_count(
        search=search,
        nombre=nombre,
        num_jugadores=num_jugadores,
        rango_minimo_id=rango_minimo_id,
        rango_maximo_id=rango_maximo_id,
        empezada=empezada
    )
    offset = (page - 1) * page_size
    items = list(
        get_partidas_publicas_paginated(
            offset, 
            page_size,
            search=search,
            nombre=nombre,
            num_jugadores=num_jugadores,
            rango_minimo_id=rango_minimo_id,
            rango_maximo_id=rango_maximo_id,
            empezada=empezada,
            ordering=ordering
        )
    )
    total_pages = max(1, (total + page_size - 1) // page_size)

    rango_nombre_cache = {}

    def _get_rango_nombre(rango_id):
        if rango_id is None:
            return None
        if rango_id not in rango_nombre_cache:
            rango = get_rango_by_id(rango_id)
            rango_nombre_cache[rango_id] = rango.nombre if rango else None
        return rango_nombre_cache[rango_id]

    items_payload = []
    for partida in items:
        id_partida = partida.get("id")
        rango_minimo_nombre = _get_rango_nombre(partida.get("rango_minimo_id"))
        rango_maximo_nombre = _get_rango_nombre(partida.get("rango_maximo_id"))

        items_payload.append(
            {
                "id": id_partida,
                "nombre": partida.get("nombre"),
                "jugadores_maximos": partida.get("num_jugadores"),
                "rango_minimo": rango_minimo_nombre,
                "rango_maximo": rango_maximo_nombre,
                "longitud": partida.get("longitud"),
                "cartas_especiales": partida.get("cartas_especiales"),
                "tickets": partida.get("tickets"),
                "fecha_creacion": partida.get("fecha_creacion"),
                "jugadores_actuales": get_jugadores_actuales_de_partida_count(id_partida),
                "estado": get_estado_de_partida(id_partida),
            }
        )

    return {
        "items": items_payload,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
    }

def crear_partida(actor, nombre, num_jugadores, privada, clave, longitud, cartas_especiales, tickets, tiempo_max_turno, rango_minimo_id=None, rango_maximo_id=None):
    """
    Crea una nueva partida con los parámetros especificados.
    """

    if not actor.is_authenticated:
        raise PermissionError("No tienes permiso para crear una partida")
    
    if get_partida_by_nombre(nombre):
        raise RegistrationError({"nombre": ["El nombre ya existe"]})
    if privada:
        if not clave:
            raise RegistrationError({"clave": ["Falta la clave para la partida privada"]})
        else:
            if get_partida_by_clave(clave):
                raise RegistrationError({"clave": ["La clave ya existe"]})
    if not privada:
        if clave:
            raise RegistrationError({"clave": ["No se puede asignar una clave a una partida pública"]})
    
    if num_jugadores < 2:
        raise ValueError("El número de jugadores debe ser al menos 2")
    if num_jugadores > 6:
        raise ValueError("El número de jugadores no puede ser mayor a 6")
    
    if longitud not in Partida.LongitudPartida.values:
        raise ValueError("La longitud de la partida no es válida")
    
    if tiempo_max_turno < 20:
        raise ValueError("El tiempo máximo por turno debe ser al menos 20 segundos")
    if tiempo_max_turno > 180:
        raise ValueError("El tiempo máximo por turno no puede ser mayor a 180 segundos (3 minutos)")
    
    rango_minimo = get_rango_by_id(rango_minimo_id) if rango_minimo_id is not None else None
    rango_maximo = get_rango_by_id(rango_maximo_id) if rango_maximo_id is not None else None
    if rango_minimo and rango_maximo:
        if rango_minimo.puntos_minimos > rango_maximo.puntos_minimos:
            raise ValueError("El rango mínimo no puede ser mayor que el rango máximo")
        if actor.puntuacion > rango_maximo.puntos_maximos or actor.puntuacion < rango_minimo.puntos_minimos:
            raise PermissionError("Tu rango se encuentra fuera del intervalo permitido para esta partida")
        
    if get_usuario_participa_en_partida_activa(actor.id):
        raise ValueError("Ya estás participando en una partida activa")
    
    partida = Partida(
        nombre=nombre,
        num_jugadores=num_jugadores,
        privada=privada,
        clave=clave,
        longitud=longitud,
        cartas_especiales=cartas_especiales,
        tickets=tickets,
        tiempo_max_turno=tiempo_max_turno,
        rango_minimo_id=rango_minimo_id,
        rango_maximo_id=rango_maximo_id
    )

    partida_usuario = PartidaUsuario(
        partida=partida,
        usuario=actor,
        creador=True,
        color=PartidaUsuario.ColorJugador.ROJO # Asignar un color por defecto al creador de la partida
    )
    
    try:
        partida.save()
        partida_usuario.save()
    except IntegrityError:
        raise RegistrationError({"detail": ["No se pudo crear la partida"]})

    return partida

def editar_partida(actor, partida_id, nombre, num_jugadores, privada, clave, longitud, cartas_especiales, tickets, tiempo_max_turno, rango_minimo_id=None, rango_maximo_id=None):
    """
    Edita una partida existente con los nuevos parámetros especificados.
    """

    if not actor.is_authenticated:
        raise PermissionError("No tienes permiso para editar una partida")
    
    partida = Partida.objects.filter(id=partida_id).first()
    if not partida:
        raise ValueError("La partida no existe")
    if partida.fecha_inicio is not None:
        raise ValueError("No se puede editar una partida que ya ha comenzado")
    
    partida_usuario_actor = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario_actor or not partida_usuario_actor.creador:
        raise PermissionError("No tienes permiso para editar esta partida")

    partida_by_nombre = get_partida_by_nombre(nombre).first()
    if partida_by_nombre and partida_by_nombre.id != partida_id:
        raise RegistrationError({"nombre": ["El nombre ya existe"]})
    if privada:
        if not clave:
            raise RegistrationError({"clave": ["Falta la clave para la partida privada"]})
        else:
            partida_by_clave = get_partida_by_clave(clave).first()
            if partida_by_clave and partida_by_clave.id != partida_id:
                raise RegistrationError({"clave": ["La clave ya existe"]})
    if not privada:
        if clave:
            raise RegistrationError({"clave": ["No se puede asignar una clave a una partida pública"]})
    
    if num_jugadores < 2:
        raise ValueError("El número de jugadores debe ser al menos 2")
    if num_jugadores > 6:
        raise ValueError("El número de jugadores no puede ser mayor a 6")
    if num_jugadores < get_jugadores_actuales_de_partida_count(partida_id):
        raise ValueError("El número de jugadores no puede ser menor que el número de jugadores actuales en la partida")
    
    if longitud not in Partida.LongitudPartida.values:
        raise ValueError("La longitud de la partida no es válida")
    
    if tiempo_max_turno < 20:
        raise ValueError("El tiempo máximo por turno debe ser al menos 20 segundos")
    if tiempo_max_turno > 180:
        raise ValueError("El tiempo máximo por turno no puede ser mayor a 180 segundos (3 minutos)")
    
    comprobar_rangos(rango_minimo_id, rango_maximo_id, partida_id)
    
    partida.nombre = nombre
    partida.num_jugadores = num_jugadores
    partida.privada = privada
    partida.clave = clave
    partida.longitud = longitud
    partida.cartas_especiales = cartas_especiales
    partida.tickets = tickets
    partida.tiempo_max_turno = tiempo_max_turno
    partida.rango_minimo_id = rango_minimo_id
    partida.rango_maximo_id = rango_maximo_id

    try:
        partida.save()
    except IntegrityError:
        raise RegistrationError({"detail": ["No se pudo crear la partida"]})

    return partida

def comprobar_rangos(rango_minimo_id, rango_maximo_id, partida_id):
    rango_minimo = get_rango_by_id(rango_minimo_id) if rango_minimo_id is not None else None
    rango_maximo = get_rango_by_id(rango_maximo_id) if rango_maximo_id is not None else None
    if rango_minimo and rango_maximo:
        if rango_minimo.puntos_minimos > rango_maximo.puntos_minimos:
            raise ValueError("El rango mínimo no puede ser mayor que el rango máximo")
    if rango_minimo or rango_maximo:
        for jugador in get_jugadores_actuales_de_partida(partida_id):
            if rango_maximo:
                if jugador["puntuacion"] > rango_maximo.puntos_maximos:
                    raise PermissionError("Hay jugadores en la partida que se encuentran fuera del intervalo permitido por los nuevos rangos")
            if rango_minimo:
                if jugador["puntuacion"] < rango_minimo.puntos_minimos:
                    raise PermissionError("Hay jugadores en la partida que se encuentran fuera del intervalo permitido por los nuevos rangos")

def get_partida_como_jugador(actor, partida_id):
    """
    Devuelve la partida con el ID especificado si el actor es un jugador de la misma.
    """

    if not get_jugador_participa_en_partida(partida_id, actor.id):
        raise PermissionError("No tienes permiso para ver esta partida")
    
    partida = Partida.objects.filter(id=partida_id).first()
    if not partida:
        raise ValueError("La partida no existe")
    
    return partida

def get_jugadores_partida(actor, partida_id):
    """
    Devuelve una lista de los jugadores que están actualmente en la partida.
    """

    if not actor.is_authenticated:
        raise PermissionError("No tienes permiso para ver los jugadores de esta partida")
    
    jugadores = get_jugadores_actuales_de_partida(partida_id)
    if jugadores is None:
        raise ValueError("La partida no existe")

    partida = get_partida_by_id(partida_id).first()
    if partida is None:
        raise ValueError("La partida no existe")
    if partida.fecha_inicio is not None: # Si la partida ha comenzado NO se deben mostrar datos secretos de los jugadores
        for jugador in jugadores:
            jugador["ticket"] = None
            jugador["cartas"] = []
            jugador["carta_comodin"] = None
            jugador["eff_acum_monedero"] = 0
    
    return jugadores

def get_partida_jugador(actor, partida_id):
    """
    Devuelve la relación entre el jugador y la partida si el jugador está participando en la misma.
    """

    if not actor.is_authenticated:
        raise PermissionError("No tienes permiso para ver esta partida")
    
    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario or partida_usuario.abandono:
        raise ValueError("No estás participando en esta partida")
    
    return partida_usuario

def abandonar_partida_sala_espera(actor, partida_id):
    """
    Permite a un jugador abandonar una partida en la que está participando.
    """
    
    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario or partida_usuario.abandono:
        raise ValueError("No estás participando en esta partida")
    if partida_usuario.creador:
        aux_asignar_nuevo_creador(partida_id, actor.id)
    
    partida_usuario.delete()

    if get_jugadores_actuales_de_partida_count(partida_id) <= 0:
        partida = get_partida_by_id(partida_id).first()
        if partida:
            partida.delete()

def aux_asignar_nuevo_creador(partida_id, usuario_id):
    """
    Asigna un nuevo creador a la partida si el creador actual abandona la misma.
    """

    partida = get_partida_by_id(partida_id).first()
    if not partida:
        raise ValueError("La partida no existe")
    
    jugadores = get_jugadores_actuales_de_partida(partida_id)
    if not jugadores:
        return
    
    nuevo_creador = None
    for jugador in jugadores:
        if jugador["id"] != usuario_id:
            nuevo_creador = jugador
            break
    
    if not nuevo_creador:
        return
    
    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, nuevo_creador["id"])
    if not partida_usuario or partida_usuario.abandono:
        raise ValueError("El nuevo creador no está participando en esta partida")
    
    partida_usuario.creador = True
    partida_usuario.save()

def unirse_a_partida_publica(actor, partida_id):
    """
    Permite a un jugador unirse a una partida pública en la que aún hay plazas disponibles.
    """

    if not actor.is_authenticated:
        raise PermissionError("No tienes permiso para unirte a esta partida")
    
    partida = get_partida_by_id(partida_id).first()
    if not partida:
        raise ValueError("La partida no existe")
    
    if get_jugador_participa_en_partida(partida_id, actor.id):
        raise ValueError("Ya estás participando en esta partida")
    
    jugadores_actuales = get_jugadores_actuales_de_partida_count(partida_id)
    if jugadores_actuales >= partida.num_jugadores:
        raise ValueError("La partida ya está llena")
    
    rango_minimo_puntos = partida.rango_minimo.puntos_minimos if partida.rango_minimo else None
    rango_maximo_puntos = partida.rango_maximo.puntos_maximos if partida.rango_maximo else None
    if rango_minimo_puntos is not None and actor.puntuacion < rango_minimo_puntos:
        raise PermissionError("Tu rango es demasiado bajo para unirte a esta partida")
    if rango_maximo_puntos is not None and actor.puntuacion > rango_maximo_puntos:
        raise PermissionError("Tu rango es demasiado alto para unirte a esta partida")
    
    if get_usuario_participa_en_partida_activa(actor.id):
        raise ValueError("Ya estás participando en una partida activa")
    
    # Asignacion de color dentro de la partida
    color = aux_asignar_color_disponible(partida.id)

    # Asignacion de creador si no hay ninguno en la partida
    creador = aux_asignar_creador_si_no_hay(partida.id)
    
    partida_usuario = PartidaUsuario(
        partida=partida,
        usuario=actor,
        creador=creador,
        color=color
    )
    
    try:
        partida_usuario.save()
    except IntegrityError:
        raise RegistrationError({"detail": ["No se pudo unir a la partida"]})
    
def unirse_a_partida_privada(actor, clave):
    """
    Permite a un jugador unirse a una partida privada con la clave correcta.
    """

    if not actor.is_authenticated:
        raise PermissionError("No tienes permiso para unirte a esta partida")
    
    partida = get_partida_by_clave(clave).first()
    if not partida:
        raise ValueError("La partida no existe. Revisa que la clave sea correcta")
    
    if get_jugador_participa_en_partida(partida.id, actor.id):
        raise ValueError("Ya estás participando en esta partida")
    
    jugadores_actuales = get_jugadores_actuales_de_partida_count(partida.id)
    if jugadores_actuales >= partida.num_jugadores:
        raise ValueError("La partida ya está llena")
    
    rango_minimo_puntos = partida.rango_minimo.puntos_minimos if partida.rango_minimo else None
    rango_maximo_puntos = partida.rango_maximo.puntos_maximos if partida.rango_maximo else None
    if rango_minimo_puntos is not None and actor.puntuacion < rango_minimo_puntos:
        raise PermissionError("Tu rango es demasiado bajo para unirte a esta partida")
    if rango_maximo_puntos is not None and actor.puntuacion > rango_maximo_puntos:
        raise PermissionError("Tu rango es demasiado alto para unirte a esta partida")
    
    if get_usuario_participa_en_partida_activa(actor.id):
        raise ValueError("Ya estás participando en una partida activa")
    
    # Asignacion de color dentro de la partida
    color = aux_asignar_color_disponible(partida.id)

    # Asignacion de creador si no hay ninguno en la partida
    creador = aux_asignar_creador_si_no_hay(partida.id)

    partida_usuario = PartidaUsuario(
        partida=partida,
        usuario=actor,
        creador=creador,
        color=color
    )
    
    try:
        partida_usuario.save()
    except IntegrityError:
        raise RegistrationError({"detail": ["No se pudo unir a la partida"]})
    
def aux_asignar_color_disponible(partida_id):
    """
    Asigna un color disponible a un jugador que se une a la partida.
    """

    colores_disponibles = get_colores_disponibles(partida_id)
    if colores_disponibles:
        return colores_disponibles[0]
    else:
        raise ValueError("No hay colores disponibles para unirte a la partida")
    
def aux_asignar_creador_si_no_hay(partida_id):
    """
    Asigna el rol de creador a un jugador si no hay ningún creador en la partida.
    """

    if not get_creador_de_partida(partida_id):
        creador = True
    else:
        creador = False
    
    return creador

def toggle_listo(actor, partida_id):
    """
    Permite a un jugador marcarse como listo/no listo en una partida en la que está participando.
    """

    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario or partida_usuario.abandono:
        raise ValueError("No estás participando en esta partida")
    
    if partida_usuario.listo:
        partida_usuario.listo = False
    else:
        partida_usuario.listo = True
    partida_usuario.save()

def expulsar_jugador(actor, partida_id, jugador_id):
    """
    Permite al creador de la partida expulsar a un jugador de la misma.
    """

    partida_usuario_actor = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario_actor or not partida_usuario_actor.creador:
        raise PermissionError("No tienes permiso para expulsar jugadores de esta partida")
    
    partida_usuario_jugador = get_partida_usuario_by_partida_and_usuario(partida_id, jugador_id)
    if not partida_usuario_jugador:
        raise ValueError("El jugador no está participando en esta partida")
    
    if partida_usuario_jugador.creador:
        raise ValueError("No puedes expulsar al creador de la partida")
    
    partida = get_partida_by_id(partida_id).first()
    if not partida:
        raise ValueError("La partida no existe")
    if partida.fecha_inicio is not None:
        raise ValueError("No puedes expulsar jugadores de una partida que ya ha comenzado")
    
    partida_usuario_jugador.delete()

def iniciar_partida(actor, partida_id, manual=False):
    """
    Permite al creador de la partida iniciar la misma si todos los jugadores están listos.
    """

    partida_usuario_actor = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario_actor or not partida_usuario_actor.creador:
        raise PermissionError("No tienes permiso para iniciar esta partida")

    partida = get_partida_by_id(partida_id).first()
    if not partida:
        raise ValueError("La partida no existe")

    partida_usuario_actor = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario_actor or not partida_usuario_actor.creador:
        raise PermissionError("No tienes permiso para iniciar esta partida")

    jugadores_conectados = get_jugadores_actuales_de_partida_count(partida_id)
    if jugadores_conectados < partida.num_jugadores:
        raise ValueError(f"No hay suficientes jugadores para iniciar la partida, se necesitan {partida.num_jugadores}.")

    jugadores = get_jugadores_actuales_de_partida(partida_id)
    if manual == False:
        for jugador in jugadores:
            if not jugador["listo"]:
                raise ValueError("Todos los jugadores deben estar listos para iniciar la partida")
    
    if partida.fecha_inicio is not None:
        raise ValueError("La partida ya ha comenzado")
    
    # Partida
    partida.fecha_inicio = timezone.now()
    partida.baraja = aux_generar_baraja_inicial(partida.cartas_especiales, partida.num_jugadores)
    partida.disposicion_jugadores = aux_generar_disposicion_jugadores(partida_id)

    # Mano
    mano = Mano(
        partida=partida,
        num=1
    )

    # Ronda
    ronda = Ronda(
        mano=mano,
        num=0
    )

    partida.save()
    mano.save()
    create_resumen_mano(partida_id)
    ronda.save()

    repartir_cartas(actor, partida_id)  # Reparte las cartas a los jugadores al iniciar la partida


def _serializar_posiciones_para_resumen(posiciones):
    """
    Reduce las posiciones finales a campos primitivos aptos para JSON y frontend.
    """
    posiciones_serializadas = {}

    for pos, jugadores_pos in posiciones.items():
        posiciones_serializadas[pos] = []

        for jugador in jugadores_pos:
            if isinstance(jugador, dict):
                posiciones_serializadas[pos].append({
                    "id": jugador.get("id"),
                    "nombre": jugador.get("nombre"),
                    "color": jugador.get("color"),
                    "puntos": jugador.get("puntos"),
                })
            else:
                posiciones_serializadas[pos].append({
                    "id": getattr(jugador, "id", None),
                    "nombre": getattr(jugador, "nombre", None),
                    "color": getattr(jugador, "color", None),
                    "puntos": getattr(jugador, "puntos", None),
                })

    return posiciones_serializadas


def _calcular_resumen_kills_deaths(jugadores):
    """
    Calcula un resumen no destructivo de puntos por kills/deaths.
    """
    puntos_ganados_por_kills = {}
    puntos_perdidos_por_deaths = {}

    for jugador in jugadores:
        color = jugador.get("color") if isinstance(jugador, dict) else getattr(jugador, "color", None)
        acumulador_kills = jugador.get("acumulador_kills", 0) if isinstance(jugador, dict) else getattr(jugador, "acumulador_kills", 0)
        acumulador_deaths = jugador.get("acumulador_deaths", 0) if isinstance(jugador, dict) else getattr(jugador, "acumulador_deaths", 0)

        if color is None:
            continue

        puntos_ganados_por_kills[color] = acumulador_kills // 2
        puntos_perdidos_por_deaths[color] = acumulador_deaths // 4

    return puntos_ganados_por_kills, puntos_perdidos_por_deaths


def _calcular_puntuacion_ganada_por_jugadores(partida, posiciones):
    """
    Calcula la puntuación global ganada por posición final.
    """
    puntuacion_ganada = {}

    if not (partida.cartas_especiales and partida.tickets):
        return puntuacion_ganada

    n = partida.num_jugadores
    m = get_manos_de_partida(partida.id).count()
    for pos, jugadores_pos in posiciones.items():
        for jugador in jugadores_pos:
            puntuable = (n > pos) and int(jugador["puntos"]) > -1000
            color = jugador["color"] if isinstance(jugador, dict) else jugador.color
            puntuacion_ganada[color] = (((n / pos) * 100) + (m*5)) if puntuable else 0

    return puntuacion_ganada

def finalizar_partida(actor, partida_id):
    """
    Finaliza la partida y determina el ganador.
    """
    partida = get_partida_by_id(partida_id).first()
    if not partida:
        raise ValueError("Partida no encontrada.")
    partida_jugador_actor = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_jugador_actor:
        raise PermissionError("No tienes permiso para finalizar esta partida.")
    mano_actual = get_mano_actual(partida_id)
    if mano_actual.num < partida.get_num_manos() and get_jugadores_no_abandono(actor, partida_id) > 1:
        raise ValueError("No se puede finalizar la partida antes de que se jueguen todas las manos.")

    if partida.fecha_fin is not None:
        jugadores = get_jugadores_actuales_de_partida(partida_id)
        posiciones = aux_fin_partida_posiciones(jugadores)
        puntos_ganados_por_kills, puntos_perdidos_por_deaths = _calcular_resumen_kills_deaths(jugadores)
        puntuacion_ganada = _calcular_puntuacion_ganada_por_jugadores(partida, posiciones)
        return {
            "puntos_ganados_por_kills": puntos_ganados_por_kills,
            "puntos_perdidos_por_deaths": puntos_perdidos_por_deaths,
            "posiciones": _serializar_posiciones_para_resumen(posiciones),
            "puntuacion_ganada_por_jugadores": puntuacion_ganada,
        }

    jugadores = get_jugadores_actuales_de_partida(partida_id)

    datos_puntos_finales = aux_fin_partida_mod_puntos(partida_id, jugadores)

    posiciones = aux_fin_partida_posiciones(jugadores)

    # Actualizar puntuación de los usuarios si la partida tiene cartas especiales y tickets
    puntuacion_ganada = _calcular_puntuacion_ganada_por_jugadores(partida, posiciones)
    partida.puntuacion_asignada_final = puntuacion_ganada
    if partida.cartas_especiales and partida.tickets:
        for pos, jugadores_pos in posiciones.items():
            for jugador in jugadores_pos:
                color = jugador["color"] if isinstance(jugador, dict) else jugador.color
                partida_usuario = get_partida_usuario_by_partida_and_color(partida_id, color)
                usuario = partida_usuario.usuario
                n = partida.num_jugadores
                puntuacion_del_jugador = puntuacion_ganada.get(color, 0)
                if n > pos:
                    usuario.puntuacion += puntuacion_del_jugador
                    usuario.save()

    # Guardar la fecha de finalización de la partida y limipiar turno actual para evitar acciones de juego
    partida.fecha_fin = timezone.now()
    partida.turno_actual = None
    # Limpiar otros atributos
    partida.baraja = []
    # Guardar partida
    partida.save()

    # Recopilacion de datos para mostrar en front
    res = {
        "puntos_ganados_por_kills": datos_puntos_finales["puntos_ganados_por_kills"],
        "puntos_perdidos_por_deaths": datos_puntos_finales["puntos_perdidos_por_deaths"],
        "posiciones": _serializar_posiciones_para_resumen(posiciones),
        "puntuacion_ganada_por_jugadores": puntuacion_ganada,
    }
    if "jug_as_extranjero" in datos_puntos_finales:
        res["jug_as_extranjero"] = datos_puntos_finales["jug_as_extranjero"]
        res["puntuacion_extra_jug_as_extranjero"] = datos_puntos_finales["puntuacion_extra_jug_as_extranjero"]

    # Comprobar si partida pertenece a torneo y actuar en consecuencia
    partida_torneo = get_partida_torneo_by_partida_id(partida_id)
    if partida_torneo:
        aux_almacenar_posiciones_finales_partida_torneo(partida_id)

    return res

def abandonar_partida(actor, partida_id):
    """
    Permite a un jugador abandonar una partida en la que está participando.
    """

    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    partida = get_partida_by_id(partida_id).first()
    if partida.fecha_inicio is None:
        raise ValueError("No puedes abandonar una partida que aún no ha comenzado. Debes abandonar la sala de espera")
    if not partida_usuario or partida_usuario.abandono:
        raise ValueError("No estás participando en esta partida")

    partida_usuario.puntos = -1000
    partida_usuario.abandono = True

    # Devolver cartas a la baraja
    cartas_del_usuario = []
    for carta in partida_usuario.cartas:
        cartas_del_usuario.append(carta)
    if partida_usuario.carta_comodin is not None:
        cartas_del_usuario.append(partida_usuario.carta_comodin)
    partida_usuario.cartas = []
    partida_usuario.carta_comodin = None
    partida_usuario.save()
    partida.baraja.extend(cartas_del_usuario)
    partida.save(update_fields=["baraja"])
    

    if partida.turno_actual == partida_usuario.color:
        mano_actual = get_mano_actual(partida_id)
        ronda_actual = get_rondas_de_mano(mano_actual.id)[-1]
        aux_siguiente_turno(partida)
        primer_jugador_activo = obtener_primer_jugador_activo(partida)
        if partida.turno_actual == primer_jugador_activo:
            if ronda_actual.num == 0:
                if ronda_actual.cambios == 0:
                    ronda_actual.cambios = 1
                    ronda_actual.save(update_fields=["cambios"])
                elif ronda_actual.cambios == 1:
                    ronda_actual.cambios = 0
                    ronda_actual.save(update_fields=["cambios"])
                elif ronda_actual.cambios == 2:
                    ronda_nueva = Ronda(mano=get_mano_actual(partida_id), num=1, cartas={}, cambios=2)
                    ronda_nueva.save()
            else:
                ronda_nueva = Ronda(mano=get_mano_actual(partida_id), num=1, cartas={}, cambios=2)
                ronda_nueva.save()

def get_jugadores_no_abandono(actor, partida_id):
    """
    Devuelve una lista de los jugadores que no han abandonado la partida.
    """

    if not actor.is_authenticated:
        raise PermissionError("No tienes permiso para ver cuántos jugadores no han abandonado esta partida")
    
    jugadores = get_jugadores_no_abandono_de_partida(partida_id)
    
    return jugadores