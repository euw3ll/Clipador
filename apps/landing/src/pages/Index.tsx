import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import Navigation from "@/components/sections/Navigation";
import Hero from "@/components/sections/Hero";
import VideoSection from "@/components/sections/VideoSection";
import PricingSection from "@/components/sections/PricingSection";
import Statistics from "@/components/sections/Statistics";
import PlatformIcons from "@/components/sections/PlatformIcons";
import SocialProof from "@/components/sections/SocialProof";
import FinalCTA from "@/components/sections/FinalCTA";
import FAQSection from "@/components/sections/FAQSection";
import Footer from "@/components/sections/Footer";
import LatestClips from "@/components/sections/LatestClips";
import {
  DEFAULT_SECTION_META,
  getSectionMeta,
} from "@/lib/siteSections";

const setMetaTag = (
  identifier: string,
  content: string,
  attribute: "name" | "property" = "name"
) => {
  const selector = attribute === "name"
    ? `meta[name="${identifier}"]`
    : `meta[property="${identifier}"]`;
  const element = document.querySelector<HTMLMetaElement>(selector);
  if (element) {
    element.setAttribute("content", content);
  }
};

const Index = () => {
  const location = useLocation();

  useEffect(() => {
    const meta = getSectionMeta(location.pathname);

    document.title = meta.title;
    setMetaTag("description", meta.description);
    setMetaTag("keywords", meta.keywords ?? DEFAULT_SECTION_META.keywords ?? "");
    setMetaTag("twitter:title", meta.title);
    setMetaTag("twitter:description", meta.description);
    setMetaTag("twitter:url", meta.canonical);
    setMetaTag("og:title", meta.title, "property");
    setMetaTag("og:description", meta.description, "property");
    setMetaTag("og:url", meta.canonical, "property");

    const canonicalLink = document.querySelector<HTMLLinkElement>(
      'link[rel="canonical"]'
    );
    if (canonicalLink) {
      canonicalLink.setAttribute("href", meta.canonical);
    }

    const scrollTimeout = window.setTimeout(() => {
      if (meta.sectionId) {
        const element = document.getElementById(meta.sectionId);
        if (element) {
          element.scrollIntoView({ behavior: "smooth", block: "start" });
          return;
        }
      }
      window.scrollTo({ top: 0, behavior: "smooth" });
    }, 80);

    return () => window.clearTimeout(scrollTimeout);
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main>
        {/* HEADLINE */}
        <section id="hero">
          <Hero />
        </section>
        
        {/* FUNCIONAMENTO */}
        <section id="video">
          <VideoSection />
        </section>

        <LatestClips />
        
        {/* PLANOS */}
        <section id="pricing">
          <PricingSection />
        </section>
        
        {/* NUMEROS */}
        <section id="stats">
          <Statistics />
        </section>
        
        <PlatformIcons />
        
        <section id="testimonials">
          <SocialProof />
        </section>
        
        {/* ULTIMO CTA */}
        <FinalCTA />
        
        {/* FAQ */}
        <section id="faq">
          <FAQSection />
        </section>
      </main>
      
      <Footer />
    </div>
  );
};

export default Index;
