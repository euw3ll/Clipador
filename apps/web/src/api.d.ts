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
export declare function loginRequest(username: string, password: string): Promise<LoginResponse>;
export declare function fetchRecentBursts(token: string, sinceMinutes?: number): Promise<BurstPayload[]>;
export declare function resolveMonitoring(token: string, mode?: string, overrides?: Record<string, unknown>): Promise<MonitoringResolution>;
export declare function fetchChannelConfig(token: string): Promise<ChannelConfig>;
export declare function updateChannelConfig(token: string, payload: ChannelConfigUpdate): Promise<ChannelConfig>;
export declare function attachChannelStreamer(token: string, payload: ChannelStreamerAttach): Promise<ChannelConfig>;
export declare function detachChannelStreamer(token: string, streamerId: number): Promise<ChannelConfig>;
export declare function reorderChannelStreamers(token: string, streamerIds: number[]): Promise<ChannelConfig>;
export declare function fetchDeliveryHistory(token: string, limit?: number): Promise<DeliveryHistory>;
export declare function refreshSession(refreshToken: string): Promise<LoginResponse>;
export declare function logoutRequest(token: string | null): Promise<void>;
