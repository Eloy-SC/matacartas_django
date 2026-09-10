import { useNavigate } from "react-router-dom";

export default function AdminRecompensas() {
	const navigate = useNavigate();

	return (
		<div className="app">
			<button className="admin-volver-button" onClick={() => navigate("/admin")}>
				⮜
			</button>
			<div className="admin-title-card">
				<h1 style={{ marginBottom: 0 }}>ADMINISTRACION - RECOMPENSAS</h1>
			</div>
			<div className="admin-form-card" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
				<button type="button" className="admin-primary-button" onClick={() => navigate("/admin/recompensas/medallas")}>
					MEDALLAS
				</button>
				<button type="button" className="admin-primary-button" onClick={() => navigate("/admin/recompensas/logros")}>
					LOGROS
				</button>
			</div>
		</div>
	);
}