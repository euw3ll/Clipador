import { FormEvent, useEffect, useState } from "react";

import {
  attachChannelStreamer,
  detachChannelStreamer,
  fetchChannelConfig,
  fetchDeliveryHistory,
  type ChannelConfig,
  type ChannelStreamer,
  type DeliveryRecord,
} from "../api";
import { useAuth } from "../context/AuthContext";

export function StreamsPage() {
  const { token } = useAuth();
  const [config, setConfig] = useState<ChannelConfig | null>(null);
  const [history, setHistory] = useState<DeliveryRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    twitch_user_id: "",
    display_name: "",
    avatar_url: "",
    monitor_interval_seconds: 180,
    monitor_min_clips: 2,
  });

  useEffect(() => {
    if (!token) return;

    async function load() {
      try {
        setLoading(true);
        setError(null);
        const [cfg, deliveries] = await Promise.all([
          fetchChannelConfig(token),
          fetchDeliveryHistory(token, 25),
        ]);
        setConfig(cfg);
        setHistory(deliveries.items);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erro ao carregar dados");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [token]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) return;

    try {
      setLoading(true);
      setError(null);
      const updated = await attachChannelStreamer(token, {
        twitch_user_id: form.twitch_user_id,
        display_name: form.display_name,
        avatar_url: form.avatar_url || undefined,
        monitor_interval_seconds: form.monitor_interval_seconds,
        monitor_min_clips: form.monitor_min_clips,
      });
      setConfig(updated);
      setForm({
        twitch_user_id: "",
        display_name: "",
        avatar_url: "",
        monitor_interval_seconds: 180,
        monitor_min_clips: 2,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao adicionar streamer");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="streams-page">
      <header>
        <h1>Streams Monitoradas</h1>
        {error && <p className="error">{error}</p>}
        {config && (
          <div className="plan-summary">
            <span>
              Slots: {config.slots_used}/{config.slots_total} (base {config.slots_base})
            </span>
            <span>Modo: {config.monitor_mode}</span>
          </div>
        )}
      </header>
      <section className="stream-form-wrapper">
        <form className="stream-form" onSubmit={handleSubmit}>
          <div className="form-grid">
            <label>
              Twitch User ID
              <input
                value={form.twitch_user_id}
                onChange={(e) => setForm((prev) => ({ ...prev, twitch_user_id: e.target.value }))}
                required
              />
            </label>
            <label>
              Nome exibido
              <input
                value={form.display_name}
                onChange={(e) => setForm((prev) => ({ ...prev, display_name: e.target.value }))}
                required
              />
            </label>
            <label>
              Avatar URL
              <input
                value={form.avatar_url}
                onChange={(e) => setForm((prev) => ({ ...prev, avatar_url: e.target.value }))}
              />
            </label>
            <label>
              Intervalo (segundos)
              <input
                type="number"
                min={30}
                value={form.monitor_interval_seconds}
                onChange={(e) =>
                  setForm((prev) => ({ ...prev, monitor_interval_seconds: Number(e.target.value) }))
                }
              />
            </label>
            <label>
              Mínimo de clipes
              <input
                type="number"
                min={1}
                value={form.monitor_min_clips}
                onChange={(e) =>
                  setForm((prev) => ({ ...prev, monitor_min_clips: Number(e.target.value) }))
                }
              />
            </label>
          </div>
          <button type="submit" disabled={loading}>
            {loading ? "Salvando..." : "Adicionar streamer"}
          </button>
        </form>
      </section>
      <section className="stream-list">
        {config?.streamers.map((stream: ChannelStreamer) => (
          <article key={stream.id} className="stream-card">
            <div>
              <h2>{stream.display_name}</h2>
              <p>ID Twitch: {stream.twitch_user_id}</p>
              {stream.label && <p>Etiqueta: {stream.label}</p>}
              {stream.status?.status && <p>Status: {stream.status.status}</p>}
            </div>
            <div className="stream-meta">
              <span>Intervalo: {stream.monitor_interval_seconds}s</span>
              <span>Mínimo: {stream.monitor_min_clips}</span>
              <button
                type="button"
                onClick={async () => {
                  if (!token) return;
                  try {
                    const updated = await detachChannelStreamer(token, stream.streamer_id);
                    setConfig(updated);
                  } catch (err) {
                    setError(err instanceof Error ? err.message : "Erro ao remover streamer");
                  }
                }}
              >
                Remover
              </button>
            </div>
          </article>
        ))}
        {config?.streamers.length === 0 && !loading && <p>Nenhum streamer cadastrado ainda.</p>}
      </section>
      <section className="history-list">
        <h2>Histórico recente</h2>
        {history.length === 0 && <p>Sem entregas registradas.</p>}
        {history.map((item) => (
          <article key={`${item.streamer_twitch_id}-${item.delivered_at}-${item.clip_external_id || ""}`}>
            <div className="history-entry">
              <strong>{item.streamer_display_name}</strong>
              <span>{new Date(item.delivered_at).toLocaleString()}</span>
            </div>
            <p>Clip: {item.clip_external_id ?? "N/A"}</p>
            {item.clip_title && <p>Título: {item.clip_title}</p>}
            {typeof item.viewer_count === "number" && <p>Views: {item.viewer_count}</p>}
          </article>
        ))}
      </section>
    </div>
  );
}
