import { api } from "./api";
import type { AuthLoginResponse, AuthMeResponse } from "../types/auth";

export async function loginAuth(email: string, password: string): Promise<AuthLoginResponse> {
  const response = await api.post<AuthLoginResponse>("/api/auth/login", {
    email,
    password,
  });
  return response.data;
}

export async function meAuth(): Promise<AuthMeResponse> {
  const response = await api.get<AuthMeResponse>("/api/auth/me");
  return response.data;
}

export async function logoutAuth(): Promise<void> {
  await api.post("/api/auth/logout");
}
