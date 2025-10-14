import heroImage from "@/assets/hero-legal-automation.jpg";
import LogoImage from "@/assets/img/crawjud2.png";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  ArrowRight,
  Bot,
  CheckCircle2,
  Clock,
  Database,
  FileText,
  Moon,
  Shield,
  Sun,
  Zap,
} from "lucide-react";
import { useTheme } from "next-themes";
import { useNavigate } from "react-router-dom";
const UrlApp = import.meta.env.VITE_APP_URL || "http://localhost:5173";

const MailTo =
  "mailto:contato@reminfotech.net.br?subject=Quero%20automatizar%20meu%20escritório%20com%20CrawJUD&body=Olá,%20tenho%20interesse%20em%20automatizar%20meu%20escritório%20com%20CrawJUD.%20Gostaria%20de%20receber%20mais%20informações%20e%20agendar%20uma%20demonstração.";

const Index = () => {
  const _navigate = useNavigate();
  const { theme, setTheme } = useTheme();

  const features = [
    {
      icon: Bot,
      title: "Automação Inteligente",
      description:
        "Robôs automatizados com Selenium para rotinas jurídicas repetitivas",
    },
    {
      icon: Zap,
      title: "Processamento Assíncrono",
      description:
        "Celery e Redis para gerenciamento eficiente de tarefas em segundo plano",
    },
    {
      icon: Database,
      title: "Integração Completa",
      description: "SQLAlchemy para gestão robusta de dados e persistência",
    },
    {
      icon: Shield,
      title: "Seguro e Confiável",
      description: "Arquitetura modular com foco em segurança e escalabilidade",
    },
    {
      icon: Clock,
      title: "Tempo Real",
      description:
        "Comunicação instantânea via Socket.IO para atualizações em tempo real",
    },
    {
      icon: FileText,
      title: "API Moderna",
      description: "Quart para APIs web assíncronas de alta performance",
    },
  ];

  const technologies = [
    { name: "Python 3.13", color: "bg-primary/10 text-primary" },
    { name: "Selenium", color: "bg-primary-light/10 text-primary-light" },
    { name: "Celery", color: "bg-primary-glow/10 text-primary-glow" },
    { name: "Redis", color: "bg-primary/10 text-primary" },
    { name: "SQLAlchemy", color: "bg-primary-light/10 text-primary-light" },
    { name: "Socket.IO", color: "bg-primary-glow/10 text-primary-glow" },
    { name: "Quart", color: "bg-primary/10 text-primary" },
  ];

  const benefits = [
    "Otimize processos repetitivos automaticamente",
    "Aumente a eficiência operacional do escritório",
    "Integre-se com diversos sistemas judiciais",
    "Reduza erros humanos em tarefas rotineiras",
    "Escale operações sem aumentar custos proporcionalmente",
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="fixed top-0 w-full bg-background/80 backdrop-blur-lg border-b border-border z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 from-primary rounded-lg flex items-center justify-center">
                <img src={LogoImage} alt="CrawJUD Logo" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-primary to-primary-light bg-clip-text text-transparent">
                CrawJUD
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                className="hover:bg-primary/10"
              >
                <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
                <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
                <span className="sr-only">Alternar tema</span>
              </Button>
              <Button
                onClick={() => (window.location.href = UrlApp)}
                className="bg-primary hover:bg-primary-light transition-all duration-300 shadow-lg hover:shadow-primary/30"
              >
                Entrar
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-primary-light/5 to-primary-glow/5" />
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-72 h-72 bg-primary rounded-full blur-3xl" />
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-primary-light rounded-full blur-3xl" />
        </div>

        <div className="container mx-auto relative z-10">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <div className="inline-block">
                <span className="px-4 py-2 bg-primary/10 text-primary rounded-full text-sm font-semibold border border-primary/20">
                  Automação Jurídica Inteligente
                </span>
              </div>

              <h1 className="text-5xl lg:text-6xl font-bold leading-tight">
                <span className="bg-gradient-to-r from-primary via-primary-light to-primary-glow bg-clip-text text-transparent">
                  CrawJUD
                </span>
                <br />
                <span className="text-foreground">Automação Jurídica</span>
              </h1>

              <p className="text-xl text-muted-foreground leading-relaxed">
                Plataforma modular para automação de rotinas jurídicas,
                integrando robôs, APIs, tarefas assíncronas e comunicação em
                tempo real. Escalabilidade e eficiência para escritórios de
                advocacia modernos.
              </p>

              <div className="flex flex-col sm:flex-row gap-4">
                <Button
                  size="lg"
                  onClick={() => (window.location.href = MailTo)}
                  className="bg-gradient-to-r from-primary to-primary-light hover:from-primary-light hover:to-primary-glow text-primary-foreground shadow-lg hover:shadow-primary/30 transition-all duration-300 group"
                >
                  Começar Agora
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </div>
            </div>

            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-primary-light/20 rounded-3xl blur-3xl" />
              <img
                src={heroImage}
                alt="Automação Jurídica CrawJUD"
                className="relative rounded-3xl shadow-2xl border border-primary/10"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">
              Por que escolher o <span className="text-primary">CrawJUD</span>?
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Transforme a operação do seu escritório com automação inteligente
            </p>
          </div>

          <div className="max-w-3xl mx-auto space-y-4">
            {benefits.map((benefit, index) => (
              <div
                key={index}
                className="flex items-center gap-4 p-4 bg-background rounded-lg border border-border hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:shadow-primary/10"
              >
                <CheckCircle2 className="h-6 w-6 text-primary flex-shrink-0" />
                <span className="text-lg">{benefit}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">
              Recursos <span className="text-primary">Principais</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Tecnologia de ponta para automação jurídica completa
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <Card
                key={index}
                className="p-6 hover:shadow-xl hover:shadow-primary/10 transition-all duration-300 border-border hover:border-primary/50 group"
              >
                <div className="mb-4 w-12 h-12 bg-gradient-to-br from-primary to-primary-light rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                  <feature.icon className="h-6 w-6 text-primary-foreground" />
                </div>
                <h3 className="text-xl font-bold mb-2 group-hover:text-primary transition-colors">
                  {feature.title}
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  {feature.description}
                </p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Technologies Section */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">
              Stack <span className="text-primary">Tecnológico</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Construído com as melhores ferramentas do mercado
            </p>
          </div>

          <div className="flex flex-wrap justify-center gap-4 max-w-4xl mx-auto">
            {technologies.map((tech, index) => (
              <div
                key={index}
                className={`px-6 py-3 rounded-full font-semibold border transition-all duration-300 hover:scale-110 hover:shadow-lg ${tech.color}`}
              >
                {tech.name}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary via-primary-light to-primary-glow opacity-95" />
        <div className="absolute inset-0">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary-foreground/10 rounded-full blur-3xl" />
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-primary-foreground/10 rounded-full blur-3xl" />
        </div>

        <div className="container mx-auto text-center relative z-10">
          <h2 className="text-4xl lg:text-5xl font-bold text-primary-foreground mb-6">
            Pronto para automatizar seu escritório?
          </h2>
          <p className="text-xl text-primary-foreground/90 mb-8 max-w-2xl mx-auto">
            Junte-se aos escritórios de advocacia que já otimizaram suas
            operações com o CrawJUD
          </p>
          <Button
            size="lg"
            onClick={() => (window.location.href = MailTo)}
            className="bg-background text-primary hover:bg-background/90 shadow-xl hover:shadow-2xl transition-all duration-300 group"
          >
            Fale com a gente!
            <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 border-t border-border">
        <div className="container mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary-light rounded-lg flex items-center justify-center">
                <span className="text-primary-foreground font-bold">C</span>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-primary to-primary-light bg-clip-text text-transparent">
                CrawJUD
              </span>
            </div>
            <div className="text-muted-foreground text-sm">
              © 2025 CrawJUD. Automação Jurídica Inteligente.
            </div>
            <div className="flex gap-6 text-sm text-muted-foreground">
              <a href="#" className="hover:text-primary transition-colors">
                Documentação
              </a>
              <a href="#" className="hover:text-primary transition-colors">
                Suporte
              </a>
              <a href="#" className="hover:text-primary transition-colors">
                Privacidade
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
