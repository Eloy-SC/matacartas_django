from ..services.resumen_mano_service import recopilar_efecto_extra_fin_mano, recopilar_efecto_inmediato_ronda, recopilar_puntos_extra, recopilar_retirada, recopilar_victoria, recopilar_muerte

from ..models.catalogo_cartas import CATALOGO

from ..models.ronda import Ronda

from ..selectors.ronda_selector import get_carta_equivalente, get_cartas_lanzadas_en_mano, get_cartas_lanzadas_en_mano_hasta_ronda, get_cartas_lanzadas_en_mano_por_jugador, get_cartas_matadoras_de_carta_equivalente, get_jugador_lanzador_carta_mayor_fuerza, get_rondas_de_mano

from ..utils.funciones_aux import aux_siguiente_turno, obtener_primer_jugador_activo

from ..selectors.mano_selector import get_mano_actual

from ..selectors.partida_selector import get_jugadores_actuales_de_partida, get_partida_by_id, get_partida_usuario_by_partida_and_color, get_partida_usuario_by_partida_and_usuario


def jugar_carta(user, partida_id, carta):
    """
    Lógica para que un jugador juegue una carta en la partida.
    """
    partida = get_partida_by_id(partida_id).first()
    if not partida:
        raise ValueError("Partida no encontrada.")
    
    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, user.id)
    if not partida_usuario or partida_usuario.abandono:
        raise PermissionError("No participas en la partida.")
    if partida.turno_actual != partida_usuario.color:
        raise PermissionError("No es tu turno para jugar.")
    
    mano = get_mano_actual(partida_id)
    ronda_actual = get_rondas_de_mano(mano.id)[-1]  # Obtener la ult ronda de la mano actual

    if carta not in partida_usuario.cartas:
        raise ValueError("No tienes esa carta en tu mano.")
    if carta in ronda_actual.cartas.values():
        raise ValueError("Esa carta ya ha sido jugada en esta ronda.")
    
    # Registrar la carta jugada
    ronda_actual.cartas[partida_usuario.color] = carta
    ronda_actual.save()

    partida_usuario.cartas.remove(carta)
    partida_usuario.save()

    aux_siguiente_turno(partida)  # Avanzar al siguiente turno
    if partida.turno_actual == obtener_primer_jugador_activo(partida):  # Si el turno vuelve al primer jugador activo, iniciar nueva ronda
        ganador_ronda(partida_id)  # Determinar ganador de la ronda y preparar la siguiente

    mano_actualizada = get_mano_actual(partida_id)
    if mano_actualizada and mano_actualizada.ganador is not None:
        return True  # Indica que la mano ha terminado
    else:
        return False  # Indica que la mano sigue en curso

def ganador_ronda(partida_id):

    # Detectar si hay especiales y asignar puntos (extra) inmediatos
    mano_actual = get_mano_actual(partida_id)
    ronda_actual = get_rondas_de_mano(mano_actual.id)[-1]
    cartas_jugadas = ronda_actual.cartas

    # Detectar si no hay cartas porque todos menos uno se han retirado antes de lanzar carta
    if len(cartas_jugadas) == 0:
        # Buscar el jugador que no se ha retirado
        jugadores = get_jugadores_actuales_de_partida(partida_id)
        jugador_no_retirado = next((jugador for jugador in jugadores if not jugador["retirado"]), None)
        if jugador_no_retirado:
            ronda_actual.ganador = jugador_no_retirado["color"]
            ronda_actual.save()
            recopilar_victoria(mano_actual.id, jugador_no_retirado["color"], "RETIRADAS", ronda_actual.num)
            aux_siguiente_ronda(partida_id)
            return
        else:
            raise ValueError("No hay jugadores válidos para determinar el ganador de la ronda.")

    especiales = False
    for carta in cartas_jugadas.values():
        if CATALOGO[carta]["tipo"].startswith("especial"):
            especiales = True
            break
    if especiales:
        aux_asignar_puntos_inmediatos_por_cartas_especiales(partida_id)

    # Determinar la carta de mayor fuerza y sus cartas matadoras
    carta_mayor_fuerza = aux_get_carta_mayor_fuerza(partida_id)
    cartas_matadoras = aux_get_cartas_matadoras(carta_mayor_fuerza, partida_id)
    # Lanzador de la carta de mayor fuerza
    lanzador_carta_mayor_fuerza = next(
        (jugador for jugador, carta in cartas_jugadas.items()
        if carta == carta_mayor_fuerza),
        None
    )

    # Buscar cartas especiales lanzadas
    cartas_especiales = []
    for c in cartas_jugadas.values():
        if CATALOGO[c]["tipo"].startswith("especial"):
            cartas_especiales.append(c)

    # Comprobacion de la carta Martirizado y su efecto, debe haber otra carta especial lanzada
    if any(carta == "MARTIRIZADO" for carta in cartas_especiales) and len(cartas_especiales) >= 2:
        lanzador_martirizado = next(
            (jugador for jugador, carta in cartas_jugadas.items()
            if carta == "MARTIRIZADO"),
            None
        )
        cartas_especiales.remove("MARTIRIZADO") # Así no se cuenta la carta del Martirizado para determinar la de mayor fuerza
        carta_mayor_especial = aux_get_carta_mayor_fuerza_de_conj(partida_id, cartas_especiales)
        lanzador_mayor_especial = next(
            (jugador for jugador, carta in cartas_jugadas.items()
            if carta == carta_mayor_especial),
            None
        )
        aux_producir_efecto_muerte(partida_id, lanzador_martirizado, lanzador_mayor_especial)
        ronda_actual.ganador = lanzador_martirizado
        ronda_actual.save()
        recopilar_victoria(mano_actual.id, lanzador_martirizado, "MARTIRIZADO", ronda_actual.num)

    # Comprobacion de carta de bastos puntiagudos
    elif carta_mayor_fuerza.endswith("_BASTOS_PUNTIAGUDOS"):
        cartas_matadoras_de_bastos = get_cartas_matadoras_de_carta_equivalente(carta_mayor_fuerza)
        cartas_matadoras_en_ronda = [carta for carta in cartas_matadoras_de_bastos if carta in cartas_jugadas.values()]
        if len(cartas_matadoras_en_ronda) > 0:
            lanzador_carta_asesina = next(
                (jugador for jugador, carta in cartas_jugadas.items()
                if carta == cartas_matadoras_en_ronda[-1]),  # La carta matadora de mayor fuerza, pues en el catalogo ya están ordenadas así
                None
            )
            if not any(carta == "CORRUPTOR" for carta in cartas_jugadas.values()):
                # En este caso la carta de mas fuerza es la que mata porque hace contraataque al ser de bastos puntiagudos
                aux_producir_efecto_muerte(partida_id, lanzador_carta_mayor_fuerza, lanzador_carta_asesina)
                ronda_actual.ganador = lanzador_carta_mayor_fuerza
                ronda_actual.save()
                recopilar_victoria(mano_actual.id, lanzador_carta_mayor_fuerza, "CONTRAATAQUE", ronda_actual.num)
            else:
                # Lo mismo, pero si hay corruptor es el el que recibe la recompensa y la muerte
                aux_producir_efecto_muerte(partida_id, lanzador_carta_mayor_fuerza, lanzador_carta_asesina, corruptor=True)
                lanzador_corruptor = next(
                    (jugador for jugador, carta in cartas_jugadas.items()
                    if carta == "CORRUPTOR"),
                    None
                )
                ronda_actual.ganador = lanzador_corruptor
                ronda_actual.save()
                recopilar_victoria(mano_actual.id, lanzador_corruptor, "CORRUPTOR", ronda_actual.num)
        else:
            # No hay cartas matadoras, gana el jugador que lanzó la carta de mayor fuerza
            ronda_actual.ganador = lanzador_carta_mayor_fuerza
            ronda_actual.save()
            recopilar_victoria(mano_actual.id, lanzador_carta_mayor_fuerza, "MAYOR_FUERZA", ronda_actual.num)
    elif len(cartas_matadoras) > 0:
        lanzador_carta_asesina = next(
            (jugador for jugador, carta in cartas_jugadas.items()
            if carta == cartas_matadoras[-1]),  # La carta matadora de mayor fuerza, pues en el catalogo ya están ordenadas así
            None
        )
        if not any(carta == "CORRUPTOR" for carta in cartas_jugadas.values()):
            aux_producir_efecto_muerte(partida_id, lanzador_carta_asesina, lanzador_carta_mayor_fuerza)
            ronda_actual.ganador = lanzador_carta_asesina
            recopilar_victoria(mano_actual.id, lanzador_carta_asesina, "MUERTE", ronda_actual.num)
        else:
            aux_producir_efecto_muerte(partida_id, lanzador_carta_asesina, lanzador_carta_mayor_fuerza, corruptor=True)
            lanzador_corruptor = next(
                (jugador for jugador, carta in cartas_jugadas.items()
                if carta == "CORRUPTOR"),
                None
            )
            ronda_actual.ganador = lanzador_corruptor
            recopilar_victoria(mano_actual.id, lanzador_corruptor, "CORRUPTOR", ronda_actual.num)
        ronda_actual.save()
    else: # Si no hay muerte de ningun tipo, gana directamente el jugador que lanzó la carta de mayor fuerza
        ronda_actual.ganador = lanzador_carta_mayor_fuerza
        ronda_actual.save()
        recopilar_victoria(mano_actual.id, lanzador_carta_mayor_fuerza, "MAYOR_FUERZA", ronda_actual.num)

    # Siguiente ronda
    aux_siguiente_ronda(partida_id)
    

def aux_siguiente_ronda(partida_id):
    ronda_actual = get_rondas_de_mano(get_mano_actual(partida_id).id)[-1]
    num_ronda = ronda_actual.num
    if num_ronda < 3:
        nueva_ronda = Ronda(mano=get_mano_actual(partida_id), num=num_ronda + 1, cartas={}, cambios=2)
        nueva_ronda.save()
    else: # Fin de la mano en caso de que se haya jugado la tercera ronda
        aux_resolver_ganador_mano(partida_id)

def retirarse_de_mano(actor, partida_id):
    """
    Permite a un jugador retirarse de la mano actual.
    """
    partida_usuario = get_partida_usuario_by_partida_and_usuario(
        partida_id,
        actor.id
    )

    if not partida_usuario or partida_usuario.abandono:
        raise PermissionError("No participas en la partida.")

    partida = get_partida_by_id(partida_id).first()

    if not partida:
        raise ValueError("Partida no encontrada.")

    if partida_usuario.color != partida.turno_actual:
        raise PermissionError("No es tu turno.")

    # Guardamos quién era el primer jugador activo ANTES de retirarse
    primer_jugador_activo = obtener_primer_jugador_activo(partida)

    partida_usuario.retirado = True
    partida_usuario.puntos -= 1
    partida_usuario.save()

    # Recopilar retirada
    mano_actual = get_mano_actual(partida_id)
    ronda_actual = get_rondas_de_mano(mano_actual)[-1]
    recopilar_retirada(mano_actual.id, ronda_actual.num, partida_usuario.color)

    cantidad_retirados = 0
    jugadores = get_jugadores_actuales_de_partida(partida_id)

    for jugador in jugadores:
        if jugador["retirado"]:
            cantidad_retirados += 1

    if cantidad_retirados == len(jugadores) - 1:
        # Solo queda un jugador activo: gana la mano
        for jugador in jugadores:
            if not jugador["retirado"]:
                mano_actual.ganador = jugador["color"]
                mano_actual.save()

                ganador_usuario = get_partida_usuario_by_partida_and_color(
                    partida_id,
                    jugador["color"]
                )

                ganador_usuario.puntos += 4
                ganador_usuario.save()

                # Recopilar victoria
                recopilar_victoria(mano_actual.id, ganador_usuario.color, "RETIRADAS", ronda_actual.num)

                aux_asignar_puntos_extra_final_mano(partida_id)
                aux_asignar_puntos_extra_ganador_mano(
                    partida_id,
                    jugador["color"]
                )
                return True  # Indica que la mano ha terminado

    else:
        aux_siguiente_turno(partida)

        if partida.turno_actual == primer_jugador_activo:
            ganador_ronda(partida_id)

## ESTAS FUNCIONES QUIZAS ESTARÍAN MEJOR EN RONDA_SELECTOR
def aux_get_carta_mayor_fuerza(partida_id):
    ronda_actual = get_rondas_de_mano(get_mano_actual(partida_id).id)[-1]
    cartas_jugadas = ronda_actual.cartas
    # Comprobar el efecto de la carta Bufón
    if any(carta == "BUFON" for carta in cartas_jugadas.values()):
        cartas_mag_uni = []
        for carta in cartas_jugadas.values():
            if (CATALOGO[carta]["tipo"] == "especial_mag" or CATALOGO[carta]["tipo"] == "especial_uni") \
                and carta != "BUFON":
                cartas_mag_uni.append(carta)
        if len(cartas_mag_uni) == 0:
            return "BUFON"

    cartas_jugadas_fuerza = {
        (nombre, CATALOGO[nombre]["fuerza"])
        for nombre in cartas_jugadas.values()
    }
    carta_mayor_fuerza = max(cartas_jugadas_fuerza, key=lambda x: x[1])
    return carta_mayor_fuerza[0]

def aux_get_carta_mayor_fuerza_de_conj(partida_id, conjunto):
    ronda_actual = get_rondas_de_mano(get_mano_actual(partida_id).id)[-1]
    cartas_jugadas_fuerza = {
        (nombre, CATALOGO[nombre]["fuerza"])
        for nombre in ronda_actual.cartas.values()
        if nombre in conjunto
    }
    carta_mayor_fuerza = max(cartas_jugadas_fuerza, key=lambda x: x[1])
    return carta_mayor_fuerza[0]


def aux_get_cartas_matadoras(carta, partida_id):

    matadoras = CATALOGO[carta].get("matadoras", ())
    res = []
    cartas_jugadas_ronda = get_rondas_de_mano(get_mano_actual(partida_id).id)[-1].cartas
    for c in cartas_jugadas_ronda.values():
        if c in matadoras:
            res.append(c)
    return res
##############

def aux_producir_efecto_muerte(partida_id, matador, matado, corruptor=False):
    jugador_matador = get_partida_usuario_by_partida_and_color(partida_id, matador)
    jugador_matado = get_partida_usuario_by_partida_and_color(partida_id, matado)
    cartas_jugadas = get_rondas_de_mano(get_mano_actual(partida_id).id)[-1].cartas
    carta_matada = next(
        (carta for color, carta in cartas_jugadas.items() if color == matado),
        None
    )
    carta_matadora = next(
        (carta for color, carta in cartas_jugadas.items() if color == matador),
        None
    )

    jugador_matado.acumulador_deaths += 1

    jugador_saqueador = None
    for carta in cartas_jugadas.values():
        if carta == "SAQUEADOR_TUMBAS":
            lanzador_saqueador = next(
                (jugador for jugador, carta in cartas_jugadas.items() if carta == "SAQUEADOR_TUMBAS"),
                None
            )
            jugador_saqueador = get_partida_usuario_by_partida_and_color(partida_id, lanzador_saqueador)
            jugador_saqueador.puntos += 2  # Recompensa por efecto de la carta Saqueador de Tumbas

    if not corruptor:
        jugador_matador.acumulador_kills += 1
        if carta_matadora.endswith("_BASTOS_PUNTIAGUDOS"):
            carta_equivalente = get_carta_equivalente(carta_matadora)
            if jugador_saqueador and jugador_saqueador != jugador_matado:
                jugador_saqueador.puntos += CATALOGO[carta_equivalente]["recompensa"]
            else:
                jugador_matador.puntos += CATALOGO[carta_equivalente]["recompensa"]
        else:
            if jugador_saqueador and jugador_saqueador != jugador_matado:
                jugador_saqueador.puntos += CATALOGO[carta_matada]["recompensa"]
            else:
                jugador_matador.puntos += CATALOGO[carta_matada]["recompensa"]
        jugador_matador.save()
    else:
        lanzador_corruptor = next(
            (jugador for jugador, carta in cartas_jugadas.items() if carta == "CORRUPTOR"),
            None
        )
        jugador_corruptor = get_partida_usuario_by_partida_and_color(partida_id, lanzador_corruptor)
        if jugador_saqueador and jugador_saqueador != jugador_matado:
            jugador_saqueador.puntos += 1
        else:
            jugador_corruptor.puntos += 1
        jugador_corruptor.acumulador_kills += 1
        jugador_corruptor.save()

    mano_actual = get_mano_actual(partida_id)
    ronda_actual = get_rondas_de_mano(mano_actual)[-1]
    if jugador_saqueador and jugador_saqueador != jugador_matado:
        recopilar_efecto_inmediato_ronda(mano_actual.id, ronda_actual.num, jugador_saqueador.color, "SAQUEADOR")
        jugador_saqueador.save()
    
    jugador_matado.save()

    # Recopilar la muerte
    recopilar_muerte(mano_actual.id, ronda_actual.num, matador, matado)

def aux_resolver_ganador_mano(partida_id):
    mano_actual = get_mano_actual(partida_id)
    rondas = get_rondas_de_mano(mano_actual.id)
    especiales = False
    for carta in get_cartas_lanzadas_en_mano(mano_actual.id):
        if CATALOGO[carta]["tipo"].startswith("especial"):
            especiales = True
            break

    ganadores = {}
    for ronda in rondas:
        if ronda.num < 1 or ronda.num > 3 or ronda.ganador is None:
            continue
        ganadores[ronda.ganador] = ganadores.get(ronda.ganador, 0) + 1

    if not ganadores:
        raise ValueError("No hay ganador válido para resolver la mano.")

    max_victorias = max(ganadores.values())
    colores_con_maximo = [color for color, victorias in ganadores.items() if victorias == max_victorias]

    # Si alguien ganó 2 o 3 rondas, gana la mano sin desempate por comodines.
    if max_victorias >= 2:
        ganador_mano = colores_con_maximo[0]
    # Solo hay desempate cuando las tres rondas tienen tres ganadores distintos (1-1-1).
    elif len(colores_con_maximo) == 3: 
        # Si hay desempate, aqui no se asignan puntos extra, eso se hace en la propia función de desempate
        ganador_mano = aux_resolver_desempate_comodines(partida_id, colores_con_maximo, especiales)
    else:
        ganador_mano = colores_con_maximo[0]
    mano_actual.ganador = ganador_mano
    mano_actual.save()

    ganador_usuario = get_partida_usuario_by_partida_and_color(partida_id, ganador_mano)
    ganador_usuario.puntos += 4
    ganador_usuario.save()
    aux_asignar_puntos_extra_final_mano(partida_id)
    aux_asignar_puntos_extra_ganador_mano(partida_id, ganador_mano)

def aux_resolver_desempate_comodines(partida_id, ganadores, especiales):

    ronda_comodines = Ronda(mano=get_mano_actual(partida_id), num=4, cartas={}, cambios=2)
    jugadores = get_jugadores_actuales_de_partida(partida_id)
    for jugador in jugadores:
        if jugador["color"] in ganadores:
            ronda_comodines.cartas[jugador["color"]] = jugador["carta_comodin"]
    ronda_comodines.save()
    comodines_a_usar = {
        (nombre, CATALOGO[nombre]["riqueza"])
        for nombre in ronda_comodines.cartas.values()
    }
    carta_mayor_riqueza = max(comodines_a_usar, key=lambda x: x[1])
    ganador = [color for color, carta in ronda_comodines.cartas.items() if carta == carta_mayor_riqueza[0]][0]

    if especiales:

        # Asignar efecto de As Extranjero si el ganador de la ronda de comodines jugó el As Extranjero
        for color in ganadores:
            if color == ganador and carta_mayor_riqueza[0] == "AS_EXTRANJERO":
                jugador_ganador = get_partida_usuario_by_partida_and_color(partida_id, color)
                jugador_ganador.eff_as_extranjero = True
                jugador_ganador.save()
                for jugador in jugadores:
                    if jugador["eff_as_extranjero"] and jugador["color"] != color:
                        jugador_perdedor = get_partida_usuario_by_partida_and_color(partida_id, jugador["color"])
                        jugador_perdedor.eff_as_extranjero = False
                        jugador_perdedor.save()

    recopilar_victoria(get_mano_actual(partida_id).id, ganador, "DESEMPATE_COMODINES", 4)

    return ganador

def aux_asignar_puntos_inmediatos_por_cartas_especiales(partida_id):
    mano_actual = get_mano_actual(partida_id)
    ronda_actual = get_rondas_de_mano(mano_actual.id)[-1]
    cartas_jugadas = ronda_actual.cartas

    # VINOS VIEJOS
    lanzadores_vinos_viejos = [color for color, carta in cartas_jugadas.items() if carta.endswith("_VINOS_VIEJOS")]
    if lanzadores_vinos_viejos:
        for carta in cartas_jugadas.values():
            if carta.endswith("_COPAS"):
                for color in lanzadores_vinos_viejos:
                    jugador = get_partida_usuario_by_partida_and_color(partida_id, color)
                    jugador.puntos += 2
                    jugador.save()
                    recopilar_efecto_inmediato_ronda(mano_actual.id, ronda_actual.num, color, "VINOS_VIEJOS")
                break

def aux_asignar_puntos_extra_ganador_mano(partida_id, ganador_mano):
    jugador = get_partida_usuario_by_partida_and_color(partida_id, ganador_mano)
    mano_actual = get_mano_actual(partida_id)
    cartas_lanzadas_por_jugador = get_cartas_lanzadas_en_mano_por_jugador(mano_actual.id, ganador_mano)

    # JOYAS REALES
    cartas_joyas = []
    for carta in cartas_lanzadas_por_jugador:
        if carta.endswith("_JOYAS_REALES"):
            cartas_joyas.append(carta)
    if len(cartas_joyas) > 1:
        jugador.puntos += 3
        recopilar_efecto_extra_fin_mano(mano_actual.id, jugador.color, "JOYAS_REALES_3")
    elif len(cartas_joyas) > 0:
        jugador.puntos += 2
        recopilar_efecto_extra_fin_mano(mano_actual.id, jugador.color, "JOYAS_REALES_2")
    jugador.save()

    # CARTAS ÚNICAS
    for carta in cartas_lanzadas_por_jugador:
        if CATALOGO[carta]["tipo"] == "especial_uni":
            jugador.puntos += 4
            recopilar_efecto_extra_fin_mano(mano_actual.id, jugador.color, "CARTA_UNICA")
    jugador.save()

def aux_asignar_puntos_extra_final_mano(partida_id):

    partida = get_partida_by_id(partida_id).first()
    mano_actual = get_mano_actual(partida_id)
    cartas_lanzadas_mano = get_cartas_lanzadas_en_mano(mano_actual.id)

    sufijos_mercancia = ("_OROS", "_JOYAS_REALES", "_COPAS", "_VINOS_VIEJOS")
    sufijos_bastos = ("_BASTOS", "_BASTOS_PUNTIAGUDOS")

    for color in partida.disposicion_jugadores:
        cartas_lanzadas_por_jugador = get_cartas_lanzadas_en_mano_por_jugador(mano_actual.id, color)
        jugador = get_partida_usuario_by_partida_and_color(partida_id, color)
        puntos_extra = 0
        necesita_guardar = False

        # MERCADER
        if any(carta.endswith("MERCADER") for carta in cartas_lanzadas_por_jugador):
            ronda_mercader_lanzado = next(
                index for index, carta in enumerate(cartas_lanzadas_por_jugador, start=1)
                if carta.endswith("MERCADER")
            )
            cartas_lanzadas_mano_hasta_ronda = get_cartas_lanzadas_en_mano_hasta_ronda(mano_actual.id, ronda_mercader_lanzado)
            cartas_mercancias = sum(1 for carta in cartas_lanzadas_mano_hasta_ronda if carta.endswith(sufijos_mercancia))
            puntos_extra += min(cartas_mercancias, 6)
            if cartas_mercancias > 0:
                recopilar_efecto_extra_fin_mano(mano_actual.id, color, "MERCADER")
                recopilar_puntos_extra(mano_actual.id, "MERCADER", min(cartas_mercancias, 6))

        # REBELDE
        if any(carta.endswith("REBELDE") for carta in cartas_lanzadas_por_jugador):
            cartas_bastos = sum(1 for carta in cartas_lanzadas_mano if carta.endswith(sufijos_bastos))
            puntos_extra += min(cartas_bastos, 8)
            if cartas_bastos > 0:
                recopilar_efecto_extra_fin_mano(mano_actual.id, color, "REBELDE")
                recopilar_puntos_extra(mano_actual.id, "REBELDE", min(cartas_bastos, 8))

        # SEGADOR
        if any(carta.endswith("SEGADOR") for carta in cartas_lanzadas_por_jugador):
            cartas_valiosas_lanzadas = sum(1 for carta in cartas_lanzadas_mano if CATALOGO[carta]["tipo"] == "especial_val")
            puntos_extra += min(cartas_valiosas_lanzadas, 6) * 2
            if cartas_valiosas_lanzadas > 0:
                recopilar_efecto_extra_fin_mano(mano_actual.id, color, "SEGADOR")
                recopilar_puntos_extra(mano_actual.id, "SEGADOR", min(cartas_valiosas_lanzadas, 6) * 2)

        # MONEDERO PECULIAR
        if any(carta.endswith("MONEDERO_PECULIAR") for carta in cartas_lanzadas_por_jugador):
            puntos_extra += jugador.eff_acum_monedero
            jugador.eff_acum_monedero = 0
            necesita_guardar = True
            recopilar_efecto_extra_fin_mano(mano_actual.id, color, "MONEDERO")

        if puntos_extra > 0:
            jugador.puntos += puntos_extra
            jugador.save()
        elif necesita_guardar:
            jugador.save()
