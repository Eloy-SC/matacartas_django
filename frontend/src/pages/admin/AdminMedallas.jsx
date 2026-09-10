
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../../styles/admin.css";
import { obtenerCsrfToken } from "../../utils/ObtenerCsfrToken";

const CATEGORIA_LABELS = {
	oro: "ORO",
	plata: "PLATA",
	bronce: "BRONCE",
};

const ORDER_FIELDS = [
	{ value: "nombre", label: "Nombre" },
	{ value: "categoria", label: "Categoría" },
];

export default function AdminMedallas() {
	const navigate = useNavigate();
	const [medallas, setMedallas] = useState([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [deletingId, setDeletingId] = useState(null);
	const [search, setSearch] = useState("");
	const [debouncedSearch, setDebouncedSearch] = useState("");
	const [selectedCategoria, setSelectedCategoria] = useState("");
	const [orderBy, setOrderBy] = useState("nombre");
	const [orderDir, setOrderDir] = useState("asc");
	const [page, setPage] = useState(1);
	const [totalPages, setTotalPages] = useState(1);
	const [totalMedallas, setTotalMedallas] = useState(0);

	const loadMedallas = useCallback((pageNumber = 1) => {
		let cancelled = false;
		setLoading(true);
		setError("");

		const params = new URLSearchParams();
		params.set("page", String(pageNumber));
		if (debouncedSearch.trim()) params.set("search", debouncedSearch.trim());
		if (selectedCategoria) params.set("categoria", selectedCategoria);
		if (orderBy) params.set("ordering", orderDir === "desc" ? `-${orderBy}` : orderBy);

		fetch(`/api/medallas/listar/?${params.toString()}`, { method: "GET", credentials: "include" })
			.then(async (res) => {
				const data = await res.json().catch(() => ({}));
				if (cancelled) return;
				if (!res.ok) {
					const detail = data?.detail || "No se pudo cargar la lista de medallas";
					throw new Error(detail);
				}
				setMedallas(Array.isArray(data?.items) ? data.items : []);
				setPage(typeof data?.page === "number" ? data.page : pageNumber);
				setTotalPages(typeof data?.total_pages === "number" ? data.total_pages : 1);
				setTotalMedallas(typeof data?.total === "number" ? data.total : 0);
			})
			.catch((e) => {
				if (cancelled) return;
				setError(e instanceof Error ? e.message : "Error cargando medallas");
				setMedallas([]);
				setTotalMedallas(0);
				setTotalPages(1);
			})
			.finally(() => {
				if (cancelled) return;
				setLoading(false);
			});

		return () => {
			cancelled = true;
		};
	}, [debouncedSearch, selectedCategoria, orderBy, orderDir]);

	useEffect(() => {
		const cancel = loadMedallas(page);
		return () => {
			if (typeof cancel === "function") cancel();
		};
	}, [loadMedallas, page]);

	useEffect(() => {
		const timeoutId = setTimeout(() => setDebouncedSearch(search), 300);
		return () => clearTimeout(timeoutId);
	}, [search]);

	useEffect(() => {
		setPage(1);
	}, [debouncedSearch, selectedCategoria, orderBy, orderDir]);

	async function handleDelete(medallaId) {
		if (!medallaId || deletingId) return;
		const ok = window.confirm("¿Seguro que quieres eliminar esta medalla?");
		if (!ok) return;

		setDeletingId(medallaId);
		setError("");
		try {
			const csrfToken = await obtenerCsrfToken();

			const res = await fetch(`/api/medallas/admin/${medallaId}/eliminar/`, {
				method: "DELETE",
				credentials: "include",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrfToken,
				},
			});
			const data = await res.json().catch(() => ({}));
			if (!res.ok) {
				throw new Error(data?.detail || "No se pudo eliminar la medalla");
			}

			loadMedallas(page);
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error eliminando medalla");
		} finally {
			setDeletingId(null);
		}
	}

	return (
		<div className="app">
			<button className="admin-volver-button" onClick={() => navigate("/admin/recompensas")}>
				⮜
			</button>
			<div className="admin-title-card">
				<h1 style={{ marginBottom: 0 }}>ADMINISTRACION - MEDALLAS</h1>
			</div>
			<div className="admin-toolbar-card">
				<input
					type="search"
					className="admin-search-input"
					placeholder="Buscar medalla..."
					aria-label="Buscar medalla"
					value={search}
					onChange={(e) => setSearch(e.target.value)}
					disabled={loading}
				/>
				<select
					className="admin-search-input"
					value={selectedCategoria}
					onChange={(e) => setSelectedCategoria(e.target.value)}
					aria-label="Filtrar por categoría"
					disabled={loading}
				>
					<option value="">Todas las categorías</option>
					<option value="oro">Oro</option>
					<option value="plata">Plata</option>
					<option value="bronce">Bronce</option>
				</select>
				<select
					className="admin-search-input"
					value={orderBy}
					onChange={(e) => setOrderBy(e.target.value)}
					aria-label="Ordenar medallas por"
					disabled={loading}
				>
					{ORDER_FIELDS.map((field) => (
						<option key={field.value} value={field.value}>
							Ordenar: {field.label}
						</option>
					))}
				</select>
				<select
					className="admin-search-input"
					value={orderDir}
					onChange={(e) => setOrderDir(e.target.value)}
					aria-label="Dirección de ordenación"
					disabled={loading}
				>
					<option value="asc">Ascendente</option>
					<option value="desc">Descendente</option>
				</select>
				<button
					type="button"
					className="admin-primary-button"
					onClick={() => navigate("/admin/recompensas/medallas/crear")}
					disabled={loading}
				>
					Crear medalla
				</button>
			</div>
			{loading ? (
				<p style={{ fontWeight: "bold", color: "white" }}>Cargando...</p>
			) : error ? (
				<p role="alert" style={{ fontWeight: "bold", color: "white" }}>
					{error}
				</p>
			) : (
				<div className="admin-users-table-wrap">
					<table className="admin-users-table">
						<thead>
							<tr>
								<th>Nombre</th>
								<th>Categoria</th>
								<th>Imagen</th>
								<th>Acciones</th>
							</tr>
						</thead>
						<tbody>
							{medallas.length === 0 ? (
								<tr>
									<td colSpan={4}>No hay medallas.</td>
								</tr>
							) : (
								medallas.map((medalla) => (
									<tr key={medalla.id ?? medalla.nombre}>
										<td>{medalla.nombre ?? ""}</td>
										<td>{CATEGORIA_LABELS[medalla.categoria] ?? medalla.categoria ?? ""}</td>
										<td>
											{medalla.imagen ? (
												<img
													src={medalla.imagen}
													alt={`Imagen de ${medalla.nombre ?? "medalla"}`}
													style={{ width: 48, height: 48, objectFit: "cover", borderRadius: 6 }}
													onError={(e) => {
														e.currentTarget.style.display = "none";
													}}
												/>
											) : (
												"-"
											)}
										</td>
										<td>
											<div className="admin-actions">
												<button
													type="button"
													className="admin-icon-button"
													aria-label="Editar medalla"
													onClick={() => navigate(`/admin/recompensas/medallas/${medalla.id}`)}
													disabled={loading || deletingId === medalla.id}
												>
													<svg
														viewBox="0 0 24 24"
														role="img"
														aria-hidden="true"
														className="admin-icon"
													>
														<path d="M3 17.25V21h3.75L19.81 7.94l-3.75-3.75L3 17.25zm2.92 2.33H5v-.92l9.06-9.06.92.92L5.92 19.58zM20.71 6.04a1 1 0 0 0 0-1.41L19.37 3.3a1 1 0 0 0-1.41 0l-1.09 1.09 3.75 3.75 1.09-1.1z" />
													</svg>
												</button>
												<button
													type="button"
													className="admin-delete-button"
													aria-label="Borrar medalla"
													onClick={() => handleDelete(medalla.id)}
													disabled={loading || deletingId === medalla.id}
												>
													<svg
														viewBox="0 0 24 24"
														role="img"
														aria-hidden="true"
														className="admin-icon"
													>
														<path d="M9 3h6l1 1h4v2H4V4h4l1-1zm1 6h2v9h-2V9zm4 0h2v9h-2V9zM7 9h2v9H7V9zm-1 12h12a1 1 0 0 0 1-1V8H5v12a1 1 0 0 0 1 1z" />
													</svg>
												</button>
											</div>
										</td>
									</tr>
								))
							)}
						</tbody>
					</table>
					<div className="admin-pagination">
						<button
							type="button"
							className="admin-secondary-button"
							onClick={() => setPage((prev) => Math.max(1, prev - 1))}
							disabled={loading || page <= 1}
						>
							Anterior
						</button>
						<span className="admin-pagination__info">
							Página {page} de {totalPages} ({totalMedallas} medallas)
						</span>
						<button
							type="button"
							className="admin-secondary-button"
							onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
							disabled={loading || page >= totalPages}
						>
							Siguiente
						</button>
					</div>
				</div>
			)}
		</div>
	);
}