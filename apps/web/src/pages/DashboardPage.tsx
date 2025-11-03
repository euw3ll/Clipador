import { useEffect, useMemo, useState } from "react";

import { fetchRecentBursts, resolveMonitoring, type BurstPayload, type MonitoringResolution } from "../api";
import { useAuth } from "../context/AuthContext";

export function DashboardPage() {
  const { token } = useAuth();
  const [bursts, setBursts] = useState<BurstPayload[]>([]);
  const [monitoring, setMonitoring] = useState<MonitoringResolution | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "error" | "success">("idle");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      return;
    }

    let active = true;

    async function load() {
      setStatus("loading");
      setError(null);
      try {
        const [burstsData, monitoringData] = await Promise.all([
          fetchRecentBursts(token),
          resolveMonitoring(token),
        ]);
        if (!active) return;
        setBursts(burstsData);
        setMonitoring(monitoringData);
        setStatus("success");
      } catch (err) {
        if (!active) return;
        setError(err instanceof Error ? err.message : "Erro ao carregar dados");
        setStatus("error");
      }
    }

    load();
    const timer = window.setInterval(load, 60_000);

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [token]);

  const headline = useMemo(() => {
    if (status === "loading") return "Carregando bursts...";
    if (status === "error") return "Ocorreu um erro";
    if (bursts.length === 0) return "Nenhum burst recente";
    return `Bursts recentes (${bursts.length})`;
  }, [status, bursts.length]);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Dashboard</h1>
        <p>{headline}</p>
        {monitoring && (
          <div className="monitoring-card">
            <span>Preset atual</span>
            <strong>{monitoring.intervalo_segundos}s</strong>
            <span>Mínimo {monitoring.min_clipes} clipes</span>
          </div>
        )}
        {error && <p className="error">{error}</p>}
      </header>
      <section className="burst-list">
        {bursts.map((burst) => (
          <article key={`${burst.inicio_iso}-${burst.fim}`} className="burst-card">
            <h2>{new Date(burst.inicio_iso).toLocaleString()}</h2>
            <p>{burst.clipes.length} clipes agrupados</p>
            <ul>
              {burst.clipes.map((clip) => (
                <li key={clip.id}>
                  <div>
                    <span className="clip-id">Clip {clip.id.toUpperCase()}</span>
                    <span className="clip-time">{new Date(clip.created_at).toLocaleTimeString()}</span>
                  </div>
                  <div>
                    <span>{clip.viewer_count} viewers</span>
                    {clip.streamer_name && <span>{clip.streamer_name}</span>}
                  </div>
                </li>
              ))}
            </ul>
          </article>
        ))}
      </section>
    </div>
  );
}
