import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import api, { getApiErrorMessage } from "../api/client";

type AuthMode = "login" | "register";

type AuthFormProps = {
  mode: AuthMode;
  onAuthenticated: () => void;
};

type TokenResponse = {
  access_token: string;
  token_type: string;
};

export default function AuthForm({ mode, onAuthenticated }: AuthFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const isRegister = mode === "register";

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const credentials = { email: email.trim(), password };
      if (isRegister) {
        await api.post("/auth/register", credentials);
      }
      const response = await api.post<TokenResponse>("/auth/login", credentials);
      onAuthenticated();
    } catch (requestError) {
      setError(
        getApiErrorMessage(
          requestError,
          isRegister ? "Could not create your account." : "Could not sign in.",
        ),
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-12">
      <section className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-sm sm:p-10">
        <Link
          className="text-sm font-semibold uppercase tracking-[0.16em] text-indigo-600"
          to="/"
        >
          Personal AI Assistant
        </Link>
        <h1 className="mt-8 text-2xl font-semibold text-slate-900">
          {isRegister ? "Create your account" : "Welcome back"}
        </h1>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          {isRegister
            ? "Sign up to start chatting with your assistant."
            : "Sign in to continue to your assistant."}
        </p>

        <form className="mt-8 space-y-5" onSubmit={submit}>
          <div>
            <label
              className="mb-2 block text-sm font-medium text-slate-700"
              htmlFor={`${mode}-email`}
            >
              Email
            </label>
            <input
              autoComplete="email"
              className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
              id={`${mode}-email`}
              onChange={(event) => setEmail(event.target.value)}
              required
              type="email"
              value={email}
            />
          </div>
          <div>
            <label
              className="mb-2 block text-sm font-medium text-slate-700"
              htmlFor={`${mode}-password`}
            >
              Password
            </label>
            <input
              autoComplete={isRegister ? "new-password" : "current-password"}
              className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
              id={`${mode}-password`}
              minLength={8}
              onChange={(event) => setPassword(event.target.value)}
              required
              type="password"
              value={password}
            />
            {isRegister && (
              <p className="mt-2 text-xs text-slate-500">
                Use at least 8 characters.
              </p>
            )}
          </div>
          {error && (
            <p className="rounded-lg bg-rose-50 px-4 py-3 text-sm text-rose-700" role="alert">
              {error}
            </p>
          )}
          <button
            className="w-full rounded-xl bg-indigo-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-300"
            disabled={isSubmitting}
            type="submit"
          >
            {isSubmitting
              ? isRegister
                ? "Creating account…"
                : "Signing in…"
              : isRegister
                ? "Create account"
                : "Sign in"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-600">
          {isRegister ? "Already have an account?" : "New here?"}{" "}
          <Link
            className="font-medium text-indigo-600 hover:text-indigo-700"
            to={isRegister ? "/login" : "/register"}
          >
            {isRegister ? "Sign in" : "Create an account"}
          </Link>
        </p>
      </section>
    </main>
  );
}
