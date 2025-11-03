# Clipador – Documento de Requisitos Iniciais

## Visão Geral
- Consolidar em um único repositório (`Clipador`) os projetos atuais: `clipador-telegram` (lógica de monitoramento), `clipador-flow-landing-main` (landing page) e `clip-editor` (ferramentas de edição de clipes).
- Transformar o Clipador em uma plataforma totalmente web-first, substituindo por completo o fluxo via Telegram.

## Módulos Planejados
- `apps/web`: interface principal onde usuários acompanham lives monitoradas, recebem alertas e gerenciam clipes.
- `apps/landing`: site institucional com marketing, planos e formulários de contato/conversão. Deve ser implantado de forma independente.
- `services/backend`: API REST/WS + orquestração de jobs (monitoramento Twitch, geração/publicação de clipes, integrações Telegram).
- `packages/clipador-core`: regras de domínio compartilhadas (monitoramento, regras de agrupamento de clipes, pipelines de exportação, abstrações de integrações).
- `packages/clip-editor`: integração do módulo `clip-editor` atual como recurso disponível inicialmente apenas para admins.

## Perfis e Acessos
- **Admin interno** (fase 1): acesso completo à plataforma web, ferramentas de edição, configuração de monitoramentos e integrações.
- **Creators/convidados** (fase 2): acesso limitado a dashboards, downloads de clipes e uso guiado do editor.
- **Visitante landing**: navega no site institucional; sem login. Possível acesso a formulários e materiais.

## Fluxos Centrais
- **Monitoramento Twitch/Web**: 
  - execução recorrente (jobs) para capturar clipes, validar se são ao vivo, agrupar por bursts e notificar.
  - disponibilizar alertas e dashboards no app web, incluindo canais gratuitos/pagos existentes.
- Modo de credenciais configurável por streamer:
  - `clipador_only`: usa credenciais centrais.
  - `clipador_trial`: usa credenciais centrais até a data de trial expirar, migrando para credenciais do cliente.
  - `client`: sempre com credenciais do cliente.
- **Gerenciamento de Clipes**:
  - listagem, filtro, download, exportação social e edição (usar recursos do `clip-editor`).
  - pipeline de publicação social (Instagram/TikTok) como feature opcional/flag.
- **Editor de Clipes (Admin)**:
  - interface restrita para montar layouts verticais, gerar legendas e títulos via IA.
  - expor API/serviço que permita futuramente liberar o recurso no app web.
- **Landing**:
  - páginas estáticas (home, features, pricing, contato).
  - integração com ferramentas externas (ex.: formulários, analytics).
  - consumir `/public/clips` para exibir lista de highlights do canal gratuito.

## Status Atual (Out/2025)
- Autenticação web via `/auth/login` com JWT e tela de login dedicada.
- Dashboard react consulta `/clips/bursts/recent` e presets de monitoramento; streams monitoradas gerenciadas via `/streams`.
- Backend expõe repositórios e modelos (`users`, `streamers`, `clips`) com migrations Alembic e script para criar admins.
- Falta implementar ingestão contínua de clipes da Twitch, pipeline do editor e publicação social.

## Integrações Externas
- Twitch API (stream/clips/VODs).
- Telegram Bot API e Telethon (alertas, sessões).
- FFmpeg (processamento de vídeo).
- OpenAI ou outro provedor IA (títulos, legendas) – validar políticas de uso.
- Armazenamento de mídia (S3/R2) para exports e assets gerados.
- Banco de dados PostgreSQL (já usado no bot).

## Requisitos Não Funcionais
- Observabilidade: logs estruturados, métricas básicas (jobs, filas, erros).
- Escalabilidade: permitir separar workers e API (containers distintos).
- Infra de jobs: Celery + Redis para ingestão periódica (tolerância a falhas, monitoramento de queue) e possibilidade de expandir para editor/publicação.
- Segurança: autenticação com JWT/SSO para painel web; limitar uploads; CORS configurável; proteção de dados sensíveis.
- Deploy: pipelines CI/CD separados (web, landing, backend). Suporte inicial a Docker e scripts `make`/`just`.
- Testabilidade: manter suites de testes (pytest, vitest) e fixtures para replicar fluxos do bot.

## Próximos Passos
1. Detalhar telas do app web (wireframes/descrições) com foco no fluxo do admin.
2. Definir contratos da API (endpoints, payloads, eventos WS) com base nos fluxos acima.
3. Criar estrutura inicial do repositório (dirs, ferramentas de build/test, templates de CI).
4. Planejar migração incremental do código existente (priorizar regras de domínio e pipelines críticos).
