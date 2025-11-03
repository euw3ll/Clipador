export interface BurstClip {
  id: string;
  created_at: string;
  viewer_count: number;
  video_id?: string | null;
  streamer_name?: string | null;
  streamer_external_id?: string | null;
}

export interface BurstPayload {
  inicio_iso: string;
  fim: string;
  clipes: BurstClip[];
}

export interface MonitoringResolution {
  intervalo_segundos: number;
  min_clipes: number;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface ChannelStreamerStatus {
  status?: string | null;
  last_seen?: string | null;
  last_notified?: string | null;
}

export interface ChannelStreamer {
  id: number;
  streamer_id: number;
  twitch_user_id: string;
  display_name: string;
  avatar_url: string | null;
  order_index: number;
  label: string | null;
  monitor_interval_seconds: number;
  monitor_min_clips: number;
  status?: ChannelStreamerStatus | null;
}

export interface ChannelConfig {
  monitor_mode: string;
  partner_mode: string;
  clipador_chefe_username: string | null;
  manual_min_clips: number | null;
  manual_interval_seconds: number | null;
  manual_min_clips_vod: number | null;
  notify_online: boolean;
  public_share_enabled: boolean;
  public_description: string | null;
  slots_base: number;
  slots_total: number;
  slots_used: number;
  slots_remaining: number;
  streamers: ChannelStreamer[];
}

export interface ChannelConfigUpdate {
  monitor_mode?: string;
  partner_mode?: string;
  clipador_chefe_username?: string | null;
  manual_min_clips?: number | null;
  manual_interval_seconds?: number | null;
  manual_min_clips_vod?: number | null;
  notify_online?: boolean;
  public_share_enabled?: boolean;
  public_description?: string | null;
  slots_configured?: number | null;
}

export interface ChannelStreamerAttach {
  twitch_user_id: string;
  display_name?: string;
  avatar_url?: string;
  monitor_interval_seconds?: number;
  monitor_min_clips?: number;
  api_mode?: string;
  label?: string;
}

export interface DeliveryRecord {
  clip_external_id: string | null;
  delivered_at: string;
  streamer_display_name: string;
  streamer_twitch_id: string;
  viewer_count?: number | null;
  clip_title?: string | null;
}

export interface DeliveryHistory {
  items: DeliveryRecord[];
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

function buildHeaders(token: string | null, additional: HeadersInit = {}): HeadersInit {
  const headers: HeadersInit = {
    Accept: "application/json",
    ...additional,
  };

  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

export async function loginRequest(username: string, password: string): Promise<LoginResponse> {
  const url = new URL(`/auth/login`, API_BASE_URL);
  const response = await fetch(url, {
    method: "POST",
    headers: buildHeaders(null, { "Content-Type": "application/json" }),
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body?.detail ?? "Credenciais inválidas");
  }

  return response.json();
}

export async function fetchRecentBursts(token: string, sinceMinutes = 60): Promise<BurstPayload[]> {
  const url = new URL(`/clips/bursts/recent`, API_BASE_URL);
  url.searchParams.set("since_minutes", String(sinceMinutes));

  const response = await fetch(url, {
    headers: buildHeaders(token),
  });

  if (!response.ok) {
    throw new Error(`Erro ao buscar bursts: ${response.status}`);
  }

  const body = await response.json();
  return Array.isArray(body.data) ? body.data : [];
}

export async function resolveMonitoring(
  token: string,
  mode = "PADRAO",
  overrides?: Record<string, unknown>,
): Promise<MonitoringResolution> {
  const url = new URL(`/monitoring/resolve`, API_BASE_URL);
  const response = await fetch(url, {
    method: "POST",
    headers: buildHeaders(token, { "Content-Type": "application/json" }),
    body: JSON.stringify({
      modo: mode,
      ...overrides,
    }),
  });

  if (!response.ok) {
    throw new Error(`Erro ao resolver preset: ${response.status}`);
  }

  const body = await response.json();
  return body.data as MonitoringResolution;
}

export async function fetchChannelConfig(token: string): Promise<ChannelConfig> {
  const response = await fetch(new URL(`/config/me`, API_BASE_URL), {
    headers: buildHeaders(token),
  });

  if (!response.ok) {
    throw new Error(`Erro ao carregar configurações: ${response.status}`);
  }

  return response.json();
}

export async function updateChannelConfig(
  token: string,
  payload: ChannelConfigUpdate,
): Promise<ChannelConfig> {
  const response = await fetch(new URL(`/config/me`, API_BASE_URL), {
    method: "PUT",
    headers: buildHeaders(token, { "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body?.detail ?? `Erro ao atualizar configuração: ${response.status}`);
  }

  return response.json();
}

export async function attachChannelStreamer(
  token: string,
  payload: ChannelStreamerAttach,
): Promise<ChannelConfig> {
  const response = await fetch(new URL(`/config/me/streamers`, API_BASE_URL), {
    method: "POST",
    headers: buildHeaders(token, { "Content-Type": "application/json" }),
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body?.detail ?? `Erro ao adicionar streamer: ${response.status}`);
  }

  return response.json();
}

export async function detachChannelStreamer(token: string, streamerId: number): Promise<ChannelConfig> {
  const response = await fetch(new URL(`/config/me/streamers/${streamerId}`, API_BASE_URL), {
    method: "DELETE",
    headers: buildHeaders(token),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body?.detail ?? `Erro ao remover streamer: ${response.status}`);
  }

  return response.json();
}

export async function reorderChannelStreamers(
  token: string,
  streamerIds: number[],
): Promise<ChannelConfig> {
  const response = await fetch(new URL(`/config/me/streamers/reorder`, API_BASE_URL), {
    method: "POST",
    headers: buildHeaders(token, { "Content-Type": "application/json" }),
    body: JSON.stringify({ streamer_ids: streamerIds }),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body?.detail ?? `Erro ao reordenar streamers: ${response.status}`);
  }

  return response.json();
}

export async function fetchDeliveryHistory(token: string, limit = 50): Promise<DeliveryHistory> {
  const url = new URL(`/config/me/history`, API_BASE_URL);
  url.searchParams.set("limit", String(limit));
  const response = await fetch(url, {
    headers: buildHeaders(token),
  });

  if (!response.ok) {
    throw new Error(`Erro ao carregar histórico: ${response.status}`);
  }

  return response.json();
}

export async function refreshSession(refreshToken: string): Promise<LoginResponse> {
  const response = await fetch(new URL(`/auth/refresh`, API_BASE_URL), {
    method: "POST",
    headers: buildHeaders(null, { "Content-Type": "application/json" }),
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body?.detail ?? "Não foi possível atualizar a sessão");
  }

  return response.json();
}

export async function logoutRequest(token: string | null): Promise<void> {
  if (!token) {
    return;
  }

  await fetch(new URL(`/auth/logout`, API_BASE_URL), {
    method: "POST",
    headers: buildHeaders(token),
  });
}
