from django.db.models import Exists, OuterRef, Q

from ..models.recompensa import Logro, RecompensaUsuario


def _build_logros_queryset(search=None, nombre=None, oculto=None):
	queryset = Logro.objects.all().prefetch_related("requisitologro_set")

	if search:
		search = search.strip()
		if search:
			queryset = queryset.filter(
				Q(nombre__icontains=search) | Q(descripcion__icontains=search)
			)

	if nombre:
		queryset = queryset.filter(nombre__icontains=nombre.strip())

	if oculto is not None:
		queryset = queryset.filter(oculto=oculto)

	return queryset


def list_logros_paginated(offset, limit, *, search=None, nombre=None, oculto=None, ordering=None):
	queryset = _build_logros_queryset(search=search, nombre=nombre, oculto=oculto)
	order_fields = [ordering or "nombre"]
	if (ordering or "nombre").lstrip("-") != "id":
		order_fields.append("id")

	return queryset.order_by(*order_fields)[offset:offset + limit]


def get_logros_count(*, search=None, nombre=None, oculto=None):
	return _build_logros_queryset(search=search, nombre=nombre, oculto=oculto).count()

def get_logros():
	return Logro.objects.all()


def _build_logros_usuario_queryset(usuario_id):
	recompensa_usuario = RecompensaUsuario.objects.filter(
		usuario_id=usuario_id,
		logro_id=OuterRef("pk"),
	)
	return Logro.objects.prefetch_related("requisitologro_set").annotate(
		desbloqueado=Exists(recompensa_usuario),
	).filter(
		Q(oculto=False) | Q(desbloqueado=True),
	)


def list_logros_usuario_paginated(usuario_id, offset, limit, *, ordering=None):
	ordering = ordering or "nombre"
	queryset = _build_logros_usuario_queryset(usuario_id)
	order_fields = [ordering]
	if ordering.lstrip("-") != "id":
		order_fields.append("id")
	return queryset.order_by(*order_fields)[offset:offset + limit]


def get_logros_usuario_count(usuario_id):
	return _build_logros_usuario_queryset(usuario_id).count()


def get_logros_ocultos_pendientes_count(usuario_id):
	return Logro.objects.filter(oculto=True).exclude(
		recompensausuario__usuario_id=usuario_id,
	).count()