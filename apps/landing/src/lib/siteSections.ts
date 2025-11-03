const BASE_URL = "https://www.clipador.com";

export type SiteSectionMeta = {
  label: string;
  path: string;
  sectionId: string;
  title: string;
  description: string;
  keywords?: string;
  canonical: string;
};

type RawSectionMeta = Omit<SiteSectionMeta, "canonical">;

const normalizePath = (path: string): string => {
  if (!path || path === "/") {
    return "/";
  }
  return path.endsWith("/") ? path.slice(0, -1) : path;
};

const rawSections: RawSectionMeta[] = [
  {
    label: "Início",
    path: "/",
    sectionId: "hero",
    title: "Clipador - Melhores momentos das lives!",
    description:
      "Cansado de assistir horas de live? Nossa IA encontra os clipes que viralizam para você! Seu tempo vale ouro, não clipes ruins.",
    keywords:
      "clipador, clipes automáticos, melhores momentos de live, cortes de live, bot de clipes",
  },
  {
    label: "Demo",
    path: "/como-funciona",
    sectionId: "video",
    title: "Como funciona o Clipador | Cortes automáticos das lives",
    description:
      "Entenda como o Clipador monitora lives 24/7, identifica momentos virais e entrega cortes prontos direto no seu Telegram.",
    keywords:
      "como funciona clipador, ia para cortes de live, demo clipador, automação de clipes",
  },
  {
    label: "Planos",
    path: "/planos",
    sectionId: "pricing",
    title: "Planos do Clipador | Escolha o pacote ideal para seus clipes",
    description:
      "Compare os planos Mensal Solo, Mensal Plus e Anual Pro do Clipador e escolha o limite ideal de streamers para monitorar.",
    keywords:
      "planos clipador, preços clipador, assinatura clipador, mensalidade clipador",
  },
  {
    label: "Estatísticas",
    path: "/estatisticas",
    sectionId: "stats",
    title: "Resultados do Clipador | Produtividade real com IA",
    description:
      "Veja os números do Clipador: usuários ativos, streamers monitorados, clipes entregues e receita gerada com IA.",
    keywords:
      "resultados clipador, estatísticas clipador, clipes virais, produtividade clipador",
  },
  {
    label: "Depoimentos",
    path: "/depoimentos",
    sectionId: "testimonials",
    title: "Depoimentos sobre o Clipador | Prova social dos editores",
    description:
      "Descubra como editores, agências e criadores usam o Clipador para viralizar clipes e acelerar monetização.",
    keywords:
      "depoimentos clipador, avaliações clipador, feedback clipador, social proof clipador",
  },
  {
    label: "FAQ",
    path: "/faq",
    sectionId: "faq",
    title: "FAQ Clipador | Tire suas dúvidas sobre cortes automáticos",
    description:
      "Perguntas frequentes sobre o Clipador: monitoramento automático, planos, cancelamento e entrega de clipes.",
    keywords:
      "faq clipador, dúvidas clipador, suporte clipador, ajuda clipador",
  },
];

const sectionsWithCanonical: SiteSectionMeta[] = rawSections.map((section) => ({
  ...section,
  canonical: `${BASE_URL}${section.path === "/" ? "/" : section.path}`,
}));

const SECTION_META_MAP = sectionsWithCanonical.reduce<Record<string, SiteSectionMeta>>(
  (acc, section) => {
    acc[section.path] = section;
    return acc;
  },
  {}
);

export const DEFAULT_SECTION_META = SECTION_META_MAP["/"];

export const NAV_SECTIONS = sectionsWithCanonical.map(({ label, path }) => ({
  label,
  path,
}));

export const getSectionMeta = (path: string): SiteSectionMeta => {
  const normalized = normalizePath(path);
  return SECTION_META_MAP[normalized] ?? DEFAULT_SECTION_META;
};

export const getBaseUrl = () => BASE_URL;
