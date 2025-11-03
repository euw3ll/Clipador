import { TrendingUp, Users, Clock, Star } from "lucide-react";
import { useCountAnimation } from "@/hooks/useCountAnimation";

const Statistics = () => {
  const stats = [
    {
      icon: <Users className="w-8 h-8" />,
      number: 157,
      suffix: "+",
      label: "Usuários Ativos",
      description: "Editores e criadores usando o sistema",
    },
    {
      icon: <TrendingUp className="w-8 h-8" />,
      number: 43,
      suffix: "+",
      label: "Streamers Monitorados",
      description: "Lives sendo acompanhadas diariamente",
    },
    {
      icon: <Clock className="w-8 h-8" />,
      number: 25137,
      suffix: "",
      label: "Clipes Entregues",
      description: "Momentos virais capturados automaticamente",
      formatNumber: (num: number) =>
        (num / 1000).toFixed(1).replace(".", ",") + "K",
    },
    {
      icon: <Star className="w-8 h-8" />,
      number: 181493,
      suffix: "",
      prefix: "R$ ",
      label: "Em Monetização",
      description: "Receita gerada pelos nossos usuários",
      formatNumber: (num: number) => (num / 1000).toFixed(0) + "K",
    },
  ];

  const StatCard = ({ stat, index }: { stat: any; index: number }) => {
    const { count, ref } = useCountAnimation({
      end: stat.number,
      duration: 2000 + index * 200,
    });

    const formatDisplayNumber = () => {
      if (stat.formatNumber) {
        return stat.formatNumber(count);
      }
      return count.toLocaleString("pt-BR");
    };

    return (
      <div
        ref={ref}
        className="text-center p-8 bg-gradient-card rounded-2xl border border-border/50 backdrop-blur-sm hover:scale-105 transition-all duration-300 shadow-card group"
      >
        <div className="inline-flex items-center justify-center w-16 h-16 bg-primary/20 rounded-2xl mb-6 group-hover:bg-primary/30 transition-colors duration-300">
          <div className="text-primary">{stat.icon}</div>
        </div>

        <div className="mb-4">
          <div className="text-4xl md:text-5xl font-bold text-foreground mb-2">
            {stat.prefix}
            {formatDisplayNumber()}
            {stat.suffix}
          </div>
          <div className="text-lg font-semibold text-primary mb-2">
            {stat.label}
          </div>
          <p className="text-sm text-muted-foreground">{stat.description}</p>
        </div>
      </div>
    );
  };

  return (
    <section className="py-20 bg-gradient-bg relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-10 left-10 w-64 h-64 bg-primary/30 rounded-full blur-3xl animate-float"></div>
        <div
          className="absolute bottom-10 right-10 w-80 h-80 bg-primary/20 rounded-full blur-3xl animate-float"
          style={{ animationDelay: "3s" }}
        ></div>
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Resultados que <span className="text-primary">Falam por Si</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Milhares de editores já economizam tempo e aumentam sua receita com
            nosso sistema de monitoramento inteligente.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <StatCard key={index} stat={stat} index={index} />
          ))}
        </div>
      </div>
    </section>
  );
};

export default Statistics;
