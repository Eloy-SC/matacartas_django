from django.urls import path

from .views.estadisticas_view import (
    get_estadisticas_globales,
    get_estadisticas_individuales,
    get_historial_partidas
)

from .views.config_global_view import (
    obtener_rango_minimo_crear_torneo,
    cambiar_rango_minimo_crear_torneo,
)

from .views.email_view import (
    confirmar_recuperacion_password, 
    solicitar_recuperacion_password,
    verificar_email,
)

from .views.resumen_mano_view import get_resumen_ult_mano

from .views.ronda_view import (
    jugar_carta,
    retirarse_de_mano
)

from .views.ticket_view import (
    usar_ticket
)

from .views.mano_view import (
    cambiar_cartas,
    elegir_carta_comodin,
    get_datos_carta,
    get_mesa,
    jugador_no_quiere_cambiar,
    jugador_quiere_cambiar,
    repartir_cartas,
    siguiente_mano,
)

from .views.partida_view import (
    abandonar_partida,
    abandonar_partida_sala_espera,
    crear_partida,
    editar_partida,
    expulsar_jugador,
    finalizar_partida,
    get_jugador_participa_en_partida,
    get_jugador_participa_en_partida_privada,
    get_partida_ha_empezado,
    get_jugadores_partida,
    get_partida_como_jugador,
    iniciar_partida,
    iniciar_partida_manual,
    listar_partidas_publicas,
    toggle_listo,
    unirse_a_partida_privada,
    unirse_a_partida_publica
)

from .views.auth_view import csrf, me, register, session_login, session_logout
from .views.user_view import (
    crear_usuario_admin,
    editar_usuario_admin,
    eliminar_usuario_admin,
    get_usuario_admin,
    listar_top_usuarios,
    listar_usuarios_admin,
    perfil_actualizar,
)
from .views.rango_view import (
    crear_rango_admin,
    editar_rango_admin,
    eliminar_rango_admin,
    get_rango,
    get_rango_de_usuario,
    listar_rangos,
)
from .views.medalla_view import (
    crear_medalla_admin,
    editar_medalla_admin,
    eliminar_medalla_admin,
    get_medalla,
    listar_medallas,
)
from .views.logro_view import crear_logro
from .views.torneo_view import (
    crear_torneo,
    get_partida_actual_de_torneo,
    get_partidas_de_torneo, 
    get_torneo, 
    listar_torneos_publicos, 
    get_participantes_torneo,
    unirse_a_torneo,
    abandonar_torneo,
    get_partida_pertenece_a_torneo,
    )
from .views.health_view import health_check

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("auth/csrf/", csrf, name="csrf"),
    path("auth/login/", session_login, name="session-login"),
    path("auth/register/", register, name="register"),
    path("auth/logout/", session_logout, name="session-logout"),
    path("auth/me/", me, name="me"),
    path("users/perfil/actualizar/", perfil_actualizar, name="perfil-actualizar"),

    # RELACIONADO CON EMAIL
    path(
        "auth/password-reset/",
        solicitar_recuperacion_password,
        name="solicitar_recuperacion_password",
    ),
    path(
        "auth/verificar-email/",
        verificar_email,
        name="verificar-email",
    ),
    path(
        "auth/password-reset-confirm/",
        confirmar_recuperacion_password,
        name="confirmar_recuperacion_password",
    ),

    # USUARIOS
    path("users/admin/listar/", listar_usuarios_admin, name="listar-usuarios-admin"),
    path("users/admin/crear/", crear_usuario_admin, name="crear-usuario-admin"),
    path("users/admin/<int:user_id>/", get_usuario_admin, name="get-usuario-admin"),
    path(
        "users/admin/<int:user_id>/editar/",
        editar_usuario_admin,
        name="editar-usuario-admin",
    ),
    path(
        "users/admin/<int:user_id>/eliminar/",
        eliminar_usuario_admin,
        name="eliminar-usuario-admin",
    ),
    path("users/top/", listar_top_usuarios, name="listar-top-usuarios"),

    # RANGOS
    path("rangos/listar/", listar_rangos, name="listar-rangos"),
    path("rangos/admin/crear/", crear_rango_admin, name="crear-rango-admin"),
    path("rangos/<int:rango_id>/", get_rango, name="get-rango"),
    path("rangos/usuario/<int:user_id>/", get_rango_de_usuario, name="get-rango-de-usuario"),
    path(
        "rangos/admin/<int:rango_id>/editar/",
        editar_rango_admin,
        name="editar-rango-admin",
    ),
    path(
        "rangos/admin/<int:rango_id>/eliminar/",
        eliminar_rango_admin,
        name="eliminar-rango-admin",
    ),

    # MEDALLAS
    path("medallas/listar/", listar_medallas, name="listar-medallas"),
    path("medallas/admin/crear/", crear_medalla_admin, name="crear-medalla-admin"),
    path("medallas/<int:medalla_id>/", get_medalla, name="get-medalla"),
    path(
        "medallas/admin/<int:medalla_id>/editar/",
        editar_medalla_admin,
        name="editar-medalla-admin",
    ),
    path(
        "medallas/admin/<int:medalla_id>/eliminar/",
        eliminar_medalla_admin,
        name="eliminar-medalla-admin",
    ),

    # LOGROS
    path("logros/admin/crear/", crear_logro, name="crear-logro-admin"),

    # CONFIGURACION GLOBAL
    path("config-global/rango-minimo/torneos/", obtener_rango_minimo_crear_torneo, name="obtener-rango-minimo-torneos"),
    path("config-global/rango-minimo/torneos/admin/", cambiar_rango_minimo_crear_torneo, name="cambiar-rango-minimo-torneos"),

    # PARTIDAS
    path("partidas/publicas/", listar_partidas_publicas, name="listar-partidas-publicas"),
    path("partidas/crear/", crear_partida, name="crear-partida"),
    path("partidas/<int:partida_id>/editar/", editar_partida, name="editar-partida"),
    path("partidas/<int:partida_id>/jugador/", get_partida_como_jugador, name="get-partida-como-jugador"),
    path("partidas/<int:partida_id>/jugadores/", get_jugadores_partida, name="get-jugadores-partida"),
    path("partidas/<int:partida_id>/participa/", get_jugador_participa_en_partida, name="get-jugador-participa-en-partida"),
    path("partidas/<str:clave>/participa/", get_jugador_participa_en_partida_privada, name="get-jugador-participa-en-partida-privada"),
    path("partidas/<int:partida_id>/pertenece-torneo/", get_partida_pertenece_a_torneo, name="get-partida-pertenece-a-torneo"),
    path("partidas/<int:partida_id>/ha-empezado/", get_partida_ha_empezado, name="get-partida-ha-empezado"),
    path("partidas/<int:partida_id>/sala-espera/abandonar/", abandonar_partida_sala_espera, name="abandonar-partida-sala-espera"),
    path("partidas/<int:partida_id>/unirse/", unirse_a_partida_publica, name="unirse-a-partida-publica"),
    path("partidas/<str:clave>/unirse/", unirse_a_partida_privada, name="unirse-a-partida-privada"),
    path("partidas/<int:partida_id>/toggle-listo/", toggle_listo, name="toggle-listo"),
    path("partidas/<int:partida_id>/expulsar-jugador/<int:jugador_id>/", expulsar_jugador, name="expulsar-jugador"),
    path("partidas/<int:partida_id>/iniciar/", iniciar_partida, name="iniciar-partida"),
    path("partidas/<int:partida_id>/iniciar/manual/", iniciar_partida_manual, name="iniciar-partida-manual"),

    # TORNEOS
    path("torneos/publicos/", listar_torneos_publicos, name="listar-torneos-publicos"),
    path("torneos/crear/", crear_torneo, name="crear-torneo"),
    path("torneos/<int:torneo_id>/", get_torneo, name="get-torneo"),
    path("torneos/<int:torneo_id>/participantes/", get_participantes_torneo, name="get-participantes-torneo"),
    path("torneos/<int:torneo_id>/unirse/", unirse_a_torneo, name="unirse-a-torneo"),
    path("torneos/<int:torneo_id>/abandonar/", abandonar_torneo, name="abandonar-torneo"),
    path("torneos/<int:torneo_id>/partida_actual/", get_partida_actual_de_torneo, name="get-partida-actual-de-torneo"),
    path("torneos/<int:torneo_id>/partidas/", get_partidas_de_torneo, name="get-partidas-de-torneo"),

    # ESTADISTICAS
    path("estadisticas/globales/", get_estadisticas_globales, name="get-estadisticas-globales"),
    path("estadisticas/individuales/", get_estadisticas_individuales, name="get-estadisticas-individuales"),
    path("estadisticas/individuales/historial/", get_historial_partidas, name="get-historial-partidas"),

    # JUEGO
    path("partida/<int:partida_id>/mano/repartir/", repartir_cartas, name="repartir-cartas"),
    path("partida/<int:partida_id>/mano/mesa/", get_mesa, name="get-mesa"),
    path("partida/<int:partida_id>/mano/datos-carta/", get_datos_carta, name="get-datos-carta"),
    path("partida/<int:partida_id>/mano/quiero-cambio/", jugador_quiere_cambiar, name="jugador-quiere-cambiar"),
    path("partida/<int:partida_id>/mano/no-quiero-cambio/", jugador_no_quiere_cambiar, name="jugador-no-quiere-cambiar"),
    path("partida/<int:partida_id>/mano/cambiar-cartas/", cambiar_cartas, name="cambiar-cartas"),
    path("partida/<int:partida_id>/mano/elegir-carta-comodin/", elegir_carta_comodin, name="elegir-carta-comodin"),
    path("partida/<int:partida_id>/mano/siguiente-mano/", siguiente_mano, name="siguiente-mano"),
    path("partida/<int:partida_id>/mano/resumen/", get_resumen_ult_mano, name="get-resumen-ult-mano"),

    path("partida/<int:partida_id>/mano/ronda/jugar-carta/", jugar_carta, name="jugar-carta"),
    path("partida/<int:partida_id>/mano/ronda/retirarse/", retirarse_de_mano, name="retirarse-de-mano"),
    path("partida/<int:partida_id>/mano/ronda/usar-ticket/", usar_ticket, name="usar-ticket"),

    path("partida/<int:partida_id>/finalizar/", finalizar_partida, name="finalizar-partida"),
    path("partida/<int:partida_id>/abandonar/", abandonar_partida, name="abandonar-partida")
]
