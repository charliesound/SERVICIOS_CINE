export type AuthRole = "admin" | "editor" | "reviewer" | "viewer";

export type AuthUser = {
  user_id: string;
  email: string;
  role: AuthRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type AuthLoginResponse = {
  ok: boolean;
  access_token: string;
  token_type: "bearer";
  user: AuthUser;
};

export type AuthMeResponse = {
  ok: boolean;
  user: AuthUser;
};
