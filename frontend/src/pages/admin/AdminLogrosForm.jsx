import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { obtenerCsrfToken } from "../../utils/ObtenerCsfrToken";
import "../../styles/admin.css";

const REQUISITO_OPTIONS = [
	["puntos_ganados_partida", "Puntos ganados en partida"],
	["puntuacion_acumulada", "Puntuación acumulada"],
	["puntos_ganados_mercader", "Puntos ganados con el Mercader"],
	["puntos_ganados_rebelde", "Puntos ganados con el Rebelde"],
	["puntos_ganados_segador", "Puntos ganados con el Segador"],
	["cartas_victimas_segador", "Cartas víctimas de segador"],
	["puntos_ganados_joyas_reales", "Puntos ganados con joyas reales"],
	["puntos_ganados_vinos_viejos", "Puntos ganados con vinos viejos"],
	["muertes_corrompidas_corruptor", "Muertes corrompidas con el Corruptor"],
	["tumbas_saqueadas_saqueador", "Tumbas saqueadas con el Saqueador"],
	["partidas_ganadas", "Partidas ganadas"],
	["cartas_kills", "Cartas rivales matadas"],
	["cartas_deaths", "Cartas propias matadas"],
	["rondas_ganadas", "Rondas ganadas"],
	["rondas_comodin_ganadas", "Rondas comodín ganadas"],
	["manos_ganadas", "Manos ganadas"],
	["retiradas", "Retiradas"],
	["manos_ganadas_unica", "Manos ganadas con carta única"],
	["contraataques_bastos_punt", "Contraataques con bastos puntiagudos"],
	["tickets_usados", "Tickets usados"],
];

const EMPTY_REQUIREMENT = {
	requisito: REQUISITO_OPTIONS[0][0],
	una_partida: false,
	valor_necesario: 1,
};

export default function AdminLogroForm() {
	const navigate = useNavigate();
	const { logroId } = useParams();
	const [nombre, setNombre] = useState("");
	const [descripcion, setDescripcion] = useState("");
	const [imagen, setImagen] = useState("");
	const [oculto, setOculto] = useState(false);
	const [requisitos, setRequisitos] = useState([]);
	const [requirementDraft, setRequirementDraft] = useState(EMPTY_REQUIREMENT);
	const [editingIndex, setEditingIndex] = useState(null);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");

	function updateRequirement(field, value) {
		setRequirementDraft((current) => ({ ...current, [field]: value }));
	}

	function saveRequirement(event) {
		event.preventDefault();
		const value = Number(requirementDraft.valor_necesario);
		if (!requirementDraft.requisito || !Number.isInteger(value) || value < 1) {
			setError("Cada requisito debe tener un tipo y un valor necesario mayor que cero.");
			return;
		}

		const normalized = { ...requirementDraft, valor_necesario: value };
		setRequisitos((current) => {
			if (editingIndex === null) return [...current, normalized];
			return current.map((item, index) => (index === editingIndex ? normalized : item));
		});
		setRequirementDraft(EMPTY_REQUIREMENT);
		setEditingIndex(null);
		setError("");
	}

	function editRequirement(index) {
		setRequirementDraft({ ...requisitos[index] });
		setEditingIndex(index);
		setError("");
	}

	function deleteRequirement(index) {
		setRequisitos((current) => current.filter((_, itemIndex) => itemIndex !== index));
		if (editingIndex === index) {
			setEditingIndex(null);
			setRequirementDraft(EMPTY_REQUIREMENT);
		}
	}

	async function handleSubmit(event) {
		event.preventDefault();
		setError("");
		if (logroId) {
			setError("Los logros no pueden editarse.");
			return;
		}
		if (!nombre.trim() || !descripcion.trim() || requisitos.length === 0) {
			setError("Completa el nombre, la descripción y añade al menos un requisito.");
			return;
		}
		if (!window.confirm("Este logro no podrá editarse después de crearlo. ¿Quieres continuar?")) return;

		setLoading(true);
		try {
			const csrfToken = await obtenerCsrfToken();
			const res = await fetch("/api/logros/admin/crear/", {
				method: "POST",
				credentials: "include",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrfToken,
				},
				body: JSON.stringify({
					nombre: nombre.trim(),
					descripcion: descripcion.trim(),
					imagen: imagen.trim() || null,
					oculto,
					requisitos,
				}),
			});
			const data = await res.json().catch(() => ({}));
			if (!res.ok) throw new Error(data?.detail || data?.nombre?.[0] || "No se pudo crear el logro");
			navigate("/admin/recompensas/logros");
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error creando logro");
		} finally {
			setLoading(false);
		}
	}

	return (
		<div className="app">
			<div className="admin-title-card"><h1 style={{ marginBottom: 0 }}>ADMINISTRACION - CREAR LOGRO</h1></div>
			<div className="admin-form-card" style={{ width: "min(100%, 760px)" }}>
				<form onSubmit={handleSubmit}>
					<div style={{ marginTop: 12 }}><label htmlFor="nombre">Nombre *</label><br /><input id="nombre" value={nombre} onChange={(e) => setNombre(e.target.value)} disabled={loading} /></div>
					<div style={{ marginTop: 12 }}><label htmlFor="descripcion">Descripción *</label><br /><textarea id="descripcion" rows="4" value={descripcion} onChange={(e) => setDescripcion(e.target.value)} disabled={loading} /></div>
					<div style={{ marginTop: 12 }}><label htmlFor="imagen">Imagen (URL)</label><br /><input id="imagen" type="url" placeholder="https://..." value={imagen} onChange={(e) => setImagen(e.target.value)} disabled={loading} /></div>
					<div style={{ marginTop: 12 }}><label htmlFor="oculto">Logro oculto</label><br /><input id="oculto" type="checkbox" className="admin-checkbox" checked={oculto} onChange={(e) => setOculto(e.target.checked)} disabled={loading} /></div>

					<section style={{ marginTop: 20 }} aria-labelledby="requisitos-title">
						<h2 id="requisitos-title">Requisitos del logro</h2>
						<div style={{ display: "grid", gap: 10 }}>
							<select value={requirementDraft.requisito} onChange={(e) => updateRequirement("requisito", e.target.value)} disabled={loading} aria-label="Tipo de requisito">
								{REQUISITO_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
							</select>
							<input type="number" min="1" step="1" value={requirementDraft.valor_necesario} onChange={(e) => updateRequirement("valor_necesario", e.target.value)} disabled={loading} aria-label="Valor necesario" />
							<label><input type="checkbox" className="admin-checkbox" checked={requirementDraft.una_partida} onChange={(e) => updateRequirement("una_partida", e.target.checked)} disabled={loading} /> Cumplir en una partida</label>
							<div>
								<button type="button" className="admin-secondary-button" onClick={saveRequirement} disabled={loading}>{editingIndex === null ? "Añadir requisito" : "Guardar requisito"}</button>
								{editingIndex !== null && <button type="button" className="admin-secondary-button" onClick={() => { setEditingIndex(null); setRequirementDraft(EMPTY_REQUIREMENT); }} style={{ marginLeft: 8 }} disabled={loading}>Cancelar edición</button>}
							</div>
						</div>
						{requisitos.length > 0 && <ul style={{ paddingLeft: 20 }}>{requisitos.map((item, index) => <li key={`${item.requisito}-${index}`} style={{ marginTop: 8 }}><strong>{REQUISITO_OPTIONS.find(([value]) => value === item.requisito)?.[1] ?? item.requisito}</strong> · {item.valor_necesario}{item.una_partida ? " · una partida" : " · acumulado"}<button type="button" className="admin-secondary-button" onClick={() => editRequirement(index)} style={{ marginLeft: 8 }} disabled={loading}>Editar</button><button type="button" className="admin-delete-button" onClick={() => deleteRequirement(index)} style={{ marginLeft: 8 }} disabled={loading}>Eliminar</button></li>)}</ul>}
					</section>

					<div style={{ marginTop: 20 }}><button type="submit" className="admin-primary-button" disabled={loading}>{loading ? "Creando..." : "Crear logro"}</button><button type="button" className="admin-secondary-button" onClick={() => navigate("/admin/recompensas/logros")} style={{ marginLeft: 8 }} disabled={loading}>Volver</button></div>
					{error && <p role="alert" style={{ marginTop: 12, whiteSpace: "pre-line", color: "red", fontWeight: "bold" }}>{error}</p>}
				</form>
			</div>
		</div>
	);
}
