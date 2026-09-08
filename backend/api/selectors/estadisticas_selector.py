

from ..selectors.resumen_mano_selector import get_resumen_mano_by_mano_id

from ..selectors.mano_selector import get_manos_de_partida

from ..selectors.partida_selector import get_jugadores_actuales_de_partida

from ..models.mano import Mano

from ..models.partida import Partida


def get_estadisticas_glob_partidas_totales():
    cant_partidas = Partida.objects.count()
    return cant_partidas

def get_estadisticas_glob_partidas_en_sala_espera():
    cant_partidas = Partida.objects.filter(fecha_inicio__isnull=True).count()
    return cant_partidas

def get_estadisticas_glob_partidas_en_curso():
    cant_partidas = Partida.objects.filter(fecha_inicio__isnull=False, fecha_fin__isnull=True).count()
    return cant_partidas

def get_estadisticas_glob_partidas_finalizadas():
    cant_partidas = Partida.objects.filter(fecha_fin__isnull=False).count()
    return cant_partidas

def get_estadisticas_glob_manos_jugadas():
    cant_manos = Mano.objects.count()
    return cant_manos

def get_estadisticas_glob_mas_puntos_en_partida():
    partidas_finalizadas = Partida.objects.filter(fecha_fin__isnull=False)
    if not partidas_finalizadas.exists():
        return None
    puntos = 0
    jugador = None
    for p in partidas_finalizadas:
        for j in get_jugadores_actuales_de_partida(p.id):
            if j["puntos"] > puntos:
                puntos = j["puntos"]
                jugador = j["nombre"]
    return (jugador, puntos) if jugador else (None, 0)

def get_estadisticas_glob_cartas_matadas():
    partidas_finalizadas = Partida.objects.filter(fecha_fin__isnull=False)
    if not partidas_finalizadas.exists():
        return None
    cartas_matadas = 0
    for p in partidas_finalizadas:
        for mano in get_manos_de_partida(p.id):
            resumen = get_resumen_mano_by_mano_id(mano.id)
            if resumen:
                dic_muertes = resumen.muertes
                cartas_matadas += len(dic_muertes.keys())
    return cartas_matadas

def get_estadisticas_glob_mas_cartas_matadas_en_partida():
    partidas_finalizadas = Partida.objects.filter(fecha_fin__isnull=False)
    if not partidas_finalizadas.exists():
        return None
    cartas_matadas = 0
    jugador = None
    for p in partidas_finalizadas:
        for j in get_jugadores_actuales_de_partida(p.id):
            cartas_matadas_en_partida_por_jugador = 0
            for mano in get_manos_de_partida(p.id):
                resumen = get_resumen_mano_by_mano_id(mano.id)
                if resumen:
                    dic_muertes = resumen.muertes
                    for ronda, (matador,matado) in dic_muertes.items():
                        if matador == j["color"]:
                            cartas_matadas_en_partida_por_jugador += 1
            if cartas_matadas_en_partida_por_jugador > cartas_matadas:
                cartas_matadas = cartas_matadas_en_partida_por_jugador
                jugador = j["nombre"]
    return (jugador, cartas_matadas) if jugador else (None, 0)

def get_estadisticas_glob_retiradas():
    partidas_finalizadas = Partida.objects.filter(fecha_fin__isnull=False)
    if not partidas_finalizadas.exists():
        return None
    retiradas = 0
    for p in partidas_finalizadas:
        for mano in get_manos_de_partida(p.id):
            resumen = get_resumen_mano_by_mano_id(mano.id)
            if resumen:
                dic_retiradas = resumen.retiradas
                for ronda, retiradas_ronda in dic_retiradas.items():
                    retiradas += len(retiradas_ronda)
    return retiradas

def get_estadisticas_glob_mas_retiradas_en_partida():
    partidas_finalizadas = Partida.objects.filter(fecha_fin__isnull=False)
    if not partidas_finalizadas.exists():
        return None
    retiradas = 0
    jugador = None
    for p in partidas_finalizadas:
        for j in get_jugadores_actuales_de_partida(p.id):
            retiradas_en_partida_por_jugador = 0
            for mano in get_manos_de_partida(p.id):
                resumen = get_resumen_mano_by_mano_id(mano.id)
                if resumen:
                    dic_retiradas = resumen.retiradas
                    for ronda, retiradas_ronda in dic_retiradas.items():
                        if j["color"] in retiradas_ronda:
                            retiradas_en_partida_por_jugador += 1
                            break # Un jugador sólo puede retirarse una vez por mano, no hace falta seguir buscando
            if retiradas_en_partida_por_jugador > retiradas:
                retiradas = retiradas_en_partida_por_jugador
                jugador = j["nombre"]
    return (jugador, retiradas) if jugador else (None, 0)

def get_estadisticas_glob_partida_mas_larga():
    partidas_finalizadas = Partida.objects.filter(fecha_fin__isnull=False)
    if not partidas_finalizadas.exists():
        return None
    duracion_maxima = 0.
    partida_mas_larga = None
    for p in partidas_finalizadas:
        duracion = (p.fecha_fin - p.fecha_inicio).total_seconds()
        if duracion > duracion_maxima:
            duracion_maxima = duracion
            partida_mas_larga = p
    return (partida_mas_larga.nombre, duracion_maxima) if partida_mas_larga else (None, 0)

def get_estadisticas_glob_partida_mas_corta():
    partidas_finalizadas = Partida.objects.filter(fecha_fin__isnull=False)
    if not partidas_finalizadas.exists():
        return None
    duracion_minima = 0.
    partida_mas_corta = None
    for p in partidas_finalizadas:
        duracion = (p.fecha_fin - p.fecha_inicio).total_seconds()
        if duracion < duracion_minima:
            duracion_minima = duracion
            partida_mas_corta = p
    return (partida_mas_corta.nombre, duracion_minima) if partida_mas_corta else (None, 0)
