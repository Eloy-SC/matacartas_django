

import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../../styles/admin.css";
import { obtenerCsrfToken } from "../../utils/ObtenerCsfrToken";

const ORDER_FIELDS = [
	{ value: "nombre", label: "Nombre" },
	{ value: "oculto", label: "Visibilidad" },
	{ value: "id", label: "Identificador" },
];

export default function AdminLogros() {
	const navigate = useNavigate();
	const [logros, setLogros] = useState([]);
	const [page, setPage] = useState(1);
	const [totalPages, setTotalPages] = useState(1);
	const [totalLogros, setTotalLogros] = useState(0);
	const [search, setSearch] = useState("");
	const [debouncedSearch, setDebouncedSearch] = useState("");
	const [selectedOculto, setSelectedOculto] = useState("");
	const [orderBy, setOrderBy] = useState("nombre");
	const [orderDir, setOrderDir] = useState("asc");
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [deletingId, setDeletingId] = useState(null);

	const loadLogros = useCallback((pageNumber = 1) => {
		let cancelled = false;
		setLoading(true);
		setError("");
		const params = new URLSearchParams({ page: String(pageNumber) });
		if (debouncedSearch.trim()) params.set("search", debouncedSearch.trim());
		if (selectedOculto) params.set("oculto", selectedOculto);
		params.set("ordering", orderDir === "desc" ? `-${orderBy}` : orderBy);

		fetch(`/api/logros/listar/?${params.toString()}`, { credentials: "include" })
			.then(async (res) => {
				const data = await res.json().catch(() => ({}));
				if (cancelled) return;
				if (!res.ok) throw new Error(data?.detail || "No se pudo cargar la lista de logros");
				setLogros(Array.isArray(data?.items) ? data.items : []);
				setPage(typeof data?.page === "number" ? data.page : pageNumber);
				setTotalPages(typeof data?.total_pages === "number" ? data.total_pages : 1);
				setTotalLogros(typeof data?.total === "number" ? data.total : 0);
			})
			.catch((e) => {
				if (cancelled) return;
				setError(e instanceof Error ? e.message : "Error cargando logros");
				setLogros([]);
				setTotalPages(1);
				setTotalLogros(0);
			})
			.finally(() => { if (!cancelled) setLoading(false); });

		return () => { cancelled = true; };
	}, [debouncedSearch, selectedOculto, orderBy, orderDir]);

	useEffect(() => {
		const timeoutId = setTimeout(() => setDebouncedSearch(search), 300);
		return () => clearTimeout(timeoutId);
	}, [search]);

	useEffect(() => { setPage(1); }, [debouncedSearch, selectedOculto, orderBy, orderDir]);
	useEffect(() => loadLogros(page), [loadLogros, page]);

	async function handleDelete(logroId) {
		if (!logroId || deletingId) return;
		if (!window.confirm("¿Seguro que quieres eliminar este logro?")) return;
		setDeletingId(logroId);
		setError("");
		try {
			const csrfToken = await obtenerCsrfToken();
			const res = await fetch(`/api/logros/admin/${logroId}/eliminar/`, {
				method: "DELETE",
				credentials: "include",
				headers: { "X-CSRFToken": csrfToken },
			});
			const data = await res.json().catch(() => ({}));
			if (!res.ok) throw new Error(data?.detail || "No se pudo eliminar el logro");
			loadLogros(page);
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error eliminando logro");
		} finally {
			setDeletingId(null);
		}
	}

	return (
		<div className="app">
			<button className="admin-volver-button" onClick={() => navigate("/admin/recompensas")}>⮜</button>
			<div className="admin-title-card"><h1 style={{ marginBottom: 0 }}>ADMINISTRACION - LOGROS</h1></div>
			<div className="admin-toolbar-card">
				<input type="search" className="admin-search-input" placeholder="Buscar logro..." aria-label="Buscar logro" value={search} onChange={(e) => setSearch(e.target.value)} disabled={loading} />
				<select className="admin-search-input" value={selectedOculto} onChange={(e) => setSelectedOculto(e.target.value)} aria-label="Filtrar por visibilidad" disabled={loading}>
					<option value="">Todos los logros</option><option value="false">Visibles</option><option value="true">Ocultos</option>
				</select>
				<select className="admin-search-input" value={orderBy} onChange={(e) => setOrderBy(e.target.value)} aria-label="Ordenar logros por" disabled={loading}>
					{ORDER_FIELDS.map((field) => <option key={field.value} value={field.value}>Ordenar: {field.label}</option>)}
				</select>
				<select className="admin-search-input" value={orderDir} onChange={(e) => setOrderDir(e.target.value)} aria-label="Dirección de ordenación" disabled={loading}>
					<option value="asc">Ascendente</option><option value="desc">Descendente</option>
				</select>
				<button type="button" className="admin-primary-button" onClick={() => navigate("/admin/recompensas/logros/crear")} disabled={loading}>Crear logro</button>
			</div>
			{loading ? <p style={{ fontWeight: "bold", color: "white" }}>Cargando...</p> : error ? <p role="alert" style={{ fontWeight: "bold", color: "white" }}>{error}</p> : (
				<div className="admin-users-table-wrap">
					<table className="admin-users-table">
						<thead><tr><th>Nombre</th><th>Descripción</th><th>Visibilidad</th><th>Requisitos</th><th>Acciones</th></tr></thead>
						<tbody>{logros.length === 0 ? <tr><td colSpan={5}>No hay logros.</td></tr> : logros.map((logro) => (
							<tr key={logro.id ?? logro.nombre}><td>{logro.nombre ?? ""}</td><td>{logro.descripcion ?? ""}</td><td>{logro.oculto ? "Oculto" : "Visible"}</td><td>{Array.isArray(logro.requisitos) ? logro.requisitos.length : 0}</td><td><button type="button" className="admin-delete-button" aria-label="Borrar logro" onClick={() => handleDelete(logro.id)} disabled={deletingId === logro.id}><svg viewBox="0 0 24 24" role="img" aria-hidden="true" className="admin-icon"><path d="M9 3h6l1 1h4v2H4V4h4l1-1zm1 6h2v9h-2V9zm4 0h2v9h-2V9zM7 9h2v9H7V9zm-1 12h12a1 1 0 0 0 1-1V8H5v12a1 1 0 0 0 1 1z" /></svg></button></td></tr>
						))}</tbody>
					</table>
					<div className="admin-pagination"><button type="button" className="admin-secondary-button" onClick={() => setPage((prev) => Math.max(1, prev - 1))} disabled={loading || page <= 1}>Anterior</button><span className="admin-pagination__info">Página {page} de {totalPages} ({totalLogros} logros)</span><button type="button" className="admin-secondary-button" onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))} disabled={loading || page >= totalPages}>Siguiente</button></div>
				</div>
			)}
		</div>
	);
}