# Clipador – Fluxos e Telas Prioritárias

## Personas (Fase 1)
- **Admin interno**: controla monitoramentos, acompanha alertas, processa clipes e usa o editor avançado.

## Navegação Principal (Dashboard Web)
- **Login** (Admin)
  - Autenticação por email + senha ou SSO interno.
  - Redireciona para Dashboard após sucesso.
- **Dashboard / Overview**
  - Cards com status dos monitoramentos ativos (canal, streamer, status online/offline, últimos clipes).
  - Timeline de alertas recentes (agrupados por burst).
  - Atalhos para ações rápidas (abrir editor, ver clipes do dia, configurar monitor).
- **Streams Monitoradas**
  - Lista tabelada com filtros (status online, plataforma, categoria).
  - Ações: editar presets, pausar/resumir monitoramento, visualizar histórico.
  - Detalhe do stream: métricas atuais, histórico de clipes, notas internas.
- **Clipes**
  - Visão feed/galeria; filtros por data, streamer, status de processamento.
  - Cada cartão mostra thumbnail, título, duração, viewers, tags.
  - Ações: assistir clipe, baixar, enviar para editor, marcar como “pronto”, exportar para redes.
- **Alertas**
  - Históricos agrupados: burst detectado → lista de clipes incluídos.
  - Exibir regras usadas (intervalo, mínimo de clipes).
  - Permitir marcar burst como resolvido/irrelevante.
- **Editor (Clip Editor Admin)**
  - Upload ou seleção de clipe existente.
  - Configuração de layout (full/dividido/auto), crop manual, preview ao vivo.
  - Geração de legendas automáticas + edição manual.
  - Sugestão de títulos com IA (permitir ajustar prompt e ver histórico).
  - Export: fila de renderização, status (em progresso, concluído, falhou), download individual ou lote.
- **Publicação Social**
  - Lista de jobs pendentes/concluídos.
  - Configuração de contas (Instagram, TikTok).
  - Logs/sugestões automáticas de legendas e hashtags.
- **Configurações**
  - Preferências globais (timezone, notificações por email/push).
  - Variáveis por streamer (intervalo de monitoramento, mínimo de clipes, tags).
  - Integrações (chaves API Twitch, OpenAI, storage).
  - Gerenciamento de usuários (quando expandirmos para creators).

## Fluxos Principais
1. **Adicionar Streamer / Monitoramento**
   - Admin abre “Novo monitoramento”.
   - Preenche Twitch handle, presets (método de agrupamento, viewers mínimos).
   - Sistema inicia captura automática e exibe status em tempo real.
2. **Avaliar Burst de Clipes**
   - Backend detecta burst → registra em DB → emite notificação em tempo real.
   - Dashboard mostra alerta; admin abre e revisa clipes incluídos.
   - Admin escolhe clipes para edição/descarta.
3. **Processar Clipe no Editor**
   - Admin seleciona clipe → “Enviar para editor”.
   - Editor permite ajustar layout, legendas, títulos → salva configurações.
   - Submete export → worker processa → resultado aparece em fila.
4. **Publicar / Compartilhar**
   - Após export, admin pode baixar ou acionar publicação social.
   - Seleciona plataforma, legenda sugerida, agenda ou publica imediatamente.
5. **Gerenciar Histórico**
   - Admin consulta clipes antigos, busca por streamer/data.
   - Pode reprocessar com novos layouts ou duplicar para outros formatos.

## Considerações UI
- Manter componentes reutilizáveis (cards, timelines, modals) compartilhados via pacote UI.
- Preparar layout para inclusão futura de creators (roles), mas esconder se não habilitado.
- Prever toasts/notificações in-app para eventos importantes (burst detectado, export concluído).
- Acessibilidade e responsividade (painéis principais desktop-first, mas com suporte tablet).
