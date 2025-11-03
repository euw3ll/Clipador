# Arquitetura Proposta – Clipador

## Estrutura de Diretórios Inicial
```
Clipador/
├── apps/
│   ├── web/        # App React/Next – dashboard Clipador
│   └── landing/    # Site institucional estático
├── services/
│   └── backend/    # API FastAPI + jobs de monitoramento/processamento
├── packages/
│   ├── clipador-core/     # Domínio compartilhado (monitoramento, regras, modelos)
│   ├── clipador-adapters/ # Integrações externas (Twitch, storage, IA, ffmpeg)
│   └── clip-editor/       # Incorporação do módulo clip-editor (admin)
├── infra/
│   ├── docker/            # Dockerfiles, compose, configs de deploy
│   └── ci/                # Workflows/GitHub Actions
├── docs/
└── scripts/
    └── dev/               # Scripts utilitários (start dev, seed, lint)
```

## Ferramentas e Tecnologias
- **Backend**: FastAPI + SQLAlchemy/Alembic; camada de acesso assíncrona via `asyncpg`; autenticação inicial com JWT (`/auth/login`); ingestão de clipes orquestrada por Celery/Redis (periodic task).
- **Frontend Web**: React (Vite ou Next.js). Reutilizar stack do landing quando possível (Tailwind, Radix, shadcn/ui).
- **Landing**: Vite + Tailwind (código atual adaptado).
- **Monorepo tooling**:
  - Frontend: npm workspaces (`package.json` raiz) para compartilhar dependências.
  - Backend: uv para gerenciar ambientes Python; scripts `make` ou `just`.
  - Lint/test: ESLint, Prettier/Tailwind; Pytest + Ruff/Mypy.
- **Infra**: Docker para desenvolvimento e deploy; GitHub Actions para CI com jobs separados (`web`, `landing`, `backend`).

- API REST principal (`/api/*`) retornando JSON (já disponível: `/auth/login`, `/clips/bursts/recent`, `/monitoring/*`, `/streams`, `/public/clips`).
- Canal de eventos em tempo real (WebSocket ou SSE) para alertas de clipes e progresso de jobs.
- Fila/worker para tarefas pesadas (render, export social) — atualmente Celery/Redis cuida da ingestão; expandir para outros jobs.

## Portas e Envs Padrão
- `apps/web`: Vite/Next em `3000`.
- `apps/landing`: Vite em `4000` (ou build estático).
- `services/backend`: FastAPI em `8000`; workers compartilham envs via `.env` comum.

- As classes/funções em `clipador-telegram/core` viram base do `clipador-core` (já disponível: agrupamento de clipes, presets e validação ao vivo).
- Backend hoje mantém tabelas `users`, `streamers`, `clips`, `bursts` e disponibiliza migrations via Alembic; próximos passos incluem modelos para jobs/bursts persistidos e histórico de publicação.
- O Telegram não fará parte do MVP web, mas mantemos estrutura para notificações web (push/email).
- O módulo `clip-editor` será integrado como pacote Python existente, com API interna exposta pelo backend e UI em `apps/web` (feature gated a admins).
- Legacy data (PostgreSQL) migra com as mesmas migrations; precisamos mapear schemas atuais e adaptar endpoints.
