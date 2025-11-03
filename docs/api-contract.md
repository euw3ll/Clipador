# Clipador – Esboço de API (v1)

## Convenções
- Base URL: `/api`
- Autenticação: Bearer JWT para rotas autenticadas (`Authorization: Bearer <token>`).
- Respostas seguem envelope padrão:
  ```json
  {
    "data": {...},
    "meta": {...},
    "error": null
  }
  ```
  ou, em caso de erro:
  ```json
  {
    "data": null,
    "error": {"code": "string", "message": "string", "details": {...}}
  }
  ```
- Timestamps em ISO8601 UTC. IDs UUID v4.

## Autenticação e Usuários
- `POST /auth/login`
  - Body: `{ "username": "admin", "password": "..." }`
  - Retorna `{ "access_token": "...", "token_type": "bearer" }`.
- (`futuro`) `POST /auth/refresh`
- (`futuro`) `POST /auth/logout`
- (`futuro`) `GET /users/me`
  - Retorna perfil do usuário autenticado, roles (`["admin"]`).
- (Futuro) `POST /users` para convidar criadores.

## Monitoramentos (Streams)
- `GET /streams`
  - Retorna lista de streamers monitorados (id, twitch_user_id, display_name, interval/threshold).
- `POST /streams`
  - Body:
    ```json
    {
      "twitch_user_id": "12345",
      "display_name": "Streamer",
      "avatar_url": null,
      "monitor_interval_seconds": 180,
      "monitor_min_clips": 2,
      "api_mode": "clipador_only",
      "trial_expires_at": "2025-01-01T00:00:00Z",
      "client_twitch_client_id": "...",
      "client_twitch_client_secret": "..."
    }
    ```
  - Retorna streamer criado.
- `DELETE /streams/{id}`
  - Remove streamer monitorado.
- (Futuro) `PATCH /streams/{id}` para ajustes finos e pausa/resume.

## Presets / Regras
- `GET /presets` – configurações de monitoramento disponíveis.
- `POST /presets` – criar preset customizado.

## Clipes
- `GET /clips`
  - Query: `stream_id`, `status`, `date_from`, `date_to`, `search`.
  - Resposta inclui metadados do streamer (`streamer_name`, `streamer_external_id`).
- `GET /clips/{clip_id}`
- `POST /clips/{clip_id}/tag`
- `POST /clips/{clip_id}/favorite`
- `POST /clips/{clip_id}/archive`
- `POST /clips/{clip_id}/download-link`
  - Gera URL temporária (S3/R2).
- `POST /clips/{clip_id}/send-to-editor`
- `POST /clips/{clip_id}/export-social`
  - Body: `{ "platforms": ["instagram"], "caption_override": "...", "schedule_at": null }`

## Bursts / Alertas
- `GET /bursts`
  - Lista agrupamentos (burst_id, horário, stream, clipes incluídos, status).
- `GET /bursts/{burst_id}`
- `POST /bursts/{burst_id}/resolve`
- `POST /bursts/{burst_id}/snooze`

## Editor (Admin)
- `POST /editor/sessions`
  - Cria sessão de edição para um clipe (retorna session_id, clipe, parâmetros default).
- `GET /editor/sessions/{session_id}`
- `PATCH /editor/sessions/{session_id}`
  - Body parcial para ajustes (layout, subtitles config, crop).
- `POST /editor/sessions/{session_id}/render`
  - Inicia job de render.
- `GET /editor/renders`
  - Lista jobs (status, progress, output URLs).
- `GET /editor/renders/{render_id}`
- `POST /editor/renders/{render_id}/retry`

## Publicação Social
- `GET /social/accounts`
- `POST /social/accounts`
- `GET /social/jobs`
- `POST /social/jobs`
- `POST /social/jobs/{job_id}/cancel`

## Integrações e Configurações
- `GET /settings`
- `PATCH /settings`
- `GET /integrations`
  - Lista chaves configuradas e status.
- `POST /integrations/twitch`
  - Salva credenciais/testa conexão.
- `POST /integrations/openai`
- `POST /integrations/storage`

## Eventos em Tempo Real (WebSocket)
- Endpoint: `GET /ws/events`
- Eventos esperados:
  - `stream.status` – muda online/offline.
  - `burst.detected` – novo agrupamento encontrado.
  - `clip.created` – novo clipe disponível.
  - `editor.render.update` – progresso atual.
  - `social.job.update` – status de publicação.

## Observabilidade / Suporte
- `GET /health` – status geral.
- `GET /metrics` – exposto para Prometheus (auth protegida).
- `GET /logs` (admin) – últimas entradas relevantes (erro jobs, etc.).
- `GET /health/worker` – verifica resposta dos workers Celery.
- `GET /public/clips` – lista clipes recentes para exibição na landing page (sem autenticação).
