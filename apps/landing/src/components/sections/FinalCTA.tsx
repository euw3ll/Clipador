import { Button } from "@/components/ui/button";
import { ArrowRight, Zap } from "lucide-react";

const FinalCTA = () => {
  return (
    <section className="py-20 bg-gradient-bg relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-primary/30 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }}></div>
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-primary/20 backdrop-blur-sm border border-primary/30 rounded-full px-4 py-2 mb-6 text-sm text-primary">
            <Zap className="w-4 h-4" />
            Comece hoje mesmo
          </div>

          <h2 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-foreground via-foreground to-primary bg-clip-text text-transparent leading-tight">
            Pare de Perder <br />
            <span className="text-primary">Tempo Assistindo Lives</span>
          </h2>
          
          <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
            Junte-se aos editores que já economizam <span className="text-primary font-semibold">90% do tempo</span> e 
            aumentaram sua produtividade com o Clipador.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
            <Button 
              variant="hero" 
              size="lg" 
              className="text-lg px-10 py-6 h-auto group"
              onClick={() => window.open('https://t.me/ClipadorBot', '_blank')}
            >
              Começar Agora no Telegram
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
          </div>

          <div className="text-sm text-muted-foreground">
            ✅ Grátis para começar • ✅ Setup em 2 minutos • ✅ Sem necessidade de cartão
          </div>
        </div>
      </div>
    </section>
  );
};

export default FinalCTA;
