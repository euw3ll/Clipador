# Clipador - Landing + API

Aplicação web (Vite + React + TypeScript) com API Node/Express para resolução de URLs de download de clipes.

## Desenvolvimento local

Pré‑requisitos: Node.js 18+ e npm.

```sh
npm ci
npm run dev
```

API (porta padrão `3001`):

```sh
cd api
npm ci
node server.js
```

Defina `PORT` no `api/.env` se quiser alterar a porta.

### Rota pública para vídeos exportados (Auto‑post social)

O servidor Express também pode servir vídeos `.mp4` em uma rota pública estável,
usada pelo Instagram/TikTok para baixar o arquivo gerado pelo bot:

- Rota: `GET /social/exports/<arquivo>`
- Pasta configurável via `EXPORTS_DIR` (padrão: `api/exports`)

Exemplo `.env` em `api/.env`:

```
PORT=3001
EXPORTS_DIR=/var/www/clipador-exports
```

Se você usa Nginx para o domínio `clipador.com`, crie um proxy para a rota:

```
location /social/exports/ {
  proxy_pass http://127.0.0.1:3001/social/exports/;
  proxy_http_version 1.1;
}
```

No bot, configure a URL base `SOCIAL_EXPORT_BASE_URL=https://clipador.com/social/exports`
e aponte o caminho físico de gravação para o mesmo diretório (`SOCIAL_EXPORT_DIR`),
caso bot e site compartilhem o mesmo servidor/volume.

## Build

```sh
npm run build
```

Os arquivos ficam em `dist/`.
