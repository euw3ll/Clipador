Clipador Site — Implantação/Operação na VPS (Traefik)

Visão geral
- Domínios: www.clipador.com (principal) e clipador.com (redireciona para www)
- TLS: Let’s Encrypt (ACME http-01) via Traefik v3, certresolver letsencrypt
- App: Vite + React (SPA) servido por Nginx com fallback para /index.html
- API: Node/Express em `api/server.js`
- Repositório remoto na VPS: `/opt/clipador-site`

Arquitetura (docker-compose.yml)
- `web` (Nginx):
  - Serve o build estático (dist)
  - SPA fallback e cache de estáticos
  - Headers de segurança + HSTS
- `api` (Express): rotas principais
  - `GET /api/health` → status JSON
  - `GET /api/clip/:slug` → retorna `{ downloadUrl }` assinado (Twitch). O browser baixa direto da Twitch (sem uso de banda da VPS)
  - `GET /social/exports/*` → serve MP4 finalizados (se usados pela publicação social)
- `traefik` (já existente na VPS):
  - Roteia Host(www.clipador.com) → `web`
  - Roteia Host(www.clipador.com) + PathPrefix(/api|/health|/social) → `api`
  - Routers HTTP (web) redirecionam para HTTPS; apex redireciona para www
  - `traefik.docker.network=traefik` definido para web/api

Diretórios/volumes
- Código: `/opt/clipador-site`
- Volumes Docker:
  - `exports_data` → montado em `/app/exports` (api)
  - `temp_data` → montado em `/app/temp` (api)

Configurações (variáveis de ambiente)
- Arquivo `/opt/clipador-site/.env`
  - `SITE_HOST=clipador.com`
- Arquivo `/opt/clipador-site/api/.env` (base em `api/.env.example`)
  - `PORT=3001`
  - `EXPORTS_DIR=/app/exports`
  - `SOCIAL_TEMP_DIR=/app/temp`
  - `SOCIAL_EXPORT_BASE_URL=https://clipador.com/social/exports`
  - `SOCIAL_JOB_API_TOKEN=<token seguro>`
  - `IG_USER_ID=` (opcional)
  - `IG_ACCESS_TOKEN=` (opcional)
  - `SOCIAL_JOB_TIMEOUT_MINUTES=10`
  - `SOCIAL_JOB_POLL_INTERVAL_SECONDS=8`
  - `FORCE_PROXY_DOWNLOAD=false` → comportamento da rota de download:
    - `false` (recomendado): redireciona para CDN (zero uso de banda na VPS)
    - `true`: faz proxy e força download com `Content-Disposition: attachment`
    - Também é possível forçar por request usando `?mode=proxy` ou `?mode=redirect`

CI/CD (GitHub Actions)
- Workflow: `.github/workflows/deploy.yml`
- Disparo: push na branch `main` ou manual (workflow_dispatch)
- Secrets necessários no repositório:
  - `SSH_HOST=72.60.159.107`
  - `SSH_PORT=22`
  - `SSH_USER=deploy`
  - `SSH_PRIVATE_KEY` = chave privada do CI (ed25519, BEGIN/END)
- O job faz: checkout → rsync para `/opt/clipador-site` → garante rede `traefik` → `docker compose build --pull` e `up -d`

DNS e portas
- `A clipador.com → 72.60.159.107`; `CNAME www → clipador.com` (apex → www)
- UFW/Firewall: portas 80 e 443 liberadas (Traefik), 22 liberada para SSH

Rodar localmente (opcional)
- `npm ci && npm run build` (gera `dist/`)
- `docker compose up -d --build`
- Acesse via Traefik/local conforme sua configuração

Verificações rápidas
- Containers: `docker compose ps`
- Logs: `docker logs -f clipador_web` e `docker logs -f clipador_api`
- Health: `curl -k https://www.clipador.com/health` (deve retornar JSON com `status=ok`)
- Download: `https://clipador.com/download/<slug>`
  - Front valida `/api/clip/:slug`.
  - Depois chama `/api/clip/:slug/download`.
  - Padrão: redireciona (302) direto para o CDN (zero banda). Para proxy forçado: `?mode=proxy`.
- TLS: `curl -I http://clipador.com` (308 → https) e `curl -I https://clipador.com` (308/301 → https://www.clipador.com)

Operação comum
- Redeploy manual: `docker compose up -d --build`
- Reiniciar apenas API: `docker compose restart api`
- Limpar imagens: `docker image prune -f`

Backup
- Exportações (se usadas):
  - `docker run --rm -v clipador-site_exports_data:/data -v $(pwd):/backup busybox tar czf /backup/exports_$(date +%F).tar.gz -C /data .`

Troubleshooting
- Certificado inválido/ausente:
  - Ver Traefik: `docker logs -f traefik | egrep -i "acme|letsencrypt|clipador.com|challenge|certificate"`
  - Confirme DNS (A → 72.60.159.107) e porta 80 aberta (HTTP-01)
- 504/timeout via Traefik:
  - Confirme que `traefik`, `clipador_web`, `clipador_api` estão na rede `traefik`: `docker network inspect traefik`
  - Verifique labels `traefik.docker.network=traefik` e services explícitos nos routers (`clipador-api/health/social`)
- 404 em `/download/:slug`:
  - Ver logs do `clipador_web` (fallback SPA) e `clipador_api` (resposta do Twitch)
- Uso de banda: por padrão é zero (redirecionamento). Se `FORCE_PROXY_DOWNLOAD=true` ou `?mode=proxy`, o arquivo passa pela VPS.

- Notas finais
- clipador.com redireciona permanentemente para https://www.clipador.com/
- HSTS ativo (Nginx) — cuidado ao trocar de domínio em ambientes de teste.
