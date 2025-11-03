import { Star, Quote } from "lucide-react";

const SocialProof = () => {
  const testimonials = [
    {
      name: "Carlos Eduardo",
      role: "Editor de Clipes",
      company: "@carlosedits",
      // Corrigido: URL para avatar masculino
      avatar: "https://i.pravatar.cc/150?u=beatriz",
      rating: 5,
      testimonial:
        "Parei de perder horas dando replay no VOD da live pra achar 3 clipes bons. Agora o Clipador me entrega os melhores momentos automaticamente. Minha produtividade aumentou 500%.",
    },
    {
      name: "Beatriz Costa",
      role: "Social Media",
      company: "Agência StreamWorks",
      // Corrigido: URL para avatar feminino
      avatar: "https://i.pravatar.cc/150?u=beatriz-fem",
      rating: 5,
      testimonial:
        "Gerencio 15 streamers e o Clipador é essencial. Recebo os clipes virais no Telegram na hora que acontecem. Meus clientes adoram a rapidez para postar no TikTok e Reels.",
    },
    {
      name: "Thiago Almeida",
      role: "Criador de Conteúdo",
      company: "@thiagomemes",
      avatar: "https://i.pravatar.cc/150?u=thiago",
      rating: 5,
      testimonial:
        "Os clipes que o Clipador entrega são sempre os que mais viralizam. É como ter um assistente 24h procurando os melhores momentos das VODs para mim.",
    },
    {
      name: "Luna Streamer",
      role: "Streamer Twitch",
      company: "@lunastream",
      avatar: "https://i.pravatar.cc/150?u=luna",
      rating: 5,
      testimonial:
        "Uso o Clipador para monitorar minha própria live e de outros streamers. Me ajuda a ver quais momentos engajam mais e a melhorar meu conteúdo, sem precisar rever tudo depois.",
    },
    {
      name: "Felipe Ramos",
      role: "Editor Freelancer",
      company: "Freelancer",
      avatar: "https://i.pravatar.cc/150?u=felipe",
      rating: 5,
      testimonial:
        "Consegui triplicar minha clientela depois que comecei a usar o Clipador. Entrego os clipes muito mais rápido e com a qualidade dos momentos que realmente importam.",
    },
    {
      name: "Gabriela Santos",
      role: "Agência de Marketing",
      company: "StreamBoost",
      avatar: "https://i.pravatar.cc/150?u=gabriela",
      rating: 5,
      testimonial:
        "O ROI dos nossos clientes aumentou 300% desde que implementamos o Clipador no nosso fluxo. É impossível trabalhar sem ele agora.",
    },
  ];

  return (
    <section className="py-20 bg-background relative">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            O que nossos <span className="text-primary">usuários dizem</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Mais de 2.500 editores e criadores já transformaram seu fluxo de
            trabalho. Veja depoimentos reais de quem usa o sistema.
          </p>
        </div>

        {/* Featured Testimonial */}
        <div className="max-w-4xl mx-auto mb-16">
          <div className="bg-gradient-card rounded-2xl p-8 md:p-12 text-center border border-border/50 shadow-card">
            <Quote className="w-12 h-12 text-primary mx-auto mb-6 opacity-60" />
            <blockquote className="text-2xl md:text-3xl font-medium text-foreground mb-8 leading-relaxed">
              "Desde que uso o Clipador, não preciso mais ficar voltando o VOD
              da live pra achar 2 clipes bons. O sistema entrega exatamente os
              momentos que viralizam. Minha receita triplicou em 3 meses."
            </blockquote>
            <div className="flex items-center justify-center gap-4">
              <img
                src="https://i.pravatar.cc/150?u=marcos"
                alt="Marcos Silva"
                className="w-16 h-16 rounded-full"
              />
              <div className="text-left">
                <div className="font-semibold text-foreground">
                  Marcos Silva
                </div>
                <div className="text-muted-foreground">
                  Editor, ClipMaster Pro
                </div>
                <div className="flex text-primary mt-1">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-current" />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Testimonials Grid - Only first 2 */}
        <div className="grid md:grid-cols-2 gap-6">
          {testimonials.slice(0, 2).map((testimonial, index) => (
            <div
              key={index}
              className="bg-card/50 rounded-xl p-6 border border-border/50 backdrop-blur-sm hover:bg-card/70 transition-all duration-300 group"
            >
              <div className="flex items-center gap-3 mb-4">
                <img
                  src={testimonial.avatar}
                  alt={testimonial.name}
                  className="w-12 h-12 rounded-full"
                />
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-foreground truncate">
                    {testimonial.name}
                  </div>
                  <div className="text-sm text-muted-foreground truncate">
                    {testimonial.role}
                  </div>
                  <div className="text-xs text-primary truncate">
                    {testimonial.company}
                  </div>
                </div>
                <div className="flex text-primary">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-3 h-3 fill-current" />
                  ))}
                </div>
              </div>

              <blockquote className="text-muted-foreground text-sm leading-relaxed">
                "{testimonial.testimonial}"
              </blockquote>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default SocialProof;
