from django.db import migrations
from django.utils import timezone


TEST_TORNEOS = [
    {
        "nombre": "Torneo Largo de Prueba",
        "num_jug_fin": 4,
        "num_jug_sem": 4,
        "num_jug_cua": 4,
        "num_jug_oct": 4,
        "partidas_longitud": "larga",
        "partidas_cartas_especiales": True,
        "partidas_tickets": True,
        "partidas_tiempo_max_turno": 120,
        "desempate_mayor_punt": True,
        "rango_minimo": "VETERANO",
        "rango_maximo": "MAESTRO SUPREMO CELESTIAL",
    },
    {
        "nombre": "Torneo Corto Prueba",
        "num_jug_fin": 2,
        "num_jug_sem": 2,
        "num_jug_cua": None,
        "num_jug_oct": None,
        "partidas_longitud": "corta",
        "partidas_cartas_especiales": False,
        "partidas_tickets": False,
        "partidas_tiempo_max_turno": 60,
        "desempate_mayor_punt": False,
        "rango_minimo": None,
        "rango_maximo": None,
    },
    {
        "nombre": "Torneo Nombre Muy Largo Para Probar Lim",
        "num_jug_fin": 3,
        "num_jug_sem": 3,
        "num_jug_cua": 3,
        "num_jug_oct": None,
        "partidas_longitud": "corta",
        "partidas_cartas_especiales": False,
        "partidas_tickets": False,
        "partidas_tiempo_max_turno": 60,
        "desempate_mayor_punt": False,
        "rango_minimo": None,
        "rango_maximo": None,
    },
    {
        "nombre": "T",
        "num_jug_fin": 3,
        "num_jug_sem": 3,
        "num_jug_cua": None,
        "num_jug_oct": None,
        "partidas_longitud": "corta",
        "partidas_cartas_especiales": False,
        "partidas_tickets": False,
        "partidas_tiempo_max_turno": 60,
        "desempate_mayor_punt": False,
        "rango_minimo": None,
        "rango_maximo": None,
    },
]

TEST_MEDALLAS = [
    {
        "nombre": "Campeon del Torneo Agosto 2026",
        "categoria": "oro",
        "imagen": None,
    },
    {
        "nombre": "Subcampeon del Torneo Agosto 2026",
        "categoria": "plata",
        "imagen": None,
    },
    {
        "nombre": "Tercer Puesto del Torneo Agosto 2026",
        "categoria": "bronce",
        "imagen": None,
    },
    {
        "nombre": "Tercer Puesto Generico Nombre Muuy Largo",
        "categoria": "bronce",
        "imagen": None,
    },
]

TEST_MEDALLAS_TORNEO = [
    {
        "torneo": "Torneo Largo de Prueba",
        "medalla": "Campeon del Torneo Agosto 2026",
        "puesto": 1,
    },
    {
        "torneo": "Torneo Largo de Prueba",
        "medalla": "Subcampeon del Torneo Agosto 2026",
        "puesto": 2,
    },
    {
        "torneo": "Torneo Largo de Prueba",
        "medalla": "Tercer Puesto del Torneo Agosto 2026",
        "puesto": 3,
    },
    {
        "torneo": "Torneo Corto Prueba",
        "medalla": "Campeon del Torneo Agosto 2026",
        "puesto": 1,
    },
    {
        "torneo": "Torneo Corto Prueba",
        "medalla": "Subcampeon del Torneo Agosto 2026",
        "puesto": 2,
    },
    {
        "torneo": "Torneo Nombre Muy Largo Para Probar Lim",
        "medalla": "Campeon del Torneo Agosto 2026",
        "puesto": 1,
    },
    {
        "torneo": "Torneo Nombre Muy Largo Para Probar Lim",
        "medalla": "Subcampeon del Torneo Agosto 2026",
        "puesto": 2,
    },
    {
        "torneo": "T",
        "medalla": "Campeon del Torneo Agosto 2026",
        "puesto": 1,
    },
    {
        "torneo": "T",
        "medalla": "Subcampeon del Torneo Agosto 2026",
        "puesto": 2,
    },
]

def _resolve_rango(rango_model, nombre):
    if not nombre:
        return None
    return rango_model.objects.get(nombre=nombre)

def _resolve_medalla(medalla_model, nombre):
    if not nombre:
        return None
    return medalla_model.objects.get(nombre=nombre)

def seed_test_torneos(apps, schema_editor):
    Torneo = apps.get_model("api", "Torneo")
    Rango = apps.get_model("api", "Rango")
    MedallaTorneo = apps.get_model("api", "MedallaTorneo")

    for torneo_spec in TEST_TORNEOS:
        defaults = {
            "fecha_inicio": torneo_spec["fecha_inicio"] if "fecha_inicio" in torneo_spec else None,
            "num_jug_fin": torneo_spec["num_jug_fin"],
            "num_jug_sem": torneo_spec["num_jug_sem"],
            "num_jug_cua": torneo_spec["num_jug_cua"],
            "num_jug_oct": torneo_spec["num_jug_oct"],
            "partidas_longitud": torneo_spec["partidas_longitud"],
            "partidas_cartas_especiales": torneo_spec["partidas_cartas_especiales"],
            "partidas_tickets": torneo_spec["partidas_tickets"],
            "partidas_tiempo_max_turno": torneo_spec["partidas_tiempo_max_turno"],
            "desempate_mayor_punt": torneo_spec["desempate_mayor_punt"],
            "rango_minimo": _resolve_rango(Rango, torneo_spec["rango_minimo"]),
            "rango_maximo": _resolve_rango(Rango, torneo_spec["rango_maximo"]),
        }
        Torneo.objects.update_or_create(nombre=torneo_spec["nombre"], defaults=defaults)
    for medalla_torneo_spec in TEST_MEDALLAS_TORNEO:
        torneo = Torneo.objects.get(nombre=medalla_torneo_spec["torneo"])
        medalla = _resolve_medalla(apps.get_model("api", "Medalla"), medalla_torneo_spec["medalla"])
        MedallaTorneo.objects.update_or_create(
            torneo=torneo,
            medalla=medalla,
            defaults={"puesto": medalla_torneo_spec["puesto"]},
        )
        

"""
def seed_test_partidas_torneo(apps, schema_editor):
    Partida = apps.get_model("api", "Partida")
    PartidaTorneo = apps.get_model("api", "PartidaTorneo")
    Torneo = apps.get_model("api", "Torneo")

    for partida_torneo_spec in TEST_PARTIDAS_TORNEO:
        partida = Partida.objects.get(nombre=partida_torneo_spec["partida"])
        torneo = Torneo.objects.get(nombre=partida_torneo_spec["torneo"])
        lookup = {
            "partida": partida,
            "torneo": torneo,
            "fase": partida_torneo_spec["fase"],
            "lado": partida_torneo_spec["lado"],
            "pareja": partida_torneo_spec["pareja"],
        }
        PartidaTorneo.objects.update_or_create(
            **lookup,
            defaults={"posiciones_finales": partida_torneo_spec["posiciones_finales"]},
        )
"""

def seed_test_medallas(apps, schema_editor):
    Medalla = apps.get_model("api", "Medalla")

    for medalla_spec in TEST_MEDALLAS:
        Medalla.objects.update_or_create(
            nombre=medalla_spec["nombre"],
            defaults={
                "categoria": medalla_spec["categoria"],
                "imagen": medalla_spec["imagen"],
            },
        )


def unseed_test_medallas(apps, schema_editor):
    Medalla = apps.get_model("api", "Medalla")
    nombres = [medalla["nombre"] for medalla in TEST_MEDALLAS]
    Medalla.objects.filter(nombre__in=nombres).delete()

"""
def unseed_test_partidas_torneo(apps, schema_editor):
    PartidaTorneo = apps.get_model("api", "PartidaTorneo")
    Torneo = apps.get_model("api", "Torneo")
    nombres_torneos = [torneo["nombre"] for torneo in TEST_TORNEOS]
    PartidaTorneo.objects.filter(torneo__nombre__in=nombres_torneos).delete()
"""

def unseed_test_torneos(apps, schema_editor):
    Torneo = apps.get_model("api", "Torneo")
    nombres = [torneo["nombre"] for torneo in TEST_TORNEOS]
    Torneo.objects.filter(nombre__in=nombres).delete()
    MedallaTorneo = apps.get_model("api", "MedallaTorneo")
    MedallaTorneo.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0003_seed_test_partidas"),
    ]

    operations = [
        migrations.RunPython(seed_test_medallas, reverse_code=unseed_test_medallas),
        migrations.RunPython(seed_test_torneos, reverse_code=unseed_test_torneos),
        #migrations.RunPython(seed_test_partidas_torneo, reverse_code=unseed_test_partidas_torneo),
    ]