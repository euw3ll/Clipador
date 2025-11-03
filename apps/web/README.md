# Clipador Web App

Dashboard principal do Clipador com autenticação JWT, visualização de bursts recentes e gestão dos streamers monitorados.

## Scripts
- `npm run dev` – inicia o servidor de desenvolvimento (porta 3000).
- `npm run build` – gera build de produção.
- `npm run preview` – pré-visualiza o build.
- `npm run lint` – placeholder para linting (configurar posteriormente).

## Configuração
- Defina `VITE_API_BASE_URL` em `.env` (ex.: `http://localhost:8000`).
- Crie um usuário admin no backend (`python services/backend/scripts/create_admin.py admin 123456`).
- Após login, o painel consome `/clips/bursts/recent`, `/monitoring/resolve` e `/streams`.
