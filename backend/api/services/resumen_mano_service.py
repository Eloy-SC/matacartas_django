

from ..models.resumen_mano import ResumenMano
from ..models.mano import Mano
from ..models.dtos import ResumenManoDTO, ResumenRondaDTO

from ..selectors.resumen_mano_selector import get_resumen_mano_by_mano_id

from ..selectors.mano_selector import get_mano_actual

from ..selectors.partida_selector import get_partida_by_id, get_partida_usuario_by_partida_and_usuario


def get_resumen_ult_mano(actor, partida_id):
    """
    Metodo para obtener el resumen de la última mano
    """

    partida_usuario = get_partida_usuario_by_partida_and_usuario(partida_id, actor.id)
    if not partida_usuario or partida_usuario.abandono:
        raise PermissionError("No participas en la partida.")

    partida = get_partida_by_id(partida_id)
    if not partida:
        raise ValueError("La partida no existe")

    mano_actual = get_mano_actual(partida_id)
    if not mano_actual:
        raise ValueError("La partida no tiene manos registradas")

    mano_finalizada = Mano.objects.filter(partida_id=partida_id, ganador__isnull=False).order_by("-num").first()
    if not mano_finalizada:
        raise ValueError("No hay ninguna mano finalizada todavía")

    resumen_mano = get_resumen_mano_by_mano_id(mano_finalizada.id)
    if not resumen_mano:
        raise ValueError("No existe resumen de la última mano finalizada")

    resumen_ronda_prep = ResumenRondaDTO(
        victoria=None,
        muerte=None,
        retiradas=None,
        efectos_inmediatos=None,
        tickets_usados=resumen_mano.tickets_usados["0"] if "0" in resumen_mano.tickets_usados.keys() else None
    )

    resumen_ronda_1 = ResumenRondaDTO(
        victoria=resumen_mano.victorias["1"] if "1" in resumen_mano.victorias.keys() else None,
        muerte=resumen_mano.muertes["1"] if "1" in resumen_mano.muertes.keys() else None,
        retiradas=resumen_mano.retiradas["1"] if "1" in resumen_mano.retiradas.keys() else None,
        efectos_inmediatos=resumen_mano.efectos_inmediatos_ronda["1"] if "1" in resumen_mano.efectos_inmediatos_ronda.keys() else None,
        tickets_usados=resumen_mano.tickets_usados["1"] if "1" in resumen_mano.tickets_usados.keys() else None
    )

    resumen_ronda_2 = ResumenRondaDTO(
        victoria=resumen_mano.victorias["2"] if "2" in resumen_mano.victorias.keys() else None,
        muerte=resumen_mano.muertes["2"] if "2" in resumen_mano.muertes.keys() else None,
        retiradas=resumen_mano.retiradas["2"] if "2" in resumen_mano.retiradas.keys() else None,
        efectos_inmediatos=resumen_mano.efectos_inmediatos_ronda["2"] if "2" in resumen_mano.efectos_inmediatos_ronda.keys() else None,
        tickets_usados=resumen_mano.tickets_usados["2"] if "2" in resumen_mano.tickets_usados.keys() else None
    )

    resumen_ronda_3 = ResumenRondaDTO(
        victoria=resumen_mano.victorias["3"] if "3" in resumen_mano.victorias.keys() else None,
        muerte=resumen_mano.muertes["3"] if "3" in resumen_mano.muertes.keys() else None,
        retiradas=resumen_mano.retiradas["3"] if "3" in resumen_mano.retiradas.keys() else None,
        efectos_inmediatos=resumen_mano.efectos_inmediatos_ronda["3"] if "3" in resumen_mano.efectos_inmediatos_ronda.keys() else None,
        tickets_usados=resumen_mano.tickets_usados["3"] if "3" in resumen_mano.tickets_usados.keys() else None
    )

    resumen_ronda_com = ResumenRondaDTO(
        victoria=resumen_mano.victorias["4"] if "4" in resumen_mano.victorias.keys() else None,
        muerte=None,
        retiradas=None,
        efectos_inmediatos=None,
        tickets_usados=None
    )

    resumen_mano_dto = ResumenManoDTO(
        mano_num=mano_finalizada.num,
        ronda_prep=resumen_ronda_prep,
        ronda_1=resumen_ronda_1,
        ronda_2=resumen_ronda_2,
        ronda_3=resumen_ronda_3,
        ronda_com=resumen_ronda_com if resumen_ronda_com.victoria is not None else None,
        efectos_extra_fin_mano=resumen_mano.efectos_extra_fin_mano,
        ganador=mano_finalizada.ganador
    )
    return resumen_mano_dto

def create_resumen_mano(partida_id):

    mano_actual = get_mano_actual(partida_id)
    ResumenMano.objects.create(
        mano=mano_actual,
        tickets_usados={"0":[], "1":[], "2":[], "3":[]},
        victorias={},
        muertes={},
        retiradas={"1":[], "2":[], "3":[]},
        efectos_inmediatos_ronda={"1":[], "2":[], "3":[]},
        efectos_extra_fin_mano=[]
    )

def recopilar_ticket_usado(mano_id, ronda_num, color, ticket):

    resumen_mano = get_resumen_mano_by_mano_id(mano_id)
    ronda_num_str = str(ronda_num)
    resumen_mano.tickets_usados[ronda_num_str].append((color, ticket))
    resumen_mano.save(update_fields=["tickets_usados"])

def recopilar_victoria(mano_id, color, tipo_victoria, ronda_num):

    resumen_mano = get_resumen_mano_by_mano_id(mano_id)
    ronda_num_str = str(ronda_num)
    resumen_mano.victorias[ronda_num_str] = (color, tipo_victoria)
    resumen_mano.save(update_fields=["victorias"])

def recopilar_muerte(mano_id, ronda_num, color_matador, color_matado):

    resumen_mano = get_resumen_mano_by_mano_id(mano_id)
    ronda_num_str = str(ronda_num)
    resumen_mano.muertes[ronda_num_str] = (color_matador, color_matado)
    resumen_mano.save(update_fields=["muertes"])

def recopilar_retirada(mano_id, ronda_num, color_retirado):

    resumen_mano = get_resumen_mano_by_mano_id(mano_id)
    ronda_num_str = str(ronda_num)
    resumen_mano.retiradas[ronda_num_str].append(color_retirado)
    resumen_mano.save(update_fields=["retiradas"])

def recopilar_efecto_inmediato_ronda(mano_id, ronda_num, color_beneficiado, efecto):

    resumen_mano = get_resumen_mano_by_mano_id(mano_id)
    ronda_num_str = str(ronda_num)
    resumen_mano.efectos_inmediatos_ronda[ronda_num_str].append((color_beneficiado, efecto))
    resumen_mano.save(update_fields=["efectos_inmediatos_ronda"])

def recopilar_efecto_extra_fin_mano(mano_id, color_beneficiado, efecto):

    resumen_mano = get_resumen_mano_by_mano_id(mano_id)
    resumen_mano.efectos_extra_fin_mano.append((color_beneficiado, efecto))
    resumen_mano.save(update_fields=["efectos_extra_fin_mano"])

def recopilar_puntos_extra(mano_id, carta, puntos):

    resumen_mano = get_resumen_mano_by_mano_id(mano_id)
    if carta == "REBELDE":
        resumen_mano.puntos_rebelde = puntos
    elif carta == "MERCADER":
        resumen_mano.puntos_mercader = puntos
    elif carta == "SEGADOR":
        resumen_mano.puntos_segador = puntos
    resumen_mano.save(update_fields=["puntos_rebelde", "puntos_mercader", "puntos_segador"])
