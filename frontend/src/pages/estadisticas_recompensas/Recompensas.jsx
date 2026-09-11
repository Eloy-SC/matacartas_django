import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import cabecera from "../../assets/cabecera.png";
import "../../styles/estadisticas.css";

const PAGE_SIZE = 10;

function PageControls({ page, totalPages, onPageChange, label }) {
	return (
		<div className="recompensas-pagination" aria-label={`Paginación de ${label}`}>
			<button
				type="button"
				className="estadisticas-history-button"
				onClick={() => onPageChange(Math.max(1, page - 1))}
				disabled={page <= 1}
			>
				Anterior
			</button>
			<span>Página {page} de {totalPages}</span>
			<button
				type="button"
				className="estadisticas-history-button"
				onClick={() => onPageChange(Math.min(totalPages, page + 1))}
				disabled={page >= totalPages}
			>
				Siguiente
			</button>
		</div>
	);
}

function ResourceImage({ src, alt }) {
	return src ? <img className="recompensa-image" src={src} alt={alt} /> : <div className="recompensa-image recompensa-image--empty" aria-hidden="true">?</div>;
}

export default function Recompensas() {
	const navigate = useNavigate();
	const [medallas, setMedallas] = useState(null);
	const [medallasPage, setMedallasPage] = useState(1);
	const [logros, setLogros] = useState(null);
	const [logrosPage, setLogrosPage] = useState(1);
	const [logrosOcultosPendientes, setLogrosOcultosPendientes] = useState(0);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");

	useEffect(() => {
		let cancelled = false;

		async function loadRecompensas() {
			setLoading(true);
			setError("");
			try {
				const [medallasResponse, logrosResponse, pendientesResponse] = await Promise.all([
					fetch(`/api/medallas/usuario/listar/?page=${medallasPage}`, { credentials: "include" }),
					fetch(`/api/logros/listar/?page=${logrosPage}`, { credentials: "include" }),
					fetch("/api/logros/ocultos/pendientes/", { credentials: "include" }),
				]);
				const [medallasData, logrosData, pendientesData] = await Promise.all([
					medallasResponse.json().catch(() => ({})),
					logrosResponse.json().catch(() => ({})),
					pendientesResponse.json().catch(() => ({})),
				]);

				if (!medallasResponse.ok || !logrosResponse.ok || !pendientesResponse.ok) {
					throw new Error(
						medallasData?.detail || logrosData?.detail || pendientesData?.detail || "No se pudieron cargar las recompensas",
					);
				}
				if (!cancelled) {
					setMedallas(medallasData);
					setLogros(logrosData);
					setLogrosOcultosPendientes(typeof pendientesData?.total === "number" ? pendientesData.total : 0);
				}
			} catch (requestError) {
				if (!cancelled) setError(requestError instanceof Error ? requestError.message : "Error cargando recompensas");
			} finally {
				if (!cancelled) setLoading(false);
			}
		}

		loadRecompensas();
		return () => { cancelled = true; };
	}, [medallasPage, logrosPage]);

	return (
		<div className="app estadisticas-page recompensas-page">
			<button className="partidas-volver-button estadisticas-volver-button" onClick={() => navigate("/inicio")}>
				⮜
			</button>
			<img src={cabecera} alt="Matacartas" style={{ maxWidth: "100%", height: "auto" }} />

			{loading && <p className="estadisticas-message">Cargando recompensas...</p>}
			{!loading && error && <p className="estadisticas-message estadisticas-message--error">{error}</p>}

			{!loading && !error && (
				<>
					<section className="form-card estadisticas-panel recompensas-panel" aria-label="Medallas del jugador">
						<h2>Medallas</h2>
						{medallas?.items?.length ? (
							<div className="recompensas-list">
								{medallas.items.map((medalla) => (
									<article className="recompensa-item" key={medalla.id}>
										<ResourceImage src={medalla.imagen} alt={`Imagen de ${medalla.nombre}`} />
										<div className="recompensa-item__content">
											<h3>{medalla.nombre}</h3>
											<span>{medalla.categoria}</span>
										</div>
									</article>
								))}
							</div>
						) : <p className="estadisticas-message">Todavía no has conseguido medallas.</p>}
						<PageControls
							page={medallas?.page ?? 1}
							totalPages={medallas?.total_pages ?? 1}
							onPageChange={setMedallasPage}
							label="medallas"
						/>
					</section>

					<section className="form-card estadisticas-panel recompensas-panel" aria-label="Logros del jugador">
						<div className="recompensas-heading">
							<h2>Logros</h2>
							<span>{logrosOcultosPendientes} ocultos por desbloquear</span>
						</div>
						{logros?.items?.length ? (
							<div className="recompensas-list">
								{logros.items.map((logro) => (
									<article className={`recompensa-item logro-item${logro.desbloqueado ? " logro-item--unlocked" : ""}`} key={logro.id}>
										<ResourceImage src={logro.imagen} alt={`Imagen de ${logro.nombre}`} />
										<div className="recompensa-item__content">
											<div className="logro-item__title">
												<h3>{logro.nombre}</h3>
												<span className={logro.desbloqueado ? "logro-status logro-status--unlocked" : "logro-status logro-status--locked"} aria-label={logro.desbloqueado ? "Desbloqueado" : "No desbloqueado"}>
													{logro.desbloqueado ? "✅" : "❌"}
												</span>
											</div>
											<p>{logro.descripcion}</p>
										</div>
									</article>
								))}
							</div>
						) : <p className="estadisticas-message">No hay logros disponibles.</p>}
						<PageControls
							page={logros?.page ?? 1}
							totalPages={logros?.total_pages ?? 1}
							onPageChange={setLogrosPage}
							label="logros"
						/>
					</section>
				</>
			)}
		</div>
	);
}
