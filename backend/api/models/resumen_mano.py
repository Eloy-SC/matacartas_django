from django.db import models

class ResumenMano(models.Model):

    mano = models.ForeignKey("Mano", on_delete=models.CASCADE)
    tickets_usados = models.JSONField(default=dict) # Tickets usados durante la mano: clave num de la ronda y valor una lista de tickets usados
    victorias = models.JSONField(default=dict) # Claves rondas y valores tuplas (jugador, tipo_victoria)
    muertes = models.JSONField(default=dict) # Claves rondas y valores (jugador_matador, jugador_matado)
    retiradas = models.JSONField(default=dict)
    efectos_inmediatos_ronda = models.JSONField(default=dict) # Claves rondas y valores [(beneficiado1, efecto1), (beneficiado2, efecto2)...]
    efectos_extra_fin_mano = models.JSONField(default=list) # [(beneficiado1, efecto1), (beneficiado2, efecto2)...]
    puntos_rebelde = models.IntegerField(default=None, null=True)
    puntos_mercader = models.IntegerField(default=None, null=True)
    puntos_segador = models.IntegerField(default=None, null=True)

