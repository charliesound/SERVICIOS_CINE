import { create } from "zustand";

import { loginAuth, logoutAuth, meAuth } from "../services/authApi";
import type { AuthRole, AuthUser } from "../types/auth";

const AUTH_TOKEN_KEY = "cine_ai_platform_access_token";

type AuthState = {
  user: AuthUser | null;
  accessToken: string | null;
  sessionReady: boolean;
  sessionLoading: boolean;
  loginError: string;
  hydrateSession: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  clearSession: () => void;
  hasRole: (...roles: AuthRole[]) => boolean;
};

function normalizeErrorMessage(error: unknown): string {
  if (error && typeof error === "object") {
    const maybeResponse = error as {
      response?: { data?: { error?: { message?: unknown } } };
      message?: unknown;
    };
    const message = maybeResponse.response?.data?.error?.message;
    if (typeof message === "string" && message.trim()) {
      return message.trim();
    }
    if (typeof maybeResponse.message === "string" && maybeResponse.message.trim()) {
      return maybeResponse.message.trim();
    }
  }
  return "No se pudo iniciar la sesión";
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  accessToken: null,
  sessionReady: false,
  sessionLoading: false,
  loginError: "",
  hydrateSession: async () => {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    if (!token) {
      set({ user: null, accessToken: null, sessionReady: true, sessionLoading: false });
      return;
    }

    set({ sessionLoading: true, loginError: "" });
    try {
      localStorage.setItem(AUTH_TOKEN_KEY, token);
      const response = await meAuth();
      set({ user: response.user, accessToken: token, sessionReady: true, sessionLoading: false });
    } catch {
      localStorage.removeItem(AUTH_TOKEN_KEY);
      set({ user: null, accessToken: null, sessionReady: true, sessionLoading: false });
    }
  },
  login: async (email: string, password: string) => {
    set({ sessionLoading: true, loginError: "" });
    try {
      const response = await loginAuth(email, password);
      localStorage.setItem(AUTH_TOKEN_KEY, response.access_token);
      set({
        user: response.user,
        accessToken: response.access_token,
        sessionReady: true,
        sessionLoading: false,
        loginError: "",
      });
    } catch (error) {
      localStorage.removeItem(AUTH_TOKEN_KEY);
      set({ user: null, accessToken: null, sessionReady: true, sessionLoading: false, loginError: normalizeErrorMessage(error) });
      throw error;
    }
  },
  logout: async () => {
    try {
      if (localStorage.getItem(AUTH_TOKEN_KEY)) {
        await logoutAuth();
      }
    } catch {
      // Ignore logout errors and clear the local session.
    } finally {
      localStorage.removeItem(AUTH_TOKEN_KEY);
      set({ user: null, accessToken: null, sessionLoading: false, sessionReady: true, loginError: "" });
    }
  },
  clearSession: () => {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    set({ user: null, accessToken: null, sessionReady: true, sessionLoading: false, loginError: "" });
  },
  hasRole: (...roles: AuthRole[]) => {
    const user = get().user;
    if (!user) {
      return false;
    }
    return roles.includes(user.role);
  },
}));
