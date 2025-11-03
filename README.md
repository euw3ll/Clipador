# Clipador Monorepo

Nova base da plataforma Clipador. Consolida monitoramento de streams, gestão de clipes, editor vertical e landing page em um único repositório web-first.

## Estrutura
```
apps/
  web/       # Dashboard Clipador (React/Next)
  landing/   # Site institucional (Vite)
services/
  backend/   # API + jobs de monitoramento
packages/
  clipador-core/      # Regras de domínio compartilhadas
  clipador-adapters/  # Integrações externas
  clip-editor/        # Módulo de edição vertical (admin)
infra/
  docker/   # Imagens/compose
  ci/       # Pipelines
scripts/
  dev/      # Scripts utilitários
docs/       # Requisitos, arquitetura, contratos
```

## Próximos Passos
- Inicializar toolchains (frontend: npm, backend: uv).
- Migrar regras de domínio e pipelines dos projetos existentes.
- Implementar API e UI conforme especificações em `docs/`.

## Testes

Use os alvos do `Makefile` para executar as suítes com os caminhos compartilhados já configurados:

```bash
make core-test
make backend-test
make db-upgrade    # aplica migrations no banco configurado
```

## Executando localmente

1. **Backend**
   ```bash
   export CLIPADOR_DATABASE_URL="postgresql://user:pass@localhost:5432/clipador"
   cp services/backend/.env.example services/backend/.env
   # edite CLIPADOR_KIRVANO_TOKEN e demais segredos conforme ambiente
   make db-upgrade
   python services/backend/scripts/create_admin.py admin 123456
   uv run --project services/backend uvicorn clipador_backend.main:app --reload --app-dir services/backend/src
   # Em outro terminal
   uv run --project services/backend celery -A clipador_backend.celery_app worker --loglevel=info
   uv run --project services/backend celery -A clipador_backend.celery_app beat --loglevel=info
   ```
2. **Web**
   ```bash
   npm install
   npm run dev -- --host
   ```
   Defina `VITE_API_BASE_URL` em `.env` da web (por padrão usa `http://localhost:8000`).
