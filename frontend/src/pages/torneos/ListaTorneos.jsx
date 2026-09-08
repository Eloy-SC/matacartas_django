import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import cabecera from "../../assets/cabecera.png";
import "../../styles/partidas.css";

const ESTADO_LABELS = {
	en_juego: "En curso",
	sala_espera: "Sin empezar",
	finalizado: "Finalizado",
	desconocido: "Desconocido",
};

const ESTADO_CLASS = {
	en_juego: "partidas-status partidas-status--en-juego",
	sala_espera: "partidas-status partidas-status--sala-espera",
	finalizado: "partidas-status partidas-status--desconocido",
	desconocido: "partidas-status partidas-status--desconocido",
};

const ORDER_FIELDS = [
	{ value: "nombre", label: "Nombre" },
	{ value: "rango_minimo_id", label: "Rango minimo" },
	{ value: "rango_maximo_id", label: "Rango maximo" },
	{ value: "num_jug_fin", label: "Jugadores final" },
	{ value: "fecha_creacion", label: "Fecha de creacion" },
];

function getEstadoLabel(estado) {
	if (!estado) return ESTADO_LABELS.desconocido;
	return ESTADO_LABELS[estado] ?? ESTADO_LABELS.desconocido;
}

function getEstadoClass(estado) {
	if (!estado) return ESTADO_CLASS.desconocido;
	return ESTADO_CLASS[estado] ?? ESTADO_CLASS.desconocido;
}

function formatFecha(value) {
	if (!value) return "-";

	const date = new Date(value);
	if (Number.isNaN(date.getTime())) return `${value}`;

	const now = new Date();
	const diffMs = now - date;

	const diffSeconds = Math.floor(diffMs / 1000);
	const diffMinutes = Math.floor(diffMs / (1000 * 60));
	const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

	if (diffSeconds < 60) {
		return `hace ${diffSeconds} s`;
	}

	if (diffMinutes < 60) {
		return `hace ${diffMinutes} min`;
	}

	if (diffHours < 48) {
		return `hace ${diffHours} h`;
	}

	return "hace varios dias";
}

function getFaseText(torneo) {
	const numJugOct = torneo?.num_jug_oct;
	const numJugCua = torneo?.num_jug_cua;
	const numJugSem = torneo?.num_jug_sem;
	const numJugFin = torneo?.num_jug_fin;

	return `F:${numJugFin ?? "-"} / SF:${numJugSem ?? "-"} / CF:${numJugCua ?? "-"} / OF:${numJugOct ?? "-"}`;
}

function getReglasText(torneo) {
	const reglas = [];
	if (torneo?.partidas_cartas_especiales) reglas.push("Cartas esp.");
	if (torneo?.partidas_tickets) reglas.push("Tickets");
	if (torneo?.desempate_mayor_punt) reglas.push("Desempate por puntuacion");
	return reglas.length > 0 ? reglas.join(", ") : "Sin extras";
}

export default function ListaTorneos() {
	const navigate = useNavigate();
	const [torneos, setTorneos] = useState([]);
	const [rangos, setRangos] = useState([]);
	const [page, setPage] = useState(1);
	const [totalPages, setTotalPages] = useState(1);
	const [totalTorneos, setTotalTorneos] = useState(0);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [search, setSearch] = useState("");
	const [debouncedSearch, setDebouncedSearch] = useState("");
	const [selectedRangoMin, setSelectedRangoMin] = useState("");
	const [selectedRangoMax, setSelectedRangoMax] = useState("");
	const [orderBy, setOrderBy] = useState("id");
	const [orderDir, setOrderDir] = useState("asc");

	const DURACION_MANOS = {
		corta: "20",
		normal: "40",
		larga: "60",
	};

	const loadRangos = useCallback(() => {
		let cancelled = false;

		fetch("/api/rangos/listar/", {
			method: "GET",
			credentials: "include",
		})
			.then(async (res) => {
				const data = await res.json().catch(() => []);
				if (cancelled) return;
				if (!res.ok) {
					throw new Error(data?.detail || "No se pudo cargar la lista de rangos");
				}
				setRangos(Array.isArray(data) ? data : []);
			})
			.catch(() => {
				if (cancelled) return;
				setRangos([]);
			});

		return () => {
			cancelled = true;
		};
	}, []);

	const loadTorneos = useCallback(
		(pageNumber = 1) => {
			let cancelled = false;
			setLoading(true);
			setError("");

			const params = new URLSearchParams();
			params.set("page", String(pageNumber));
			if (debouncedSearch.trim()) {
				params.set("search", debouncedSearch.trim());
			}
			if (selectedRangoMin) {
				params.set("rango_minimo_id", selectedRangoMin);
			}
			if (selectedRangoMax) {
				params.set("rango_maximo_id", selectedRangoMax);
			}
			if (orderBy) {
				const orderingValue = orderDir === "desc" ? `-${orderBy}` : orderBy;
				params.set("ordering", orderingValue);
			}

			fetch(`/api/torneos/publicos/?${params.toString()}`, {
				method: "GET",
				credentials: "include",
			})
				.then(async (res) => {
					const data = await res.json().catch(() => ({}));
					if (cancelled) return;
					if (!res.ok) {
						const detail = data?.detail || "No se pudo cargar la lista de torneos";
						throw new Error(detail);
					}
					const items = Array.isArray(data?.items) ? data.items : [];

					if (cancelled) return;
					setTorneos(items);
					setPage(typeof data?.page === "number" ? data.page : pageNumber);
					setTotalPages(typeof data?.total_pages === "number" ? data.total_pages : 1);
					setTotalTorneos(typeof data?.total === "number" ? data.total : 0);
				})
				.catch((e) => {
					if (cancelled) return;
					setError(e instanceof Error ? e.message : "Error cargando torneos");
					setTorneos([]);
					setTotalTorneos(0);
					setTotalPages(1);
				})
				.finally(() => {
					if (cancelled) return;
					setLoading(false);
				});

			return () => {
				cancelled = true;
			};
		},
		[debouncedSearch, selectedRangoMin, selectedRangoMax, orderBy, orderDir]
	);

	useEffect(() => {
		const cancel = loadRangos();
		return () => {
			if (typeof cancel === "function") cancel();
		};
	}, [loadRangos]);

	useEffect(() => {
		const cancel = loadTorneos(page);
		return () => {
			if (typeof cancel === "function") cancel();
		};
	}, [loadTorneos, page]);

	useEffect(() => {
		const timeoutId = setTimeout(() => {
			setDebouncedSearch(search);
		}, 300);
		return () => {
			clearTimeout(timeoutId);
		};
	}, [search]);

	useEffect(() => {
		setPage(1);
	}, [debouncedSearch, selectedRangoMin, selectedRangoMax, orderBy, orderDir]);

	const emptyMessage = debouncedSearch.trim()
		? "No hay torneos que coincidan con la busqueda."
		: "No hay torneos.";

	return (
		<div className="app">
			<button className="partidas-volver-button" onClick={() => navigate("/inicio")}>
				⮜
			</button>
			<img src={cabecera} alt="Matacartas" style={{ maxWidth: "100%", height: "auto" }} />
			<div className="partidas-toolbar-card">
				<input
					type="search"
					className="partidas-search-input"
					placeholder="Buscar torneo..."
					aria-label="Buscar torneo"
					value={search}
					onChange={(e) => setSearch(e.target.value)}
					disabled={loading}
				/>
				<select
					className="partidas-search-input"
					value={selectedRangoMin}
					onChange={(e) => setSelectedRangoMin(e.target.value)}
					aria-label="Filtrar por rango minimo"
					disabled={loading}
				>
					<option value="">Rango minimo</option>
					{rangos.map((rango) => (
						<option key={rango.id ?? rango.nombre} value={rango.id ?? ""}>
							{rango.nombre ?? ""}
						</option>
					))}
				</select>
				<select
					className="partidas-search-input"
					value={selectedRangoMax}
					onChange={(e) => setSelectedRangoMax(e.target.value)}
					aria-label="Filtrar por rango maximo"
					disabled={loading}
				>
					<option value="">Rango maximo</option>
					{rangos.map((rango) => (
						<option key={rango.id ?? rango.nombre} value={rango.id ?? ""}>
							{rango.nombre ?? ""}
						</option>
					))}
				</select>
				<select
					className="partidas-search-input"
					value={orderBy}
					onChange={(e) => setOrderBy(e.target.value)}
					aria-label="Ordenar por"
					disabled={loading}
				>
					{ORDER_FIELDS.map((field) => (
						<option key={field.value} value={field.value}>
							Ordenar: {field.label}
						</option>
					))}
				</select>
				<select
					className="partidas-search-input"
					value={orderDir}
					onChange={(e) => setOrderDir(e.target.value)}
					aria-label="Ordenar direccion"
					disabled={loading}
				>
					<option value="asc">Ascendente</option>
					<option value="desc">Descendente</option>
				</select>
				<button
					type="button"
					className="partidas-secondary-button"
					onClick={() => loadTorneos(page)}
					disabled={loading}
				>
					Actualizar
				</button>
			</div>
			{loading ? (
				<p style={{ fontWeight: "bold" }}>Cargando...</p>
			) : error ? (
				<p role="alert" style={{ fontWeight: "bold" }}>
					{error}
				</p>
			) : (
				<div className="partidas-table-wrap">
					<table className="partidas-table">
						<thead>
							<tr>
								<th>Nombre</th>
								<th>Rango minimo</th>
								<th>Rango maximo</th>
								<th>Formato</th>
								<th>Manos/partida</th>
								<th>Reglas</th>
								<th>Creado</th>
								<th>Estado</th>
								<th> </th>
							</tr>
						</thead>
						<tbody>
							{torneos.length === 0 ? (
								<tr>
									<td colSpan={8}>{emptyMessage}</td>
								</tr>
							) : (
								torneos.map((torneo, index) => {
									const rowKey = torneo?.id ?? `${torneo?.nombre ?? "torneo"}-${index}`;
									const fechaCreacion = formatFecha(torneo?.fecha_creacion);
									return (
										<tr key={rowKey}>
											<td>{torneo?.nombre ?? ""}</td>
											<td>{torneo?.rango_minimo ?? "-"}</td>
											<td>{torneo?.rango_maximo ?? "-"}</td>
											<td>{getFaseText(torneo)}</td>
											<td>{DURACION_MANOS[torneo?.partidas_longitud] ?? "-"}</td>
											<td>{getReglasText(torneo)}</td>
											<td>{fechaCreacion}</td>
											<td>
												<span className={getEstadoClass(torneo?.estado)}>
													{getEstadoLabel(torneo?.estado)}
												</span>
											</td>
											<td>
												<button
													type="button"
													className="partidas-primary-button"
													onClick={() => navigate(`/torneos/${torneo?.id ?? ""}`)}
												>
													Ver
												</button>
											</td>
										</tr>
									);
								})
							)}
						</tbody>
					</table>
					<div className="partidas-pagination">
						<button
							type="button"
							className="partidas-secondary-button"
							onClick={() => setPage((prev) => Math.max(1, prev - 1))}
							disabled={loading || page <= 1}
						>
							Anterior
						</button>
						<span className="partidas-pagination__info">
							Pagina {page} de {totalPages} ({totalTorneos} torneos)
						</span>
						<button
							type="button"
							className="partidas-secondary-button"
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
