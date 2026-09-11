import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import defaultProfilePic from "../assets/default_profile_pic.png";
import cabecera from "../assets/cabecera.png";
import "../styles/rangos.css";
import UserRango from "../utils/UserRango.jsx";
import { obtenerCsrfToken } from "../utils/ObtenerCsfrToken";

export default function Inicio() {
	const navigate = useNavigate();
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [profileImageUrl, setProfileImageUrl] = useState("");
	const [avatarError, setAvatarError] = useState(false);
	const [isStaff, setIsStaff] = useState(false);
	const [showClasificacion, setShowClasificacion] = useState(false);
	const [topUsers, setTopUsers] = useState([]);
	const [topLoading, setTopLoading] = useState(false);
	const [topError, setTopError] = useState("");
	const [currentUserId, setCurrentUserId] = useState(null);

	const avatarSrc = profileImageUrl && !avatarError ? profileImageUrl : defaultProfilePic;

	useEffect(() => {
		let cancelled = false;
		setAvatarError(false);

		fetch("/api/auth/me/", { method: "GET", credentials: "include" })
			.then((res) => res.json())
			.then((data) => {
				if (cancelled) return;
				const imagen = data?.imagen;
				setProfileImageUrl(typeof imagen === "string" ? imagen : "");
				setIsStaff(Boolean(data?.is_staff));
				setCurrentUserId(data?.id ?? null);
			})
			.catch(() => {
				if (cancelled) return;
				setProfileImageUrl("");
				setIsStaff(false);
				setCurrentUserId(null);
			});

		return () => {
			cancelled = true;
		};
	}, []);

	useEffect(() => {
		if (!showClasificacion) return;
		let cancelled = false;
		setTopLoading(true);
		setTopError("");

		fetch("/api/users/top/", { method: "GET", credentials: "include" })
			.then(async (res) => {
				const data = await res.json().catch(() => ([]));
				if (!res.ok) {
					const detail = data?.detail || "No se pudo cargar la clasificación";
					throw new Error(detail);
				}
				const items = Array.isArray(data) ? data : [];

				const itemsWithRango = await Promise.all(
					items.map(async (user) => {
						if (!user?.id) return { ...user, rango_nombre: "" };
						try {
							const rangoRes = await fetch(`/api/rangos/usuario/${user.id}/`, {
								method: "GET",
								credentials: "include",
							});
							const rangoData = await rangoRes.json().catch(() => ({}));
							if (!rangoRes.ok) {
								return { ...user, rango_nombre: "" };
							}
							return {
								...user,
								rango_nombre: rangoData?.nombre ?? "",
								rango_color: rangoData?.color ?? "",
							};
						} catch (e) {
							return { ...user, rango_nombre: "" };
						}
					})
				);

				if (cancelled) return;
				setTopUsers(itemsWithRango);
			})
			.catch((e) => {
				if (cancelled) return;
				setTopError(e instanceof Error ? e.message : "Error cargando clasificación");
				setTopUsers([]);
			})
			.finally(() => {
				if (cancelled) return;
				setTopLoading(false);
			});

		return () => {
			cancelled = true;
		};
	}, [showClasificacion]);

	async function handleLogout() {
		setLoading(true);
		setError("");
		try {
			const csrfToken = await obtenerCsrfToken();

			const logoutRes = await fetch("/api/auth/logout/", {
				method: "POST",
				credentials: "include",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrfToken,
				},
			});
			if (!logoutRes.ok) {
				const data = await logoutRes.json().catch(() => ({}));
				throw new Error(data.detail || "No se pudo cerrar sesión");
			}

			navigate("/login", { replace: true });
		} catch (e) {
			setError(e instanceof Error ? e.message : "Error cerrando sesión");
		} finally {
			setLoading(false);
		}
	}

	return (
		<div className="app app--with-avatar">
			{isStaff && (
				<button
					type="button"
					className="admin-inicio-button"
					onClick={() => navigate("/admin")}
					aria-label="Panel de administración"
				>
					ADMINISTRACIÓN
				</button>
			)}
			<img src={cabecera} alt="Matacartas" style={{maxWidth: "100%", height: "auto"}} />
			<button
				type="button"
				className="rec-inicio-button"
				onClick={() => navigate("/recompensas")}
				aria-label="Ver recompensas"
			>
				🎁
			</button>
			<button
				type="button"
				className="estad-inicio-button"
				onClick={() => navigate("/estadisticas")}
				aria-label="Ver estadísticas"
			>
				📊
			</button>
			<button
				type="button"
				className="clasif-inicio-button"
				onClick={() => setShowClasificacion(true)}
				aria-label="Ver clasificación"
			>
				🏆
			</button>
			<button
				type="button"
				className="avatar-button"
				onClick={() => navigate("/perfil?mode=view")}
				aria-label="Ir al perfil"
			>
				<img
					className="avatar-img"
					src={avatarSrc}
					alt="Foto de perfil"
					onError={() => {
						if (profileImageUrl) setAvatarError(true);
					}}
				/>
			</button>
			{showClasificacion && (
				<div
					className="form-card"
					style={{
						position: "fixed",
						top: "50%",
						left: "50%",
						transform: "translate(-50%, -50%)",
						zIndex: 10,
					}}
				>
					<button
						type="button"
						onClick={() => setShowClasificacion(false)}
						aria-label="Cerrar"
						className="close-card-button"
					>
						X
					</button>
					<h2>Clasificacion</h2>
					{topLoading ? (
						<p style={{ fontWeight: "bold" }}>Cargando...</p>
					) : topError ? (
						<p role="alert">{topError}</p>
					) : (
						<div className="clasif-table-wrap">
							<table className="clasif-table">
								<thead>
									<tr>
										<th aria-hidden="true"></th>
										<th aria-hidden="true"></th>
										<th>Nombre</th>
										<th>Rango</th>
										<th>Puntuación</th>
									</tr>
								</thead>
								<tbody>
									{topUsers.length === 0 ? (
										<tr>
											<td colSpan={5}>No hay datos.</td>
										</tr>
									) : (
										topUsers.flatMap((user, index) => {
											const rowKey = user.id ?? user.username ?? user.nombre ?? index;
											const isCurrentUser =
												currentUserId !== null && user.id === currentUserId;
											const hasSeparator =
												typeof user?.posicion === "number" && user.posicion > 10;

											const row = (
												<tr
													key={`row-${rowKey}`}
													className={isCurrentUser ? "clasif-row--current" : undefined}
												>
													<td>{user.posicion}</td>
													<td className="clasif-avatar-cell">
														<img
															className="clasif-avatar"
															src={user.imagen || defaultProfilePic}
															alt={`Foto de ${user.nombre ?? "usuario"}`}
															onError={(event) => {
																event.currentTarget.src = defaultProfilePic;
															}}
														/>
													</td>
													<td>{user.nombre ?? ""}</td>
													<td>
														<UserRango userId={user.id} />
													</td>
													<td>
														{typeof user.puntuacion === "number"
															? user.puntuacion
															: user.puntuacion ?? ""}
													</td>
												</tr>
											);

											if (hasSeparator && index > 0) {
												return [
													<tr key={`sep-${rowKey}`} className="clasif-separator-row" aria-hidden="true">
														<td colSpan={5}></td>
													</tr>,
													row,
												];
											}

											return row;
										})
									)}
								</tbody>
							</table>
						</div>
					)}
				</div>
			)}
			<div className="form-card">
				<div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 16 }}>
					<button type="button" className="main-primary-button" onClick={() => navigate("/partidas")}>
						BUSCA PARTIDA
					</button>
					<p style={{ margin: "12px 0", fontWeight: "bold" }}>     o      </p>
					<button type="button" className="main-primary-button" onClick={() => navigate("/crear-partida")}>
						CREA UNA PARTIDA
					</button>
				</div>
				<div style={{ display: "flex", flexDirection: "row", alignItems: "center", gap: 16 }}>
					<button type="button" className="main-primary-button" onClick={() => navigate("/torneos")}>
						BUSCA TORNEO
					</button>
					<p style={{ margin: "12px 0", fontWeight: "bold" }}>     o      </p>
					<button type="button" className="main-primary-button" onClick={() => navigate("/crear-torneo")}>
						CREA UN TORNEO
					</button>
				</div>
				<button type="button" className="main-primary-button" onClick={handleLogout} disabled={loading}>
					{loading ? "Cerrando sesión..." : "Cerrar sesión"}
				</button>
				{error && (
					<p role="alert" style={{ marginTop: 12 }}>
						{error}
					</p>
				)}
			</div>
		</div>
	);
}
