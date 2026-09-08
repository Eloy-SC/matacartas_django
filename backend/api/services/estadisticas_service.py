

from ..selectors.estadisticas_selector import get_estadisticas_glob_cartas_matadas, get_estadisticas_glob_manos_jugadas, get_estadisticas_glob_mas_cartas_matadas_en_partida, get_estadisticas_glob_mas_puntos_en_partida, get_estadisticas_glob_mas_retiradas_en_partida, get_estadisticas_glob_partida_mas_corta, get_estadisticas_glob_partida_mas_larga, get_estadisticas_glob_partidas_en_curso, get_estadisticas_glob_partidas_en_sala_espera, get_estadisticas_glob_partidas_finalizadas, get_estadisticas_glob_partidas_totales, get_estadisticas_glob_retiradas, get_estadisticas_ind_cartas_matadas, get_estadisticas_ind_cartas_matadas_en_una_partida, get_estadisticas_ind_muertes_recibibidas, get_estadisticas_ind_muertes_recibibidas_en_una_partida, get_estadisticas_ind_partidas_jugadas, get_estadisticas_ind_puntos_ganados, get_estadisticas_ind_puntos_ganados_en_una_partida, get_estadisticas_ind_retiradas, get_estadisticas_ind_retiradas_en_una_partida


def get_estadisticas_globales(actor):
    """
    Obtiene las estadísticas globales de todas las partidas finalizadas.
    """
    if not actor.is_authenticated:
        raise PermissionError("Usuario no autenticado")

    estadisticas = {
        "partidas_totales": get_estadisticas_glob_partidas_totales(),
        "partidas_en_sala_espera": get_estadisticas_glob_partidas_en_sala_espera(),
        "partidas_en_curso": get_estadisticas_glob_partidas_en_curso(),
        "partidas_finalizadas": get_estadisticas_glob_partidas_finalizadas(),
        "manos_jugadas": get_estadisticas_glob_manos_jugadas(),
        "mas_puntos_en_partida": get_estadisticas_glob_mas_puntos_en_partida(),
        "cartas_matadas": get_estadisticas_glob_cartas_matadas(),
        "mas_cartas_matadas_en_partida": get_estadisticas_glob_mas_cartas_matadas_en_partida(),
        "retiradas": get_estadisticas_glob_retiradas(),
        "mas_retiradas_en_partida": get_estadisticas_glob_mas_retiradas_en_partida(),
        "partida_mas_larga": get_estadisticas_glob_partida_mas_larga(),
        "partidas_mas_corta": get_estadisticas_glob_partida_mas_corta()
    }

    return estadisticas

def get_estadisticas_individuales(actor):
    """
    Obtiene las estadísticas individuales de un usuario.
    """
    if not actor.is_authenticated:
        raise PermissionError("Usuario no autenticado")

    estadisticas = {
        "partidas_jugadas": get_estadisticas_ind_partidas_jugadas(actor.id),
        "cartas_matadas": get_estadisticas_ind_cartas_matadas(actor.id),
        "muertes_recibidas": get_estadisticas_ind_muertes_recibibidas(actor.id),
        "retiradas": get_estadisticas_ind_retiradas(actor.id),
        "puntos_ganados": get_estadisticas_ind_puntos_ganados(actor.id),
        "puntos_ganados_en_una_partida": get_estadisticas_ind_puntos_ganados_en_una_partida(actor.id),
        "cartas_matadas_en_una_partida": get_estadisticas_ind_cartas_matadas_en_una_partida(actor.id),
        "muertes_recibidas_en_una_partida": get_estadisticas_ind_muertes_recibibidas_en_una_partida(actor.id),
        "retiradas_en_una_partida": get_estadisticas_ind_retiradas_en_una_partida(actor.id)
    }

    return estadisticas