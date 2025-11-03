import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";

import { loginRequest, logoutRequest, refreshSession } from "../api";

type SessionState = {
  accessToken: string;
  refreshToken: string;
};

type AuthContextValue = {
  token: string | null;
  loading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  refresh: () => Promise<boolean>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const SESSION_KEY = "clipador:auth-session";
const REFRESH_WINDOW_MS = 60_000;

const isBrowser = typeof window !== "undefined";

function decodeExpiration(token: string): number | null {
  const parts = token.split(".");
  if (parts.length !== 3) {
    return null;
  }

  try {
    let payload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    if (payload.length % 4 !== 0) {
      payload = payload.padEnd(payload.length + (4 - (payload.length % 4)), "=");
    }
    const json = atob(payload);
    const data = JSON.parse(json) as { exp?: number };
    return typeof data.exp === "number" ? data.exp : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<SessionState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const refreshInFlight = useRef<Promise<string | null> | null>(null);

  const persistSession = useCallback((value: SessionState | null) => {
    setSession(value);
    if (!isBrowser) {
      return;
    }
    if (value) {
      window.localStorage.setItem(SESSION_KEY, JSON.stringify(value));
    } else {
      window.localStorage.removeItem(SESSION_KEY);
    }
  }, []);

  useEffect(() => {
    if (!isBrowser) {
      return;
    }
    const stored = window.localStorage.getItem(SESSION_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as SessionState;
        persistSession(parsed);
      } catch {
        window.localStorage.removeItem(SESSION_KEY);
      }
    }
  }, [persistSession]);

  const refresh = useCallback(async () => {
    if (!session?.refreshToken) {
      return false;
    }

    if (refreshInFlight.current) {
      const token = await refreshInFlight.current;
      return typeof token === "string" && token.length > 0;
    }

    const task = (async () => {
      try {
        const response = await refreshSession(session.refreshToken);
        const nextSession = {
          accessToken: response.access_token,
          refreshToken: response.refresh_token,
        };
        persistSession(nextSession);
        setError(null);
        return nextSession.accessToken;
      } catch (err) {
        persistSession(null);
        setError(
          err instanceof Error ? err.message : "Sessão expirada. Faça login novamente.",
        );
        return null;
      } finally {
        refreshInFlight.current = null;
      }
    })();

    refreshInFlight.current = task;
    const token = await task;
    return typeof token === "string" && token.length > 0;
  }, [persistSession, session]);

  useEffect(() => {
    if (!session?.accessToken) {
      return;
    }
    const expiration = decodeExpiration(session.accessToken);
    if (!expiration) {
      return;
    }
    const refreshAt = expiration * 1000 - REFRESH_WINDOW_MS;
    const delay = refreshAt - Date.now();

    if (delay <= 0) {
      void refresh();
      return;
    }

    const timeoutId = window.setTimeout(() => {
      void refresh();
    }, delay);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [session, refresh]);

  const login = useCallback(
    async (username: string, password: string) => {
      setLoading(true);
      setError(null);
      try {
        const response = await loginRequest(username, password);
        persistSession({
          accessToken: response.access_token,
          refreshToken: response.refresh_token,
        });
        return true;
      } catch (err) {
        persistSession(null);
        setError(err instanceof Error ? err.message : "Falha na autenticação");
        return false;
      } finally {
        setLoading(false);
      }
    },
    [persistSession],
  );

  const logout = useCallback(async () => {
    try {
      await logoutRequest(session?.accessToken ?? null);
    } catch {
      // Ignorar erros de logout server-side; apenas limpar localmente.
    } finally {
      persistSession(null);
    }
  }, [persistSession, session]);

  const value = useMemo(
    () => ({
      token: session?.accessToken ?? null,
      loading,
      error,
      login,
      logout,
      refresh,
    }),
    [session, loading, error, login, logout, refresh],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
