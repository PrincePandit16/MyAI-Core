import { FormEvent, useState } from "react";
import api, { getApiErrorMessage } from "../api/client";

type ChatProps = {
  onLogout: () => void;
};

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

export default function Chat({ onLogout }: ChatProps) {
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState("");
  const [sessionId] = useState(() => crypto.randomUUID());

  async function sendMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedPrompt = prompt.trim();
    if (!trimmedPrompt || isSending) return;

    setError("");
    setIsSending(true);
    setMessages((current) => [
      ...current,
      { id: crypto.randomUUID(), role: "user", content: trimmedPrompt },
    ]);
    setPrompt("");

    try {
      const response = await api.post<{ response: string }>("/api/chat", {
        session_id: sessionId,
        prompt: trimmedPrompt,
      });
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.data.response,
        },
      ]);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "Could not reach the assistant API."));
    } finally {
      setIsSending(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-8 text-slate-900 sm:px-6">
      <section className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-3xl flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <header className="flex items-center justify-between gap-4 border-b border-slate-200 px-5 py-4 sm:px-7">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-indigo-600">
              Personal AI Assistant
            </p>
            <h1 className="mt-1 text-xl font-semibold">Chat</h1>
          </div>
          <button
            className="rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
            onClick={onLogout}
            type="button"
          >
            Sign out
          </button>
        </header>

        <div className="flex flex-1 flex-col gap-4 overflow-y-auto p-5 sm:p-7">
          {messages.length === 0 ? (
            <div className="m-auto max-w-md text-center">
              <h2 className="text-lg font-medium">What can I help with?</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Send a message to chat with the configured language model.
                Messages are not saved after this session.
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                className={`max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-6 ${
                  message.role === "user"
                    ? "ml-auto bg-indigo-600 text-white"
                    : "mr-auto border border-slate-200 bg-slate-50 text-slate-800"
                }`}
                key={message.id}
              >
                <p className="mb-1 text-xs font-semibold opacity-70">
                  {message.role === "user" ? "You" : "Assistant"}
                </p>
                {message.content}
              </div>
            ))
          )}
          {isSending && (
            <p className="mr-auto text-sm text-slate-500" role="status">
              Waiting for the API…
            </p>
          )}
          {error && (
            <p
              className="rounded-lg bg-rose-50 px-4 py-3 text-sm text-rose-700"
              role="alert"
            >
              Message could not be sent: {error}
            </p>
          )}
        </div>

        <form
          className="border-t border-slate-200 bg-white p-4 sm:p-5"
          onSubmit={sendMessage}
        >
          <label className="sr-only" htmlFor="prompt">
            Message
          </label>
          <div className="flex gap-3">
            <input
              autoComplete="off"
              className="min-w-0 flex-1 rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
              id="prompt"
              onChange={(event) => setPrompt(event.target.value)}
              placeholder="Type a message…"
              value={prompt}
            />
            <button
              className="rounded-xl bg-indigo-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-300"
              disabled={!prompt.trim() || isSending}
              type="submit"
            >
              {isSending ? "Sending…" : "Send"}
            </button>
          </div>
        </form>
      </section>
    </main>
  );
}
