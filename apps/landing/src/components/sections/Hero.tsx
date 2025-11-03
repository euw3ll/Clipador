import { Button } from "@/components/ui/button";
import { Play, ArrowRight } from "lucide-react";
import { useEffect, useState } from "react";
import heroImage from "@/assets/hero-bg.jpg";

const Hero = () => {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <section className="relative min-h-screen flex items-center justify-center bg-gradient-bg overflow-hidden">
      {/* Parallax Background Image */}
      <div
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage: `url(${heroImage})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          transform: `translateY(${scrollY * 0.5}px)`,
        }}
      />

      {/* Background Elements */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-primary/20 rounded-full blur-3xl animate-float"></div>
        <div
          className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl animate-float"
          style={{ animationDelay: "2s" }}
        ></div>
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <div className="text-center max-w-4xl mx-auto animate-slide-up pt-24 sm:pt-28 md:pt-32">
          {/* Main Heading */}
          <h1 className="text-4xl sm:text-5xl md:text-7xl font-bold mb-6 animate-slide-up">
            <span className="bg-gradient-to-r from-foreground via-primary to-foreground bg-clip-text text-transparent animate-gradient block py-1">
              {" "}
              {/* <-- MUDE AQUI */}
              Cortes Inteligentes
            </span>
            <span className="bg-gradient-to-r from-primary via-foreground to-primary bg-clip-text text-transparent block py-1">
              {" "}
              {/* <-- E AQUI */}
              que Viralizam
            </span>
          </h1>
          {/* Subheading */}
          <p
            className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed animate-fade-in"
            style={{ animationDelay: "0.3s" }}
          >
            O Clipador monitora as lives para você e entrega os melhores momentos prontos para publicar.
            <span className="block mt-2 text-lg md:text-xl">
              💰 Seu tempo vale ouro, não clipes ruins.
            </span>
          </p>
          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <Button
              variant="hero"
              size="lg"
              className="text-lg px-8 py-6 h-auto group dopamine-shine pulse-shadow"
              onClick={() => window.open("https://t.me/ClipadorBot", "_blank")}
            >
              Começar no Telegram
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>

            <Button
              variant="glass"
              size="lg"
              className="text-lg px-8 py-6 h-auto group dopamine-shine"
              onClick={() => window.open("https://t.me/clipadorfree", "_blank")}
            >
              <Play className="w-5 h-5 group-hover:scale-110 transition-transform" />
              Ver Demo
            </Button>
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce z-20">
        {" "}
        {/* <-- MUDANÇA AQUI: Removido 'w-full', 'flex' e 'justify-center' */}
        <div className="w-6 h-10 border-2 border-border rounded-full flex justify-center">
          <div className="w-1 h-3 bg-primary rounded-full mt-2 animate-pulse"></div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
