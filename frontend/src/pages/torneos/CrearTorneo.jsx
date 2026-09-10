import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import cabecera from "../../assets/cabecera.png";
import "../../styles/partidas.css";
import { formatApiError } from "../../utils/ApiErrors.jsx";
import { obtenerCsrfToken } from "../../utils/ObtenerCsfrToken";

const JUGADORES_OPTIONS = [2, 3, 4];

const LONGITUD_OPTIONS = [
	{ value: "express", label: "Express (5 manos)" },
	{ value: "corta", label: "Corta (20 manos)" },
	{ value: "normal", label: "Normal (40 manos)" },
	{ value: "larga", label: "Larga (60 manos)" },
];

export default function CrearTorneo() {
	const navigate = useNavigate();
	const [rangos, setRangos] = useState([]);
	const [rangosLoading, setRangosLoading] = useState(true);
	const [rangosError, setRangosError] = useState("");
	const [medallas, setMedallas] = useState([]);
	const [medallasLoading, setMedallasLoading] = useState(true);
	const [medallasError, setMedallasError] = useState("");
	const [incluirCuartos, setIncluirCuartos] = useState(true);
	const [incluirOctavos, setIncluirOctavos] = useState(false);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [successMessage, setSuccessMessage] = useState("");
	const [numJugFin, setNumJugFin] = useState(3);

	useEffect(() => {
		let cancelled = false;
		setRangosLoading(true);
		setRangosError("");

		fetch("/api/rangos/listar/", {
			method: "GET",
			credentials: "include",
		})
			.then(async (res) => {
				const data = await res.json().catch(() => []);
				if (cancelled) return;
				if (!res.ok) {
					const detail = data?.detail || "No se pudieron cargar los rangos";
					throw new Error(detail);
				}
				setRangos(Array.isArray(data) ? data : []);
			})
			.catch((e) => {
				if (cancelled) return;
				setRangosError(e instanceof Error ? e.message : "Error cargando rangos");
				setRangos([]);
			})
			.finally(() => {
				if (cancelled) return;
				setRangosLoading(false);
			});

		return () => {
			cancelled = true;
		};
	}, []);

	useEffect(() => {
		let cancelled = false;
		setMedallasLoading(true);
		setMedallasError("");

		fetch("/api/medallas/listar/", {
			method: "GET",
			credentials: "include",
		})
			.then(async (res) => {
				const data = await res.json().catch(() => []);
				if (cancelled) return;
				if (!res.ok) {
					const detail = data?.detail || "No se pudieron cargar las medallas";
					throw new Error(detail);
				}
				setMedallas(Array.isArray(data) ? data : (Array.isArray(data?.items) ? data.items : []));
			})
			.catch((e) => {
				if (cancelled) return;
				setMedallasError(e instanceof Error ? e.message : "Error cargando medallas");
				setMedallas([]);
			})
			.finally(() => {
				if (cancelled) return;
				setMedallasLoading(false);
			});

		return () => {
			cancelled = true;
		};
	}, []);

	const rangoPlaceholder = rangosLoading
		? "Cargando rangos..."
		: rangosError
			? "Error cargando rangos"
			: "Selecciona un rango";

	const medallaPlaceholder = medallasLoading
		? "Cargando medallas..."
		: medallasError
			? "Error cargando medallas"
			: "Selecciona una medalla";

	async function handleSubmit(event) {
		event.preventDefault();
		setError("");
		setSuccessMessage("");

		const formData = new FormData(event.currentTarget);
		const nombre = `${formData.get("nombre") ?? ""}`.trim();
		const rangoMinimoValue = formData.get("rangoMinimo");
		const rangoMaximoValue = formData.get("rangoMaximo");
		const numJugFinValue = formData.get("numJugFin");
		const numJugSemValue = formData.get("numJugSem");
		const numJugCuaValue = formData.get("numJugCua");
		const numJugOctValue = formData.get("numJugOct");
		const tiempoValue = formData.get("tiempoMaximo");

		if (!nombre) {
			setError("Introduce el nombre del torneo");
			return;
		}

		const num_jug_fin = numJugFinValue ? Number(numJugFinValue) : 3;
		const num_jug_sem = numJugSemValue ? Number(numJugSemValue) : 3;
		const num_jug_cua = incluirCuartos && numJugCuaValue ? Number(numJugCuaValue) : null;
		const num_jug_oct = incluirOctavos && numJugOctValue ? Number(numJugOctValue) : null;
		const partidas_tiempo_max_turno = tiempoValue ? Number(tiempoValue) : 90;

		const medalla_primer_puesto = formData.get("medallaPrimerPuesto");
		const medalla_segundo_puesto = formData.get("medallaSegundoPuesto");
		const medalla_tercer_puesto = formData.get("medallaTercerPuesto");

		if ([num_jug_fin, num_jug_sem, partidas_tiempo_max_turno].some((value) => Number.isNaN(value))) {
			setError("Revisa los valores numéricos del formulario");
			return;
		}

		if (incluirCuartos && Number.isNaN(num_jug_cua)) {
			setError("El número de jugadores de cuartos no es válido");
			return;
		}

		if (incluirOctavos && Number.isNaN(num_jug_oct)) {
			setError("El número de jugadores de octavos no es válido");
			return;
		}

		const payload = {
			nombre,
			rango_minimo_id: rangoMinimoValue ? Number(rangoMinimoValue) : null,
			rango_maximo_id: rangoMaximoValue ? Number(rangoMaximoValue) : null,
			num_jug_fin,
			num_jug_sem,
			num_jug_cua,
			num_jug_oct,
			partidas_longitud: formData.get("longitud") || "normal",
			partidas_cartas_especiales: Boolean(formData.get("cartasEspeciales")),
			partidas_tickets: Boolean(formData.get("tickets")),
			partidas_tiempo_max_turno,
			desempate_mayor_punt: Boolean(formData.get("desempateMayorPunt")),
			medalla_primer_puesto_id: medalla_primer_puesto ? Number(medalla_primer_puesto) : null,
			medalla_segundo_puesto_id: medalla_segundo_puesto ? Number(medalla_segundo_puesto) : null,
			medalla_tercer_puesto_id: num_jug_fin >= 3 && medalla_tercer_puesto ? Number(medalla_tercer_puesto) : null,
		};

		setLoading(true);
		try {
			const csrfToken = await obtenerCsrfToken();

			const res = await fetch("/api/torneos/crear/", {
				method: "POST",
				credentials: "include",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrfToken,
				},
				body: JSON.stringify(payload),
			});

			const data = await res.json().catch(() => ({}));
			if (!res.ok) {
				throw new Error(formatApiError(data) || "No se pudo crear el torneo");
			}

			setSuccessMessage("Torneo creado");
			const idTorneo = data?.id;
			if (!idTorneo) {
				throw new Error("No se pudo obtener el ID del torneo");
			}
			navigate(`/torneos/${idTorneo}`);
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error creando torneo");
		} finally {
			setLoading(false);
		}
	}

	return (
		<div className="app">
			<button className="partidas-volver-button" onClick={() => navigate("/inicio")}>
				⮜
			</button>
			<img src={cabecera} alt="Matacartas" style={{ maxWidth: "100%", height: "auto" }} />
			<div className="form-card">
				<form onSubmit={handleSubmit}>
					<div style={{ marginTop: 12 }}>
						<label htmlFor="nombre">Nombre del torneo</label>
						<br />
						<input id="nombre" name="nombre" type="text" maxLength={39} placeholder="Hasta 39 caracteres" />
					</div>
					<div style={{ marginTop: 12 }}>
						<label htmlFor="rangoMinimo">Rango minimo</label>
						<br />
						<select id="rangoMinimo" name="rangoMinimo" disabled={rangosLoading || Boolean(rangosError)}>
							<option value="">{rangoPlaceholder}</option>
							{rangos.map((rango) => (
								<option key={rango.id} value={rango.id}>
									{rango.nombre}
								</option>
							))}
						</select>
					</div>
					<div style={{ marginTop: 12 }}>
						<label htmlFor="rangoMaximo">Rango maximo</label>
						<br />
						<select id="rangoMaximo" name="rangoMaximo" disabled={rangosLoading || Boolean(rangosError)}>
							<option value="">{rangoPlaceholder}</option>
							{rangos.map((rango) => (
								<option key={rango.id} value={rango.id}>
									{rango.nombre}
								</option>
							))}
						</select>
					</div>

					<div style={{ marginTop: 12 }}>
						<label htmlFor="numJugFin">Jugadores por partida en final</label>
						<br />
						<select id="numJugFin" name="numJugFin" defaultValue={3} onChange={(e) => setNumJugFin(Number(e.target.value))}>
							{JUGADORES_OPTIONS.map((value) => (
								<option key={value} value={value}>
									{value}
								</option>
							))}
						</select>
					</div>

					<div style={{ marginTop: 12 }}>
						<label htmlFor="numJugSem">Jugadores por partida en semifinal</label>
						<br />
						<select id="numJugSem" name="numJugSem" defaultValue={3}>
							{JUGADORES_OPTIONS.map((value) => (
								<option key={value} value={value}>
									{value}
								</option>
							))}
						</select>
					</div>

					<div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 8 }}>
						<input
							id="incluirCuartos"
							type="checkbox"
							checked={incluirCuartos}
							onChange={(event) => {
								setIncluirCuartos(event.target.checked);
								if (!event.target.checked) {
									setIncluirOctavos(false);
								}
							}}
						/>
						<label htmlFor="incluirCuartos">Incluir cuartos</label>
					</div>
					{incluirCuartos && (
						<div style={{ marginTop: 12 }}>
							<label htmlFor="numJugCua">Jugadores por partida en cuartos</label>
							<br />
							<select id="numJugCua" name="numJugCua" defaultValue={3}>
								{JUGADORES_OPTIONS.map((value) => (
									<option key={value} value={value}>
										{value}
									</option>
								))}
							</select>
						</div>
					)}

					<div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 8 }}>
						<input
							id="incluirOctavos"
							type="checkbox"
							checked={incluirOctavos}
							onChange={(event) => setIncluirOctavos(event.target.checked)}
							disabled={!incluirCuartos}
						/>
						<label htmlFor="incluirOctavos">Incluir octavos</label>
					</div>
					{incluirCuartos && incluirOctavos && (
						<div style={{ marginTop: 12 }}>
							<label htmlFor="numJugOct">Jugadores por partida en octavos</label>
							<br />
							<select id="numJugOct" name="numJugOct" defaultValue={3}>
								{JUGADORES_OPTIONS.map((value) => (
									<option key={value} value={value}>
										{value}
									</option>
								))}
							</select>
						</div>
					)}

					<div style={{ marginTop: 12 }}>
						<label htmlFor="longitud">Longitud de las partidas</label>
						<br />
						<select id="longitud" name="longitud" defaultValue="normal">
							{LONGITUD_OPTIONS.map((option) => (
								<option key={option.value} value={option.value}>
									{option.label}
								</option>
							))}
						</select>
					</div>

					<div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 8 }}>
						<input id="cartasEspeciales" name="cartasEspeciales" type="checkbox" defaultChecked />
						<label htmlFor="cartasEspeciales">Cartas especiales</label>
					</div>
					<div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 8 }}>
						<input id="tickets" name="tickets" type="checkbox" defaultChecked />
						<label htmlFor="tickets">Tickets</label>
					</div>
					<div style={{ marginTop: 12 }}>
						<label htmlFor="tiempoMaximo">Tiempo maximo por turno (segundos)</label>
						<br />
						<input id="tiempoMaximo" name="tiempoMaximo" type="number" defaultValue={90} />
					</div>
					<div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 8 }}>
						<input id="desempateMayorPunt" name="desempateMayorPunt" type="checkbox" defaultChecked />
						<label htmlFor="desempateMayorPunt">Desempate por mayor puntuacion</label>
					</div>

				<div style={{ marginTop: 20, borderTop: "1px solid #ccc", paddingTop: 16 }}>
					<h3 style={{ marginTop: 0 }}>Medallas del torneo</h3>

					<div style={{ marginTop: 12 }}>
						<label htmlFor="medallaPrimerPuesto">Medalla primer puesto</label>
						<br />
						<select id="medallaPrimerPuesto" name="medallaPrimerPuesto" disabled={medallasLoading || Boolean(medallasError)}>
							<option value="">{medallaPlaceholder}</option>
							{medallas.filter((medalla) => medalla.categoria === "oro").map((medalla) => (
								<option key={medalla.id} value={medalla.id}>
									{medalla.nombre}
								</option>
							))}
						</select>
					</div>

					<div style={{ marginTop: 12 }}>
						<label htmlFor="medallaSegundoPuesto">Medalla segundo puesto</label>
						<br />
						<select id="medallaSegundoPuesto" name="medallaSegundoPuesto" disabled={medallasLoading || Boolean(medallasError)}>
							<option value="">{medallaPlaceholder}</option>
							{medallas.filter((medalla) => medalla.categoria === "plata").map((medalla) => (
								<option key={medalla.id} value={medalla.id}>
									{medalla.nombre}
								</option>
							))}
						</select>
					</div>

					{numJugFin >= 3 && (
						<div style={{ marginTop: 12 }}>
							<label htmlFor="medallaTercerPuesto">Medalla tercer puesto</label>
							<br />
							<select id="medallaTercerPuesto" name="medallaTercerPuesto" disabled={medallasLoading || Boolean(medallasError)}>
								<option value="">{medallaPlaceholder}</option>
								{medallas.filter((medalla) => medalla.categoria === "bronce").map((medalla) => (
									<option key={medalla.id} value={medalla.id}>
										{medalla.nombre}
									</option>
								))}
							</select>
						</div>
					)}
				</div>

				<div style={{ marginTop: 16, gap: 8 }}>
					<button type="submit" className="partidas-primary-button" disabled={loading || rangosLoading || medallasLoading}>
							{loading ? "Creando..." : "Crear"}
						</button>
					</div>
					{error && (
						<p role="alert" style={{ marginTop: 12, color: "red", fontWeight: "bold" }}>
							{error}
						</p>
					)}
					{successMessage && (
						<p style={{ marginTop: 12, color: "green", fontWeight: "bold" }}>{successMessage}</p>
					)}
				</form>
			</div>
		</div>
	);
}
