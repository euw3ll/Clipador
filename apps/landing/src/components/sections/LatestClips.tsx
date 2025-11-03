import { useEffect, useState } from "react";

interface PublicClip {
  id: string;
  created_at: string;
  viewer_count: number;
  title?: string | null;
  duration?: number | null;
  streamer_name?: string | null;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export default function LatestClips() {
  const [clips, setClips] = useState<PublicClip[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const response = await fetch(`${API_BASE_URL}/public/clips?limit=9`);
        if (!response.ok) {
          throw new Error(`Erro ${response.status}`);
        }
        const body = await response.json();
        setClips(Array.isArray(body.data) ? body.data : []);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Não foi possível carregar os clipes");
      }
    }

    load();
  }, []);

  return (
    <section className="relative py-20" id="free-clips">
      <div className="container max-w-6xl px-6 mx-auto">
        <div className="mb-10 text-center">
          <span className="inline-flex items-center rounded-full bg-primary/10 px-4 py-1 text-sm font-medium text-primary">
            Canal Gratuito
          </span>
          <h2 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">
            Highlights capturados automaticamente
          </h2>
          <p className="mt-3 max-w-2xl mx-auto text-muted-foreground">
            Veja os clipes que estão sendo detectados agora mesmo. Esse feed reflete o que seus leads enxergam no canal gratuito do Clipador.
          </p>
          {error && <p className="mt-3 text-sm text-destructive">{error}</p>}
        </div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {clips.map((clip) => (
            <article
              key={clip.id}
              className="rounded-2xl border border-border/60 bg-card/70 p-6 backdrop-blur transition hover:border-primary/60 hover:shadow-lg"
            >
              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <span className="font-medium text-foreground">{clip.streamer_name ?? "Streamer"}</span>
                <span>{new Date(clip.created_at).toLocaleDateString()}</span>
              </div>
              <h3 className="mt-4 text-lg font-semibold text-foreground">
                {clip.title ?? `Clip ${clip.id}`}
              </h3>
              <p className="mt-3 text-sm text-muted-foreground">
                {clip.viewer_count} viewers • {clip.duration ? Math.round(clip.duration) : "?"}s
              </p>
            </article>
          ))}
          {clips.length === 0 && !error && (
            <p className="col-span-full text-center text-muted-foreground">
              Estamos capturando os primeiros clipes do dia...
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
