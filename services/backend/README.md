# Clipador Backend

Serviço FastAPI responsável pela API do Clipador e orquestração de jobs de monitoramento/processamento. Já expõe rotas para bursts recentes e presets de monitoramento, consumindo o domínio em `packages/clipador-core`.

## Desenvolvimento

```bash
export CLIPADOR_DATABASE_URL="postgresql://user:pass@localhost:5432/clipador"
uv run --project services/backend uvicorn clipador_backend.main:app --reload --app-dir services/backend/src
```

### Endpoints úteis

- `GET /health`
- `POST /auth/login`
- `GET /clips/bursts/recent?since_minutes=60`
- `GET /monitoring/presets`
- `POST /monitoring/resolve`
- `GET /streams`
- `POST /streams`
- `DELETE /streams/{id}`

### Configuração

Variáveis principais (ver `.env.example`):

- `CLIPADOR_DATABASE_URL` — URL do Postgres. O driver assíncrono `asyncpg` é aplicado automaticamente.
- `CLIPADOR_TWITCH_CLIENT_ID` / `CLIPADOR_TWITCH_CLIENT_SECRET` — credenciais para capturar clips da Twitch (obrigatório para ingestão).
- `CLIPADOR_APP_ENV` — influencia logs/echo do SQLAlchemy.
- `CLIPADOR_JWT_SECRET` — segredo usado para assinar os JWTs do painel.
- `CLIPADOR_REDIS_URL` — broker/result backend do Celery (default `redis://localhost:6379/0`).

Os modelos ORM atuais contemplam `users`, `streamers`, `clips`, `bursts` e `burst_clips`. Para gerar as tabelas execute `alembic upgrade head`. Um script utilitário (`python services/backend/scripts/create_admin.py <user> <senha>`) cria o primeiro usuário admin.

O loop de ingestão (`ClipIngestionService`) roda via Celery/Redis; mantenha worker e beat ativos para sincronizar clipes da Twitch a cada 3 minutos. Certifique-se de cadastrar streamers (via API ou script) para que os bursts apareçam no dashboard.

### Worker & Scheduler (Celery)

```bash
uv run --project services/backend celery -A clipador_backend.celery_app worker --loglevel=info
uv run --project services/backend celery -A clipador_backend.celery_app beat --loglevel=info
```

O beat dispara `clipador.ingestion.sync` a cada 180s. Use `GET /health/worker` para verificar o status. Logs estruturados (`ingestion_*`) são emitidos em caso de falha ou criação de bursts.

### Testes

```bash
PYTHONPATH=$(pwd)/packages/clipador-core/src:$(pwd)/packages/clipador-adapters/src \
  uv run --project services/backend --extra dev pytest services/backend/tests
```

O comando acima instala as dependências opcionais (`dev`) e garante acesso aos pacotes compartilhados via `PYTHONPATH`. O target `make backend-test` já encapsula essa chamada.

### Seed/Migração

Para importar streamers/clipes legados via CSV:

```bash
uv run --project services/backend python services/backend/scripts/seed_from_csv.py \
  --streamers dados/streamers.csv \
  --clips dados/clipes.csv
```

Campos esperados:
- `streamers.csv`: `twitch_user_id`, `display_name`, `avatar_url`, `monitor_interval_seconds`, `monitor_min_clips`, `api_mode`, `trial_expires_at`, `client_twitch_client_id`, `client_twitch_client_secret`.
- `clipes.csv`: `clip_id`, `streamer_twitch_user_id`, `created_at`, `viewer_count`, `video_id`, `title`, `duration`.
