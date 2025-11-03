// src/pages/DownloadPage.tsx

import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, AlertTriangle, Home, Instagram, Music2 } from "lucide-react";
import logo from "@/assets/logo-branco.png";

// --- API TWITCH ---
// Resolve a base da API em produção e desenvolvimento.
// - Em dev: usa localhost:3001
// - Em produção: usa o mesmo domínio (rota /api)
const getApiBaseUrl = () => {
  const envBase = (import.meta as any)?.env?.VITE_API_BASE_URL as
    | string
    | undefined;
  if (envBase) return envBase.replace(/\/$/, "");

  const host = window.location.hostname;
  const isLocal =
    host === "localhost" || host === "12-7.0.0.1" || host === "[::1]";
  return isLocal ? "http://localhost:3001" : ""; // empty -> same origin
};

const getClipDownloadUrl = async (slug: string): Promise<string> => {
  console.log(`Buscando URL de download para o slug: ${slug}`);
  try {
    const base = getApiBaseUrl();
    const url = `${base}/api/clip/${encodeURIComponent(slug)}`;
    const response = await fetch(url);
    if (!response.ok) {
      let errorMessage = "Erro ao buscar o clipe.";
      try {
        const errorData = await response.json();
        errorMessage = errorData.error || errorMessage;
      } catch {
        try {
          const txt = await response.text();
          if (txt?.startsWith("<!DOCTYPE")) {
            errorMessage =
              "A rota /api pode não estar configurada no servidor.";
          }
        } catch {}
      }
      throw new Error(errorMessage);
    }

    const data = await response.json();
    return data.downloadUrl as string;
  } catch (error) {
    console.error("Erro na chamada da API:", error);
    throw error;
  }
};
const DownloadPage = () => {
  const { slug } = useParams<{ slug: string }>();
  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading"
  );
  const [errorMessage, setErrorMessage] = useState("");
  const [showCta, setShowCta] = useState(false);

  useEffect(() => {
    const fetchAndRedirect = async () => {
      if (!slug) {
        setErrorMessage("O link do clipe parece estar inválido ou incompleto.");
        setStatus("error");
        return;
      }

      try {
        // Primeiro validamos o slug (mantém UX de erro amigável em vez de JSON cru)
        await getClipDownloadUrl(slug);
        setStatus("success");
        // Dispara o download em um iframe oculto para manter controle da aba
        const base = getApiBaseUrl();
        // Usa proxy para forçar Content-Disposition: attachment (evita preview em alguns navegadores)
        const downloadUrl = `${base}/api/clip/${encodeURIComponent(
          slug
        )}/download?mode=proxy`;

        const iframe = document.createElement("iframe");
        iframe.style.display = "none";
        iframe.src = downloadUrl;
        document.body.appendChild(iframe);

        // Decide se podemos fechar a aba (apenas se foi aberta por script)
        const canClose = !!window.opener;

        // Fechamento/CTA após pequeno delay, para dar tempo do download iniciar
        setTimeout(() => {
          if (canClose) {
            try {
              window.close();
            } catch {}
          } else {
            setShowCta(true);
          }
        }, 3000);
      } catch (error) {
        console.error("Erro ao buscar clipe:", error);
        setErrorMessage(
          "O clipe não foi encontrado ou expirou. Tente novamente ou verifique o link."
        );
        setStatus("error");
      }
    };

    fetchAndRedirect();
  }, [slug]);

  const renderContent = () => {
    // CTA dentro do mesmo layout da página
    if (showCta) {
      return (
        <>
          <CardTitle className="text-2xl mb-2">
            Já seguiu a gente nas redes sociais?
          </CardTitle>
          <CardDescription className="mb-6">
            Siga o <b>@eoclipador</b> e não perca novidades, dicas e drops
            exclusivos.
          </CardDescription>

          <div className="flex flex-col sm:flex-row gap-3 w-full justify-center">
            <Button asChild variant="destructive">
              <a
                href="https://www.instagram.com/eoclipador"
                target="_blank"
                rel="noreferrer noopener"
                className="w-full sm:w-auto"
              >
                <Instagram className="w-4 h-4 mr-2" />
                Instagram
              </a>
            </Button>
            <Button asChild variant="outline">
              <a
                href="https://www.tiktok.com/@eoclipador"
                target="_blank"
                rel="noreferrer noopener"
                className="w-full sm:w-auto"
              >
                <Music2 className="w-4 h-4 mr-2" />
                TikTok
              </a>
            </Button>
          </div>

          {slug && (
            <p className="text-xs text-muted-foreground mt-6 text-center">
              Se o seu navegador não baixou automaticamente,{" "}
              <a
                href={`${getApiBaseUrl()}/api/clip/${encodeURIComponent(
                  slug
                )}/download?mode=proxy`}
                className="underline hover:text-primary"
              >
                clique aqui.
              </a>
            </p>
          )}
        </>
      );
    }

    switch (status) {
      case "loading":
        return (
          <>
            <Loader2 className="w-12 h-12 text-primary animate-spin mb-4" />
            <CardTitle className="text-2xl">
              Preparando seu download...
            </CardTitle>
            <CardDescription>
              Estamos buscando o seu clipe. O download começará em instantes.
            </CardDescription>
          </>
        );
      case "success":
        return (
          <>
            <Loader2 className="w-12 h-12 text-primary animate-spin mb-4" />
            <CardTitle className="text-2xl">Redirecionando...</CardTitle>
            <CardDescription>
              Seu download está pronto e deve começar agora.
            </CardDescription>
          </>
        );
      case "error":
        return (
          <>
            <AlertTriangle className="w-12 h-12 text-destructive mb-4" />
            <CardTitle className="text-2xl">Oops! Algo deu errado</CardTitle>
            <CardDescription className="mb-6">{errorMessage}</CardDescription>
            <Button asChild>
              <Link to="/">
                <Home className="w-4 h-4 mr-2" />
                Voltar para o Início
              </Link>
            </Button>
          </>
        );
    }
  };

  return (
    <div className="min-h-screen w-full bg-gradient-bg flex items-center justify-center p-4">
      <Card className="w-full max-w-md text-center bg-card/50 backdrop-blur-sm border-border/50">
        <CardHeader>
          <img src={logo} alt="Clipador Logo" className="w-32 mx-auto mb-4" />
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center p-8">
          {renderContent()}
        </CardContent>
      </Card>
    </div>
  );
};

export default DownloadPage;
