type Step = {
  title: string;
  description: string;
  mediaLabel: string;
  mediaSrc: string;
  mediaType?: "video" | "image";
};

const steps: Step[] = [
  {
    title: "1. Configure os streamers",
    description:
      "Selecione os canais que quer monitorar e deixe o Clipador de plantão para avisar assim que algo viral surgir.",
    mediaLabel: "Tela mostrando a escolha dos streamers",
    mediaSrc: "/videos/passo1.mp4",
    mediaType: "video",
  },
  {
    title: "2. Ajuste a sensibilidade",
    description:
      "Defina os gatilhos de hype, chat e duração para receber apenas os momentos que fazem sentido para o seu corte.",
    mediaLabel: "Tela configurando filtros e alertas",
    mediaSrc: "/videos/passo2.mp4",
    mediaType: "video",
  },
  {
    title: "3. Receba os clipes na hora",
    description:
      "O que acontece na live chega no seu Telegram com título, timestamp e link. É só baixar e postar.",
    mediaLabel: "Notificação do Clipador entregando o clipe",
    mediaSrc: "/videos/passo3.mp4",
    mediaType: "video",
  },
];

const VideoSection = () => {
  return (
    <section className="py-20 bg-background relative">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Como o Sistema <span className="text-primary">Funciona</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Três passos para eliminar a caçada manual por clipes e deixar o Clipador entregar os highlights certos para você.
          </p>
        </div>

        <div className="grid gap-8 lg:grid-cols-3">
          {steps.map((step, index) => (
            <article
              key={step.title}
              className="group h-full rounded-2xl border border-border/50 bg-card/50 p-8 shadow-card backdrop-blur-sm transition-all duration-300 hover:-translate-y-1 hover:border-primary/50 dopamine-pop"
            >
              <span className="text-sm font-semibold uppercase tracking-wide text-primary/80">
                Passo {index + 1}
              </span>
              <h3 className="mt-2 text-2xl font-semibold text-foreground">
                {step.title}
              </h3>
              <p className="mt-4 text-base leading-relaxed text-muted-foreground">
                {step.description}
              </p>

              <div className="mt-8 relative aspect-video w-full overflow-hidden rounded-xl border border-border/60 bg-gradient-to-br from-primary/15 via-background to-background/70">
                {step.mediaType !== "image" ? (
                  <video
                    className="absolute inset-0 h-full w-full object-cover"
                    src={step.mediaSrc}
                    autoPlay
                    muted
                    loop
                    playsInline
                    aria-label={step.mediaLabel}
                  />
                ) : (
                  <img
                    className="absolute inset-0 h-full w-full object-cover"
                    src={step.mediaSrc}
                    alt={step.mediaLabel}
                    loading="lazy"
                  />
                )}
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
};

export default VideoSection;
