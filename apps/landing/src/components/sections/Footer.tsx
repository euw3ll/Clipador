import { Heart, MessageCircle, Mail } from "lucide-react";
import logo from "@/assets/logo-branco.png";
import { Link } from "react-router-dom";
import { NAV_SECTIONS } from "@/lib/siteSections";

const Footer = () => {
  // Lista de links do cabeçalho
  const navItems = NAV_SECTIONS;

  return (
    <footer className="relative py-16 bg-gradient-to-t from-card/30 to-background border-t border-border/50 overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute top-1/2 left-1/4 w-64 h-64 bg-primary/20 rounded-full blur-3xl animate-pulse"></div>
        <div
          className="absolute top-1/3 right-1/4 w-48 h-48 bg-primary/10 rounded-full blur-3xl animate-pulse"
          style={{ animationDelay: "1s" }}
        ></div>
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <div className="grid md:grid-cols-4 gap-12 mb-12">
          {/* Brand Section */}
          <div className="md:col-span-2 space-y-4 animate-fade-in">
            <div className="flex items-center gap-3">
              <Link to="/" aria-label="Ir para o início">
                <img
                  src={logo}
                  alt="Clipador Logo"
                  className="w-[140px] h-[60px] object-contain border-none"
                />
              </Link>
            </div>
            <p className="text-muted-foreground max-w-md leading-relaxed">
              Revolucionando a criação de conteúdo com IA. Monitore streamers
              continuamente e receba automaticamente apenas os clipes mais
              virais.
            </p>
          </div>

          {/* Quick Links */}
          <div
            className="space-y-4 animate-fade-in"
            style={{ animationDelay: "0.1s" }}
          >
            <h4 className="text-lg font-semibold text-foreground">
              Links Rápidos
            </h4>
            <div className="space-y-3">
              {/* Loop para criar os links dinamicamente */}
              {navItems.map((item) => (
                <Link
                  key={item.label}
                  to={item.path}
                  className="block text-muted-foreground hover:text-primary transition-colors duration-300 hover:translate-x-1 transform"
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>

          {/* Contact */}
          <div
            className="space-y-4 animate-fade-in"
            style={{ animationDelay: "0.2s" }}
          >
            <h4 className="text-lg font-semibold text-foreground">Contato</h4>
            <div className="space-y-3">
              <div
                className="flex items-center gap-3 text-muted-foreground hover:text-primary transition-colors duration-300 cursor-pointer group"
                onClick={() =>
                  window.open("https://t.me/ClipadorBot", "_blank")
                }
              >
                <MessageCircle className="w-4 h-4 group-hover:scale-110 transition-transform" />
                <span>Telegram Bot</span>
              </div>
              <div className="flex items-center gap-3 text-muted-foreground">
                <Mail className="w-4 h-4" />
                <span>suporteclipador@gmail.com</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-border/30">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div
              className="flex items-center gap-2 text-muted-foreground text-sm animate-fade-in"
              style={{ animationDelay: "0.3s" }}
            >
              <span>Feito com</span>
              <Heart className="w-4 h-4 text-primary animate-pulse" />
              <span>por</span>
              <span className="text-foreground font-medium hover:text-primary transition-colors duration-300">
                W3Core
              </span>
            </div>

            <div
              className="text-muted-foreground text-sm animate-fade-in"
              style={{ animationDelay: "0.4s" }}
            >
              © 2024 Clipador. Todos os direitos reservados.
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
