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

class RequisitoLogro(models.Model):
    class Requisito(models.TextChoices):
        PUNTOS_GANADOS_PARTIDA = "puntos_ganados_partida", "Puntos ganados en partida"
        PUNTUACION_ACUMULADA = "puntuacion_acumulada", "Puntuación acumulada"
        PUNTOS_GANADOS_MERCADER = "puntos_ganados_mercader", "Puntos ganados con mercader"
        PUNTOS_GANADOS_REBELDE = "puntos_ganados_rebelde", "Puntos ganados con rebelde"
        PUNTOS_GANADOS_SEGADOR = "puntos_ganados_segador", "Puntos ganados con segador"
        CARTAS_VICTIMAS_SEGADOR = "cartas_victimas_segador", "Cartas víctimas de segador"
        PUNTOS_GANADOS_JOYAS_REALES = "puntos_ganados_joyas_reales", "Puntos ganados con joyas reales"
        PUNTOS_GANADOS_VINOS_VIEJOS = "puntos_ganados_vinos_viejos", "Puntos ganados con vinos viejos"
        MUERTES_CORROMPIDAS_CORRUPTOR = "muertes_corrompidas_corruptor", "Muertes corrompidas con el Corruptor"
        MUERTES_BENEFICIO_ROBADO_SAQUEADOR = "muertes_beneficio_robado_saqueador", "Muertes de beneficio robado con el Saqueador"
        PARTIDAS_GANADAS = "partidas_ganadas", "Partidas ganadas"
        CARTAS_KILLS = "cartas_kills", "Cartas rivales matadas"
        CARTAS_DEATHS = "cartas_deaths", "Cartas propias matadas"
        CARTAS_JUGADAS = "cartas_jugadas", "Cartas jugadas"
        RONDAS_GANADAS = "rondas_ganadas", "Rondas ganadas"
        RONDAS_COMODIN_GANADAS = "rondas_comodin_ganadas", "Rondas comodín ganadas"
        MANOS_GANADAS = "manos_ganadas", "Manos ganadas"
        RETIRADAS = "retiradas", "Retiradas"
        MANOS_GANADAS_DON_DINERO = "manos_ganadas_don_dinero", "Manos ganadas con Don Dinero"
        MANOS_GANADAS_MARTIRIZADO = "manos_ganadas_martirizado", "Manos ganadas con el Martirizado"
        CONTRAATAQUES_BASTOS_PUNT = "contraataques_bastos_punt", "Contraataques con bastos puntiagudos"
        TICKETS_USADOS = "tickets_usados", "Tickets usados"

    logro = models.ForeignKey(
        Logro,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )
    requisito = models.CharField(max_length=50, choices=Requisito.choices)
    valor_necesario = models.IntegerField(default=1) # Valor necesario para cumplir el requisito y obtener el logro
    progreso = models.IntegerField(default=0) # Atributo para almacenar el progreso y no tener que recalcularlo

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