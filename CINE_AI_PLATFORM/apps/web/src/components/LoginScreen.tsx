import { useState, type FormEvent } from "react";

type LoginScreenProps = {
  loading: boolean;
  error: string;
  onLogin: (email: string, password: string) => Promise<void>;
};

export default function LoginScreen({ loading, error, onLogin }: LoginScreenProps) {
  const [email, setEmail] = useState("admin@cine.local");
  const [password, setPassword] = useState("CHANGE_ME");
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
    <div className="min-h-screen bg-[#fafafa] px-4 py-10 text-gray-900 md:px-6">
      <div className="mx-auto flex min-h-[calc(100vh-5rem)] max-w-5xl items-center justify-center">
        <div className="grid w-full max-w-4xl overflow-hidden rounded-[28px] border border-gray-200 bg-white shadow-[0_24px_80px_rgba(15,23,42,0.08)] md:grid-cols-[1.1fr_0.9fr]">
          <div className="hidden border-r border-gray-200 bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.16),_transparent_42%),linear-gradient(180deg,_#ffffff_0%,_#f8fafc_100%)] p-10 md:flex md:flex-col md:justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.2em] text-gray-500">CINE AI PLATFORM</div>
              <h1 className="mt-4 text-4xl font-semibold tracking-[-0.04em] text-gray-950">Acceso al panel de produccion</h1>
              <p className="mt-4 max-w-md text-sm leading-6 text-gray-600">
                Entra con tu sesion Bearer para continuar con proyectos, escenas y shots desde el dashboard principal.
              </p>
            </div>

            <div className="rounded-2xl border border-gray-200 bg-white/80 p-5 backdrop-blur">
              <div className="text-xs uppercase tracking-[0.18em] text-gray-500">Acceso local</div>
              <div className="mt-3 space-y-2 text-sm text-gray-700">
                <p><span className="font-semibold text-gray-900">Email:</span> admin@cine.local</p>
                <p><span className="font-semibold text-gray-900">Password:</span> CHANGE_ME</p>
              </div>
            </div>
          </div>

          <div className="p-6 sm:p-8 md:p-10">
            <div className="text-xs uppercase tracking-[0.2em] text-gray-500 md:hidden">CINE AI PLATFORM</div>
            <h1 className="mt-2 text-3xl font-semibold tracking-[-0.03em] text-gray-950 md:text-[2rem]">Iniciar sesion</h1>
            <p className="mt-2 text-sm text-gray-600">Acceso con rol y sesion Bearer.</p>

            {message ? (
              <div className="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {message}
              </div>
            ) : null}

            <form className="mt-6 space-y-5" onSubmit={(event) => void handleSubmit(event)}>
              <label className="block">
                <span className="mb-1.5 block text-sm font-medium text-gray-700">Email</span>
                <input
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  type="email"
                  autoComplete="email"
                  className="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
                />
              </label>

              <label className="block">
                <span className="mb-1.5 block text-sm font-medium text-gray-700">Password</span>
                <input
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  type="password"
                  autoComplete="current-password"
                  className="w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
                />
              </label>

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-xl bg-gray-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? "Validando..." : "Entrar"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
