import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import { BrowserRouter, Routes, Route, Navigate, useLocation, useParams } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Inicio from "./pages/Inicio.jsx";
import Perfil from "./pages/Perfil.jsx";
import Admin from "./pages/admin/Admin.jsx";
import AdminUsers from "./pages/admin/AdminUsers.jsx";
import AdminUserForm from "./pages/admin/AdminUserForm.jsx";
import AdminRangos from "./pages/admin/AdminRangos.jsx";
import AdminRangoForm from "./pages/admin/AdminRangoForm.jsx";
import AdminTorneos from "./pages/admin/AdminTorneos.jsx";
import AdminRecompensas from "./pages/admin/AdminRecompensas.jsx";
import AdminMedallas from "./pages/admin/AdminMedallas.jsx";
import AdminMedallaForm from "./pages/admin/AdminMedallaForm.jsx";
import AdminLogros from "./pages/admin/AdminLogros.jsx";
import AdminLogroForm from "./pages/admin/AdminLogrosForm.jsx";
import ListaPartidas from "./pages/partidas/ListaPartidas.jsx";
import CrearPartida from "./pages/partidas/CrearPartida.jsx";
import SalaEsperaPartida from "./pages/partidas/SalaEsperaPartida.jsx";
import ListaTorneos from "./pages/torneos/ListaTorneos.jsx";
import CrearTorneo from "./pages/torneos/CrearTorneo.jsx";
import Torneo from "./pages/torneos/Torneo.jsx";
import RecuperarPassword from "./pages/RecuperarPassword.jsx";
import RestablecerPassword from "./pages/RestablecerPassword.jsx";
import VerificarEmail from "./pages/VerificarEmail.jsx";
import Juego from "./pages/juego/Juego.jsx";
import Estadisticas from "./pages/estadisticas_recompensas/Estadisticas.jsx";
import Recompensas from "./pages/estadisticas_recompensas/Recompensas.jsx";
import "./index.css";
import "./styles/main.css";

function RequireAuth({ children }) {
  const location = useLocation();
  const [status, setStatus] = React.useState("checking"); // checking | authed | unauthed

  React.useEffect(() => {
    let cancelled = false;

    fetch("/api/auth/me/", { method: "GET", credentials: "include" })
      .then((res) => {
        if (cancelled) return;
        setStatus(res.ok ? "authed" : "unauthed");
      })
      .catch(() => {
        if (cancelled) return;
        setStatus("unauthed");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (status === "checking") return null;
  if (status === "unauthed") {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return children;
}

function RequireAdmin({ children }) {
  const location = useLocation();
  const [status, setStatus] = React.useState("checking"); // checking | staff | no-staff

  React.useEffect(() => {
    let cancelled = false;

    fetch("/api/auth/me/", { method: "GET", credentials: "include" })
      .then(async (res) => {
        if (cancelled) return;
        if (!res.ok) {
          setStatus("no-staff");
          return;
        }
        const data = await res.json().catch(() => ({}));
        setStatus(Boolean(data?.is_staff) ? "staff" : "no-staff");
      })
      .catch(() => {
        if (cancelled) return;
        setStatus("no-staff");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (status === "checking") return null;
  if (status === "no-staff") {
    return <Navigate to="/inicio" replace state={{ from: location }} />;
  }

  return children;
}

function RedirectIfAuthed({ children }) {
  const [status, setStatus] = React.useState("checking"); // checking | authed | unauthed

  React.useEffect(() => {
    let cancelled = false;

    fetch("/api/auth/me/", { method: "GET", credentials: "include" })
      .then((res) => {
        if (cancelled) return;
        setStatus(res.ok ? "authed" : "unauthed");
      })
      .catch(() => {
        if (cancelled) return;
        setStatus("unauthed");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (status === "checking") return null;
  if (status === "authed") {
    return <Navigate to="/inicio" replace />;
  }

  return children;
}

async function obtenerEstadoPartida(partidaId, comprobarTorneo = false) {
  const participaRes = await fetch(`/api/partidas/${partidaId}/participa/`, {
    method: "GET",
    credentials: "include",
  });

  if (!participaRes.ok) return null;

  const participaData = await participaRes.json().catch(() => ({}));
  if (!participaData?.participa) {
    return { participa: false, haEmpezado: false, perteneceATorneo: false };
  }

  const comprobaciones = [
    fetch(`/api/partidas/${partidaId}/ha-empezado/`, {
      method: "GET",
      credentials: "include",
    }),
  ];

  if (comprobarTorneo) {
    comprobaciones.push(
      fetch(`/api/partidas/${partidaId}/pertenece-torneo/`, {
        method: "GET",
        credentials: "include",
      })
    );
  }

  const respuestas = await Promise.all(comprobaciones);
  if (respuestas.some((res) => !res.ok)) return null;

  const inicioData = await respuestas[0].json().catch(() => ({}));
  const torneoData = comprobarTorneo
    ? await respuestas[1].json().catch(() => ({}))
    : {};

  return {
    participa: true,
    haEmpezado: Boolean(inicioData?.ha_empezado),
    perteneceATorneo: Boolean(torneoData?.pertenece_a_torneo),
  };
}

function RequireParticipatingNotStartNotTorneo({ children }) {
  const location = useLocation();
  const { partidaId } = useParams();
  const [status, setStatus] = React.useState("checking");

  React.useEffect(() => {
    let cancelled = false;

    if (!partidaId) {
      setStatus("denied");
      return () => {
        cancelled = true;
      };
    }

    obtenerEstadoPartida(partidaId, true)
      .then((estado) => {
        if (cancelled) return;

        const puedeEntrar = estado?.participa
          && !estado.haEmpezado
          && !estado.perteneceATorneo;
        setStatus(puedeEntrar ? "allowed" : "denied");
      })
      .catch(() => {
        if (!cancelled) setStatus("denied");
      });

    return () => {
      cancelled = true;
    };
  }, [partidaId]);

  if (status === "checking") return null;
  if (status === "denied") {
    return <Navigate to="/partidas" replace state={{ from: location }} />;
  }

  return children;
}

function RequireParticipatingStarted({ children }) {
  const location = useLocation();
  const { partidaId } = useParams();
  const [status, setStatus] = React.useState("checking");

  React.useEffect(() => {
    let cancelled = false;

    if (!partidaId) {
      setStatus("denied");
      return () => {
        cancelled = true;
      };
    }

    obtenerEstadoPartida(partidaId)
      .then((estado) => {
        if (cancelled) return;

        const puedeEntrar = estado?.participa && estado.haEmpezado;
        setStatus(puedeEntrar ? "allowed" : "denied");
      })
      .catch(() => {
        if (!cancelled) setStatus("denied");
      });

    return () => {
      cancelled = true;
    };
  }, [partidaId]);

  if (status === "checking") return null;
  if (status === "denied") {
    return <Navigate to="/partidas" replace state={{ from: location }} />;
  }

  return children;
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={ <RedirectIfAuthed> <App /> </RedirectIfAuthed>} />
        <Route path="/login" element={ <RedirectIfAuthed> <Login /> </RedirectIfAuthed>} />
        <Route path="/recuperar-password" element={ <RecuperarPassword /> } />
        <Route path="/restablecer-password/:uid/:token" element={ <RestablecerPassword /> } />
        <Route path="/verificar-email/:uid/:token" element={ <VerificarEmail /> } />

        {/* Necesario iniciar sesión */}
        <Route path="/inicio" element={ <RequireAuth> <Inicio /> </RequireAuth>}/>
        <Route path="/perfil" element={ <RequireAuth> <Perfil /> </RequireAuth>}/>
        <Route path="/partidas" element={ <RequireAuth> <ListaPartidas /> </RequireAuth>}/>
        <Route path="/crear-partida" element={ <RequireAuth> <CrearPartida /> </RequireAuth>}/>
        <Route path="/torneos" element={ <RequireAuth> <ListaTorneos /> </RequireAuth>}/>
        <Route path="/crear-torneo" element={ <RequireAuth> <CrearTorneo /> </RequireAuth>}/>
        <Route path="/torneos/:torneoId" element={ <RequireAuth> <Torneo /> </RequireAuth>}/>
        <Route path="/estadisticas" element={ <RequireAuth> <Estadisticas /> </RequireAuth>}/>
        <Route path="/recompensas" element={ <RequireAuth> <Recompensas /> </RequireAuth>}/>

        {/* Necesario iniciar sesión y participar en la partida */}
        <Route path="/partidas/sala-de-espera/:partidaId" element={ <RequireParticipatingNotStartNotTorneo> <SalaEsperaPartida /> </RequireParticipatingNotStartNotTorneo>}/>
        <Route path="/partidas/mesa/:partidaId" element={ <RequireParticipatingStarted> <Juego /> </RequireParticipatingStarted>}/>

        {/* Necesario ser administrador */}
        <Route path="/admin" element={ <RequireAdmin> <Admin /> </RequireAdmin>}/>
        <Route path="/admin/usuarios" element={ <RequireAdmin> <AdminUsers /> </RequireAdmin>}/>
        <Route path="/admin/usuarios/crear" element={ <RequireAdmin> <AdminUserForm /> </RequireAdmin>}/>
        <Route path="/admin/usuarios/:userId" element={ <RequireAdmin> <AdminUserForm /> </RequireAdmin>}/>
        <Route path="/admin/rangos" element={ <RequireAdmin> <AdminRangos /> </RequireAdmin>}/>
        <Route path="/admin/rangos/crear" element={ <RequireAdmin> <AdminRangoForm /> </RequireAdmin>}/>
        <Route path="/admin/rangos/:rangoId" element={ <RequireAdmin> <AdminRangoForm /> </RequireAdmin>}/>
        <Route path="/admin/torneos" element={ <RequireAdmin> <AdminTorneos /> </RequireAdmin>}/>
        <Route path="/admin/recompensas" element={ <RequireAdmin> <AdminRecompensas /> </RequireAdmin>}/>
        <Route path="/admin/recompensas/medallas" element={ <RequireAdmin> <AdminMedallas /> </RequireAdmin>}/>
        <Route path="/admin/recompensas/medallas/crear" element={ <RequireAdmin> <AdminMedallaForm /> </RequireAdmin>}/>
        <Route path="/admin/recompensas/medallas/:medallaId" element={ <RequireAdmin> <AdminMedallaForm /> </RequireAdmin>}/>
        <Route path="/admin/recompensas/logros" element={ <RequireAdmin> <AdminLogros /> </RequireAdmin>}/>
        <Route path="/admin/recompensas/logros/crear" element={ <RequireAdmin> <AdminLogroForm /> </RequireAdmin>}/>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
