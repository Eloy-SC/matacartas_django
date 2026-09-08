

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import cabecera from "../../assets/cabecera.png";
import "../../styles/estadisticas.css";

const metricasPrincipales = [
    { key: "partidas_totales", label: "Partidas totales" },
    { key: "partidas_finalizadas", label: "Partidas finalizadas" },
    { key: "manos_jugadas", label: "Manos jugadas" },
    { key: "cartas_matadas", label: "Cartas matadas" },
    { key: "retiradas", label: "Retiradas" },
];

const estadoPartidas = [
    { key: "partidas_en_sala_espera", label: "En sala de espera" },
    { key: "partidas_en_curso", label: "En curso" },
];

const records = [
    { key: "mas_puntos_en_partida", label: "Más puntos en una partida", suffix: "puntos" },
    { key: "mas_cartas_matadas_en_partida", label: "Más cartas matadas en una partida", suffix: "cartas" },
    { key: "mas_retiradas_en_partida", label: "Más retiradas en una partida", suffix: "retiradas" },
];

const metricasIndividuales = [
    { key: "partidas_jugadas", label: "Partidas jugadas", suffix: "partidas" },
    { key: "cartas_matadas", label: "Cartas matadas", suffix: "cartas" },
    { key: "muertes_recibidas", label: "Muertes recibidas", suffix: "muertes" },
    { key: "retiradas", label: "Retiradas", suffix: "retiradas" },
    { key: "puntos_ganados", label: "Puntos ganados", suffix: "puntos" },
];

const recordsIndividuales = [
    { key: "puntos_ganados_en_una_partida", label: "Más puntos en una partida", suffix: "puntos" },
    { key: "cartas_matadas_en_una_partida", label: "Más cartas matadas en una partida", suffix: "cartas" },
    { key: "muertes_recibidas_en_una_partida", label: "Más muertes recibidas en una partida", suffix: "muertes" },
    { key: "retiradas_en_una_partida", label: "Más retiradas en una partida", suffix: "retiradas" },
];

function formatDuration(seconds) {
    if (typeof seconds !== "number") return "Sin datos";
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return minutes ? `${minutes} min ${remainingSeconds} s` : `${remainingSeconds} s`;
}

function formatRecord(value, suffix) {
    if (!Array.isArray(value) || value.length < 2 || value[0] == null || value[1] == null) {
        return { name: "Sin datos", value: "" };
    }
    return { name: value[0], value: `${value[1]} ${suffix}` };
}

export default function Estadisticas() {
    const navigate = useNavigate();
    const [estadisticas, setEstadisticas] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [estadisticasIndividuales, setEstadisticasIndividuales] = useState(null);
    const [loadingIndividuales, setLoadingIndividuales] = useState(true);
    const [errorIndividuales, setErrorIndividuales] = useState("");

    useEffect(() => {
        let cancelled = false;

        fetch("/api/estadisticas/globales/", { method: "GET", credentials: "include" })
            .then(async (response) => {
                const data = await response.json().catch(() => ({}));
                if (!response.ok) {
                    throw new Error(data?.detail || "No se pudieron cargar las estadísticas");
                }
                return data;
            })
            .then((data) => {
                if (!cancelled) setEstadisticas(data);
            })
            .catch((requestError) => {
                if (!cancelled) setError(requestError instanceof Error ? requestError.message : "Error cargando estadísticas");
            })
            .finally(() => {
                if (!cancelled) setLoading(false);
            });

        return () => {
            cancelled = true;
        };
    }, []);

    useEffect(() => {
        let cancelled = false;

        fetch("/api/estadisticas/individuales/", { method: "GET", credentials: "include" })
            .then(async (response) => {
                const data = await response.json().catch(() => ({}));
                if (!response.ok) {
                    throw new Error(data?.detail || "No se pudieron cargar tus estadísticas");
                }
                return data;
            })
            .then((data) => {
                if (!cancelled) setEstadisticasIndividuales(data);
            })
            .catch((requestError) => {
                if (!cancelled) {
                    setErrorIndividuales(requestError instanceof Error ? requestError.message : "Error cargando tus estadísticas");
                }
            })
            .finally(() => {
                if (!cancelled) setLoadingIndividuales(false);
            });

        return () => {
            cancelled = true;
        };
    }, []);

    return (
        <div className="app estadisticas-page">
            <button className="partidas-volver-button estadisticas-volver-button" onClick={() => navigate("/inicio")}>
                ⮜
            </button>
            <img src={cabecera} alt="Matacartas" style={{ maxWidth: "100%", height: "auto" }} />

            {loading && <p className="estadisticas-message">Cargando estadísticas...</p>}
            {!loading && error && <p className="estadisticas-message estadisticas-message--error">{error}</p>}

            {!loading && !error && estadisticas && (
                <section className="form-card estadisticas-panel" aria-label="Panel de estadísticas globales">
                    <p className="estadisticas-intro">Resumen de la actividad acumulada de todas las partidas.</p>
                    <div className="estadisticas-summary-grid">
                        {metricasPrincipales.map(({ key, label }) => (
                            <article className="estadistica-card" key={key}>
                                <span>{label}</span>
                                <strong>{estadisticas[key] ?? 0}</strong>
                            </article>
                        ))}
                    </div>

                    <div className="estadisticas-columns">
                        <section className="estadisticas-section estadisticas-section--card">
                            <h2>Estado de las partidas</h2>
                            <div className="estadisticas-status-list">
                                {estadoPartidas.map(({ key, label }) => (
                                    <div className="estadisticas-status-row" key={key}>
                                        <span>{label}</span>
                                        <strong>{estadisticas[key] ?? 0}</strong>
                                    </div>
                                ))}
                            </div>
                        </section>

                        <section className="estadisticas-section estadisticas-section--card">
                            <h2>Récords individuales</h2>
                            <div className="estadisticas-record-list">
                                {records.map(({ key, label, suffix }) => {
                                    const record = formatRecord(estadisticas[key], suffix);
                                    return (
                                        <div className="estadisticas-record" key={key}>
                                            <span>{label}</span>
                                            <strong>{record.name}</strong>
                                            <small>{record.value}</small>
                                        </div>
                                    );
                                })}
                            </div>
                        </section>
                    </div>

                    <section className="estadisticas-section estadisticas-section--card estadisticas-section--duration">
                        <h2>Duración de las partidas</h2>
                        <div className="estadisticas-duration-grid">
                            <div>
                                <span>Partida más larga</span>
                                <strong>{estadisticas.partida_mas_larga?.[0] || "Sin datos"}</strong>
                                <small>{formatDuration(estadisticas.partida_mas_larga?.[1])}</small>
                            </div>
                            <div>
                                <span>Partida más corta</span>
                                <strong>{estadisticas.partidas_mas_corta?.[0] || "Sin datos"}</strong>
                                <small>{formatDuration(estadisticas.partidas_mas_corta?.[1])}</small>
                            </div>
                        </div>
                    </section>
                </section>
            )}

            {loadingIndividuales && <p className="estadisticas-message">Cargando tus estadísticas...</p>}
            {!loadingIndividuales && errorIndividuales && (
                <p className="estadisticas-message estadisticas-message--error">{errorIndividuales}</p>
            )}

            {!loadingIndividuales && !errorIndividuales && estadisticasIndividuales && (
                <section className="form-card estadisticas-panel estadisticas-panel--individuales" aria-label="Panel de estadísticas individuales">
                    <p className="estadisticas-intro">Tu actividad y tus mejores resultados en partidas finalizadas.</p>

                    <div className="estadisticas-summary-grid estadisticas-summary-grid--individuales">
                        {metricasIndividuales.map(({ key, label, suffix }) => (
                            <article className="estadistica-card" key={key}>
                                <span>{label}</span>
                                <strong>{estadisticasIndividuales[key] ?? 0}</strong>
                                <small>{suffix}</small>
                            </article>
                        ))}
                    </div>

                    <section className="estadisticas-section estadisticas-section--card estadisticas-individuales-records">
                        <h2>Tus récords en una partida</h2>
                        <div className="estadisticas-record-list">
                            {recordsIndividuales.map(({ key, label, suffix }) => (
                                <div className="estadisticas-record" key={key}>
                                    <span>{label}</span>
                                    <strong>{estadisticasIndividuales[key] ?? 0}</strong>
                                    <small>{suffix}</small>
                                </div>
                            ))}
                        </div>
                    </section>
                </section>
            )}
        </div>
    );
}