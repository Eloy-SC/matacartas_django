from django.db import models

from ..models.usuario import Usuario


class Recompensa(models.Model):

    nombre = models.CharField(max_length=40, unique=True, null=False, blank=False)
    imagen = models.TextField(blank=True, null=True, default=None, max_length=1000)

    class Meta:
        abstract = True

class Medalla(Recompensa):
    class CategoriaMedalla(models.TextChoices):
        ORO = "oro", "Oro"
        PLATA = "plata", "Plata"
        BRONCE = "bronce", "Bronce"

    categoria = models.CharField(max_length=20, choices=CategoriaMedalla.choices, default=CategoriaMedalla.BRONCE)

class Logro(Recompensa):
    descripcion = models.TextField(null=False, max_length=1000)
    oculto = models.BooleanField(null=False, default=False)  # Indica si el logro es visible para los usuarios o no

class RequisitoLogro(models.Model):
    class Requisito(models.TextChoices):
        PUNTOS_GANADOS_PARTIDA = "puntos_ganados_partida", "Puntos ganados en partida"
        PUNTUACION_ACUMULADA = "puntuacion_acumulada", "Puntuación acumulada"
        PUNTOS_GANADOS_MERCADER = "puntos_ganados_mercader", "Puntos ganados con el Mercader"
        PUNTOS_GANADOS_REBELDE = "puntos_ganados_rebelde", "Puntos ganados con el Rebelde"
        PUNTOS_GANADOS_SEGADOR = "puntos_ganados_segador", "Puntos ganados con el Segador"
        CARTAS_VICTIMAS_SEGADOR = "cartas_victimas_segador", "Cartas víctimas de segador"
        PUNTOS_GANADOS_JOYAS_REALES = "puntos_ganados_joyas_reales", "Puntos ganados con joyas reales"
        PUNTOS_GANADOS_VINOS_VIEJOS = "puntos_ganados_vinos_viejos", "Puntos ganados con vinos viejos"
        MUERTES_CORROMPIDAS_CORRUPTOR = "muertes_corrompidas_corruptor", "Muertes corrompidas con el Corruptor"
        TUMBAS_SAQUEADAS_SAQUEADOR = "tumbas_saqueadas_saqueador", "Tumbas saqueadas con el Saqueador"
        PARTIDAS_GANADAS = "partidas_ganadas", "Partidas ganadas"
        CARTAS_KILLS = "cartas_kills", "Cartas rivales matadas"
        CARTAS_DEATHS = "cartas_deaths", "Cartas propias matadas"
        RONDAS_GANADAS = "rondas_ganadas", "Rondas ganadas"
        RONDAS_COMODIN_GANADAS = "rondas_comodin_ganadas", "Rondas comodín ganadas"
        MANOS_GANADAS = "manos_ganadas", "Manos ganadas"
        RETIRADAS = "retiradas", "Retiradas"
        MANOS_GANADAS_UNICA = "manos_ganadas_unica", "Manos ganadas con carta única"
        CONTRAATAQUES_BASTOS_PUNT = "contraataques_bastos_punt", "Contraataques con bastos puntiagudos"
        TICKETS_USADOS = "tickets_usados", "Tickets usados"

    logro = models.ForeignKey(
        Logro,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    requisito = models.CharField(max_length=50, choices=Requisito.choices)
    una_partida = models.BooleanField(default=False) # Indica si el requisito se debe cumplir en una sola partida o de forma acumulativa. No es compatible con algunos tipos de requisito
    valor_necesario = models.IntegerField(default=1) # Valor necesario para cumplir el requisito y obtener el logro

class RecompensaUsuario(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )
    medalla = models.ForeignKey(
        Medalla,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    logro = models.ForeignKey(
        Logro,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )