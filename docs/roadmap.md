# Clipador – Roadmap Imediato

## 1. Tooling
- ✅ Adotar npm workspaces e inicializar app web (Vite React) + migrar landing existente.
- Configurar lint/format compartilhado (ESLint, Prettier, Tailwind).
- ✅ Configurar uv workspace/Makefile para backend e pacotes Python.

## 2. Migração de Domínio
- ✅ Portar lógica de agrupamento de clipes, monitoramentos e validação ao vivo do `clipador-telegram` para `packages/clipador-core`.
- Extrair integrações (Twitch, storage, IA) para `clipador-adapters`.
- Conectar pipeline de geração/export social ao backend.

## 3. Backend
- ✅ Implementar autenticação básica (JWT) com `POST /auth/login` + proteção de rotas.
- ✅ Expor endpoints iniciais (`/clips/bursts/recent`, `/monitoring/*`, `/streams`, `/public/clips`).
- ✅ Configurar migrations Alembic + script de seed (`create_admin.py`).
- ✅ Ingestão contínua de clipes via Twitch API com modos de credencial (clipador_only, clipador_trial, client) e persistência de bursts.
- Configurar scheduler/worker dedicado (APS/Celery) + Redis.
- Implementar publicação social e integração com clip-editor via backend.

## 4. Frontend Web
- ✅ Bootstrapping do app (Vite + React) e autenticação com tela de login.
- ✅ Construir Dashboard com dados reais (bursts/presets) e gerenciamento de streams.
- Integrar editor admin (upload -> render) e painel de histórico completo.
- Adicionar gráficos, filtros avançados e notifications in-app.

## 5. Landing
- Migrar layout existente (`clipador-flow-landing-main`) para `apps/landing`.
- Ajustar assets, rotas e build estático.

## 6. Editor Admin
- Incorporar módulo `clip-editor` como serviço/worker.
- Expor endpoints e UI para processamento manual.

## 7. Observabilidade & Deploy
- Adicionar logging estruturado, health/metrics, tracing opcional.
- Criar pipelines de CI/CD independentes (web, landing, backend).
- Montar docker-compose para desenvolvimento local.
