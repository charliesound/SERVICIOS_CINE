import { useState, type FormEvent } from "react";

type LoginScreenProps = {
  loading: boolean;
  error: string;
  onLogin: (email: string, password: string) => Promise<void>;
};

export default function LoginScreen({ loading, error, onLogin }: LoginScreenProps) {
  const [email, setEmail] = useState("admin@cine.local");
  const [password, setPassword] = useState("admin1234");
  const [localError, setLocalError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLocalError("");

    const normalizedEmail = email.trim();
    const normalizedPassword = password.trim();
    if (!normalizedEmail || !normalizedPassword) {
      setLocalError("Email y password son obligatorios.");
      return;
    }

    try {
      await onLogin(normalizedEmail, normalizedPassword);
    } catch {
      // Error surfaced by parent store.
    }
  }

  const message = error || localError;

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 px-4">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
        <div className="text-xs uppercase tracking-[0.2em] text-slate-400">CINE AI PLATFORM</div>
        <h1 className="mt-2 text-2xl font-semibold text-white">Iniciar sesion</h1>
        <p className="mt-1 text-sm text-slate-400">Acceso con rol y sesión Bearer.</p>

        {message ? (
          <div className="mt-4 rounded-lg border border-red-800 bg-red-950/60 px-3 py-2 text-sm text-red-200">
            {message}
          </div>
        ) : null}

        <form className="mt-5 space-y-4" onSubmit={(event) => void handleSubmit(event)}>
          <label className="block">
            <span className="mb-1 block text-sm text-slate-300">Email</span>
            <input
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              type="email"
              autoComplete="email"
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 outline-none focus:border-cyan-500"
            />
          </label>

          <label className="block">
            <span className="mb-1 block text-sm text-slate-300">Password</span>
            <input
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              autoComplete="current-password"
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 outline-none focus:border-cyan-500"
            />
          </label>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Validando..." : "Entrar"}
          </button>
        </form>
      </div>
    </div>
  );
}
