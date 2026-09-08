
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..services import estadisticas_service


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_estadisticas_globales(request):
    """
    Endpoint para obtener las estadísticas globales de todas las partidas finalizadas.
    """
    try:
        estadisticas = estadisticas_service.get_estadisticas_globales(request.user)
    except Exception as e:
        return Response({"detail": str(e)}, status=500)
    
    return Response(estadisticas, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_estadisticas_individuales(request):
    """
    Endpoint para obtener las estadísticas individuales de un usuario.
    """
    try:
        estadisticas = estadisticas_service.get_estadisticas_individuales(request.user)
    except Exception as e:
        return Response({"detail": str(e)}, status=500)
    
    return Response(estadisticas, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_historial_partidas(request):
    """
    Endpoint para obtener el historial de partidas de un usuario.
    """
    try:
        historial = estadisticas_service.get_historial_partidas(request.user)
    except Exception as e:
        return Response({"detail": str(e)}, status=500)
    
    return Response(historial, status=200)