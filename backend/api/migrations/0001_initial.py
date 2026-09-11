import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone


def seed_config_global(apps, schema_editor):
    ConfiguracionGlobal = apps.get_model("api", "ConfiguracionGlobal")

    # Crear la configuración global con el rango mínimo
    ConfiguracionGlobal.objects.create(rango_minimo_crear_torneo=None)

class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Usuario",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "password",
                    models.CharField(max_length=128, verbose_name="password"),
                ),
                (
                    "last_login",
                    models.DateTimeField(blank=True, null=True, verbose_name="last login"),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={"unique": "A user with that username already exists."},
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(blank=True, max_length=150, verbose_name="first name"),
                ),
                (
                    "last_name",
                    models.CharField(blank=True, max_length=150, verbose_name="last name"),
                ),
                (
                    "email",
                    models.EmailField(blank=True, max_length=254, verbose_name="email address"),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined"),
                ),
                (
                    "nombre",
                    models.CharField(max_length=40),
                ),
                (
                    "puntuacion",
                    models.IntegerField(default=0),
                ),
                (
                    "imagen",
                    models.TextField(blank=True, null=True, max_length=1000, default=None),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
                (
                    "email_verificado",
                    models.BooleanField(default=False),
                ),
            ],
            options={
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Rango",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=25, unique=True, null=False, blank=False)),
                (
                    "color",
                    models.CharField(
                        max_length=20,
                        choices=[
                            ("blanco", "Blanco"),
                            ("negro", "Negro"),
                            ("rosa", "Rosa"),
                            ("rojo_claro", "Rojo claro"),
                            ("rojo", "Rojo"),
                            ("rojo_oscuro", "Rojo oscuro"),
                            ("verde_claro", "Verde claro"),
                            ("verde_esperanza", "Verde esperanza"),
                            ("verde", "Verde"),
                            ("verde_oscuro", "Verde oscuro"),
                            ("azul_claro", "Azul claro"),
                            ("azul", "Azul"),
                            ("azul_oscuro", "Azul oscuro"),
                            ("azul_cian", "Azul cian"),
                            ("amarillo", "Amarillo"),
                            ("amarillo_dorado", "Dorado"),
                            ("amarillo_naranja", "Amarillo anaranjado"),
                            ("naranja", "Naranja"),
                            ("morado_claro", "Púrpura"),
                            ("morado", "Morado"),
                            ("morado_oscuro", "Morado oscuro"),
                            ("gris", "Gris"),
                            ("gris_plata", "Plata"),
                            ("marron_bronce", "Bronce"),
                            ("marron", "Marrón"),
                        ],
                        null=False,
                        blank=False,
                    ),
                ),
                ("puntos_minimos", models.IntegerField(null=False, unique=True)),
                ("puntos_maximos", models.IntegerField(null=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Partida",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=60, unique=True, null=False, blank=False)),
                ("num_jugadores", models.IntegerField(null=False, default=2)),
                ("privada", models.BooleanField(default=False)),
                ("clave", models.CharField(max_length=20, unique=True, null=True, blank=True)),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("fecha_inicio", models.DateTimeField(null=True, blank=True)),
                ("fecha_fin", models.DateTimeField(null=True, blank=True)),
                (
                    "longitud",
                    models.CharField(
                        max_length=20,
                        choices=[
                            ("express", "Express"),
                            ("corta", "Corta"),
                            ("normal", "Normal"),
                            ("larga", "Larga"),
                        ],
                        null=False,
                        blank=False,
                    ),
                ),
                ("cartas_especiales", models.BooleanField(default=True)),
                ("tickets", models.BooleanField(default=True)),
                ("tiempo_max_turno", models.IntegerField(null=False, default=90)),
                (
                    "rango_minimo",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="api.rango",
                    ),
                ),
                (
                    "rango_maximo",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="api.rango",
                    ),
                ),
                ("baraja", models.JSONField(default=list)),
                ("disposicion_jugadores", models.JSONField(default=list)),
                ("turno_actual", models.CharField(max_length=8, null=True)),
                ("puntuacion_asignada_final", models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name="PartidaUsuario",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "partida",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.partida",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.usuario",
                    ),
                ),
                ("creador", models.BooleanField(default=False)),
                ("listo", models.BooleanField(default=False)),
                ("color", models.CharField(
                        max_length=8,
                        choices=[
                            ("rojo", "Rojo"),
                            ("azul", "Azul"),
                            ("verde", "Verde"),
                            ("amarillo", "Amarillo"),
                            ("morado", "Morado"),
                            ("naranja", "Naranja"),
                        ],
                        null=False,
                        blank=False,
                    ),
                ),
                ("puntos", models.IntegerField(null=False, default=0)),
                ("cartas", models.JSONField(default=list)),
                ("carta_comodin", models.CharField(max_length=25, null=True, default=None)),
                ("acumulador_kills", models.IntegerField(null=False, default=0)),
                ("acumulador_deaths", models.IntegerField(null=False, default=0)),
                ("retirado", models.BooleanField(default=False)),
                ("eff_acum_monedero", models.IntegerField(null=False, default=0)),
                ("eff_as_extranjero", models.BooleanField(default=False)),
                ("ticket", models.CharField(max_length=25, null=True, default=None)),
                ("abandono", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Mano",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "partida",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.partida",
                    ),
                ),
                ("num", models.IntegerField(null=False, default=1)),
                ("ganador", models.CharField(max_length=10, null=True, default=None)),
            ],
        ),
        migrations.CreateModel(
            name="Ronda",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "mano",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.mano",
                    ),
                ),
                ("num", models.IntegerField(null=False, default=0)),
                ("cartas", models.JSONField(default=dict, null=True)),
                ("cambios", models.IntegerField(default=0)),
                ("ganador", models.CharField(max_length=10, null=True, default=None)),
            ],
        ),
        migrations.CreateModel(
            name="ResumenMano",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "mano",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.mano",
                    ),
                ),
                ("tickets_usados", models.JSONField(default=dict)),
                ("victorias", models.JSONField(default=dict)),
                ("muertes", models.JSONField(default=dict)),
                ("retiradas", models.JSONField(default=dict)),
                ("efectos_inmediatos_ronda", models.JSONField(default=dict)),
                ("efectos_extra_fin_mano", models.JSONField(default=list)),
                ("puntos_rebelde", models.IntegerField(default=None, null=True)),
                ("puntos_mercader", models.IntegerField(default=None, null=True)),
                ("puntos_segador", models.IntegerField(default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Torneo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=39, unique=True, null=False, blank=False)),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("fecha_inicio", models.DateTimeField(null=True, blank=True)),
                ("fecha_fin", models.DateTimeField(null=True, blank=True)),
                (
                    "rango_minimo",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="api.rango",
                    ),
                ),
                (
                    "rango_maximo",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="api.rango",
                    ),
                ),
                ("num_jug_fin", models.IntegerField(null=False, default=3)),
                ("num_jug_sem", models.IntegerField(null=False, default=3)),
                ("num_jug_cua", models.IntegerField(null=True, default=3)),
                ("num_jug_oct", models.IntegerField(null=True, default=3)),
                (
                    "partidas_longitud",
                    models.CharField(
                        max_length=20,
                        choices=[
                            ("express", "Express"),
                            ("corta", "Corta"),
                            ("normal", "Normal"),
                            ("larga", "Larga"),
                        ],
                        default="normal",
                    ),
                ),
                ("partidas_cartas_especiales", models.BooleanField(default=True)),
                ("partidas_tickets", models.BooleanField(default=True)),
                ("partidas_tiempo_max_turno", models.IntegerField(null=False, default=90)),
                ("desempate_mayor_punt", models.BooleanField(null=False, default=True)),
            ],
        ),
        migrations.CreateModel(
            name="PartidaTorneo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "partida",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.partida",
                    ),
                ),
                (
                    "torneo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.torneo",
                    ),
                ),
                (
                    "fase",
                    models.CharField(
                        max_length=20,
                        choices=[
                            ("octavos", "Octavos"),
                            ("cuartos", "Cuartos"),
                            ("semifinal", "Semifinal"),
                            ("final", "Final"),
                        ],
                        default="cuartos",
                    ),
                ),
                ("lado", models.IntegerField(null=False, default=0)),
                ("pareja", models.IntegerField(null=False, default=0)),
                ("posiciones_finales", models.JSONField(default=dict)),
            ],
        ),
        migrations.CreateModel(
            name="TorneoUsuario",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "torneo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.torneo",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.usuario",
                    ),
                ),
                ("creador", models.BooleanField(null=False, default=False)),
                ("eliminado", models.BooleanField(null=False, default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Medalla",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=40, unique=True, null=False, blank=False)),
                ("imagen", models.TextField(blank=True, null=True, default=None, max_length=1000)),
                (
                    "categoria",
                    models.CharField(
                        max_length=20,
                        choices=[
                            ("oro", "Oro"),
                            ("plata", "Plata"),
                            ("bronce", "Bronce"),
                        ],
                        default="bronce",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ConfiguracionGlobal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "rango_minimo_crear_torneo",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="api.rango",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MedallaTorneo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "medalla",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.medalla",
                    ),
                ),
                (
                    "torneo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.torneo",
                    ),
                ),
                (
                    "puesto",
                    models.IntegerField(null=False, blank=False),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Logro",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombre", models.CharField(max_length=40, unique=True, null=False, blank=False)),
                ("imagen", models.TextField(blank=True, null=True, default=None, max_length=1000)),
                ("descripcion", models.TextField(null=False, max_length=1000)),
                ("oculto", models.BooleanField(null=False, default=False)),
            ],
        ),
        migrations.CreateModel(
            name="RecompensaUsuario",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.usuario",
                    ),
                ),
                (
                    "medalla",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.medalla",
                    ),
                ),
                (
                    "logro",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.logro",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RequisitoLogro",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "logro",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.logro",
                    ),
                ),
                ("requisito", models.CharField(max_length=50, choices=[
                    ("puntos_ganados_partida", "Puntos ganados en partida"),
                    ("puntuacion_acumulada", "Puntuación acumulada"),
                    ("puntos_ganados_mercader", "Puntos ganados con el Mercader"),
                    ("puntos_ganados_rebelde", "Puntos ganados con el Rebelde"),
                    ("puntos_ganados_segador", "Puntos ganados con el Segador"),
                    ("cartas_victimas_segador", "Cartas víctimas de segador"),
                    ("puntos_ganados_joyas_reales", "Puntos ganados con joyas reales"),
                    ("puntos_ganados_vinos_viejos", "Puntos ganados con vinos viejos"),
                    ("muertes_corrompidas_corruptor", "Muertes corrompidas con el Corruptor"),
                    ("tumbas_saqueadas_saqueador", "Tumbas saqueadas con el Saqueador"),
                    ("partidas_ganadas", "Partidas ganadas"),
                    ("cartas_kills", "Cartas rivales matadas"),
                    ("cartas_deaths", "Cartas propias matadas"),
                    ("rondas_ganadas", "Rondas ganadas"),
                    ("rondas_comodin_ganadas", "Rondas comodín ganadas"),
                    ("manos_ganadas", "Manos ganadas"),
                    ("retiradas", "Retiradas"),
                    ("manos_ganadas_unica", "Manos ganadas con carta única"),
                    ("contraataques_bastos_punt", "Contraataques con bastos puntiagudos"),
                    ("tickets_usados", "Tickets usados")
                ])),
                ("una_partida", models.BooleanField(default=False)),
                ("valor_necesario", models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name="RequisitoLogroUsuario",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.usuario",
                    ),
                ),
                (
                    "requisito_logro",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="api.requisitologro",
                    ),
                ),
                ("progreso", models.IntegerField(default=0)),
            ],
        ),
        migrations.RunPython(seed_config_global, reverse_code=migrations.RunPython.noop),
    ]
