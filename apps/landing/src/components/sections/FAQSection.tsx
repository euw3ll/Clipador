import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { HelpCircle } from "lucide-react";

const FAQSection = () => {
  const faqs = [
    {
      question: "Como funciona o monitoramento automático?",
      answer:
        "O Clipador monitora seus streamers favoritos continuamente através de múltiplos sinais: picos de audiência, análise do chat em tempo real, identificação de momentos engraçados/épicos e reações. Você pode configurar a sensibilidade e os tipos de conteúdo que deseja receber pelo bot.",
    },
    {
      question: "Quantos streamers posso monitorar?",
      answer:
        "Depende do seu plano: Mensal Solo (até 3 streamers), Mensal Plus (até 8 streamers), Anual Pro (até 15 streamers). Cada plano permite monitoramento completo dos streamers selecionados.",
    },
    {
      question: "Como funciona a troca de streamers?",
      answer:
        "A troca de streamers é feita durante a renovação do seu plano, independentemente de qual plano você tenha. Você pode gerenciar sua lista de streamers através do bot no Telegram.",
    },
    {
      question: "Os clipes são gerados automaticamente?",
      answer:
        "Sim, os clipes são gerados automaticamente pelo sistema e enviados diretamente para o seu chat do Telegram. A mensagem inclui o clipe completo e um botão para download imediato.",
    },
    {
      question: "Posso usar os clipes comercialmente?",
      answer:
        "Os clipes são extraídos de conteúdo público das lives. Recomendamos sempre verificar as políticas de cada streamer e plataforma onde você pretende publicar.",
    },
    {
      question: "Como recebo os clipes?",
      answer:
        "Todos os alertas e informações são enviados diretamente para o seu Telegram através do nosso bot. Você receberá uma notificação assim que um novo momento viral for detectado, junto com o timestamp e contexto.",
    },
    {
      question: "Qual o formato dos alertas?",
      answer:
        "Você recebe notificações no Telegram com: timestamp exato do momento, contexto do que aconteceu, link direto para a live, e screenshot do momento para visualização rápida.",
    },
    {
      question: "Posso cancelar a qualquer momento?",
      answer:
        "Sim, você pode cancelar seu plano a qualquer momento através do nosso bot no Telegram. Não há fidelidade, oferecemos reembolso em até 7 dias úteis, e você tem 3 dias de teste gratuito para experimentar o serviço.",
    },
  ];

  return (
    <section className="py-20 bg-card/20 relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 opacity-10">
        <div
          className="absolute top-1/3 right-1/4 w-80 h-80 bg-primary/15 rounded-full blur-3xl animate-pulse"
          style={{ animationDelay: "2s" }}
        ></div>
        <div className="absolute bottom-1/3 left-1/4 w-60 h-60 bg-primary/10 rounded-full blur-3xl animate-pulse"></div>
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <div className="text-center mb-16 animate-fade-in">
          <div className="inline-flex items-center gap-2 bg-card/50 backdrop-blur-sm border border-border/50 rounded-full px-4 py-2 mb-6 text-sm text-muted-foreground">
            <HelpCircle className="w-4 h-4 text-primary" />
            Perguntas Frequentes
          </div>

          <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-foreground to-primary bg-clip-text text-transparent">
            Dúvidas Frequentes
          </h2>

          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Tire suas principais dúvidas sobre o Clipador e como ele pode
            revolucionar sua criação de conteúdo
          </p>
        </div>

        <div
          className="max-w-4xl mx-auto animate-fade-in"
          style={{ animationDelay: "0.2s" }}
        >
          <Accordion type="single" collapsible className="space-y-4">
            {faqs.map((faq, index) => (
              <AccordionItem
                key={index}
                value={`item-${index}`}
                className="bg-card/50 backdrop-blur-sm border border-border/50 rounded-lg px-6 hover:border-primary/30 transition-colors duration-300"
              >
                <AccordionTrigger className="text-left text-lg font-semibold hover:text-primary transition-colors duration-300 py-6">
                  {faq.question}
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground pb-6 leading-relaxed">
                  {faq.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>

        {/* CTA Section */}
        <div
          className="text-center mt-16 animate-fade-in"
          style={{ animationDelay: "0.4s" }}
        >
          <p className="text-muted-foreground mb-4">
            Ainda tem dúvidas? Fale conosco diretamente!
          </p>
          <div
            className="inline-flex items-center gap-2 text-primary font-semibold cursor-pointer hover:underline"
            onClick={() => window.open("https://t.me/ClipadorBot", "_blank")}
          >
            <HelpCircle className="w-4 h-4" />
            Conversar no Telegram
          </div>
        </div>
      </div>
    </section>
  );
};

export default FAQSection;
