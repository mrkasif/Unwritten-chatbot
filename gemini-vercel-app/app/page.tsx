"use client";

import { useCallback, useEffect, useRef, useState } from "react";

type Role = "user" | "assistant";
type Message = { role: Role; content: string };

const MODELS = ["gemini-2.5-flash", "gemini-2.5-pro"];

function Avatar({ emoji }: { emoji: string }) {
  return (
    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-borderline bg-surface text-lg">
      {emoji}
    </div>
  );
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const [apiKey, setApiKey] = useState("");
  const [model, setModel] = useState(MODELS[0]);
  const [temperature, setTemperature] = useState(0.7);
  const [systemPrompt, setSystemPrompt] = useState(
    "You are a helpful, expert AI collaborator.",
  );

  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    try {
      const saved = localStorage.getItem("unwritten-messages");
      if (saved) setMessages(JSON.parse(saved));
    } catch {
      // ignore corrupted local state
    }
  }, []);

  useEffect(() => {
    localStorage.setItem("unwritten-messages", JSON.stringify(messages));
  }, [messages]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const clearChat = useCallback(() => setMessages([]), []);

  const send = useCallback(async () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");

    const history = messages.map(({ role, content }) => ({ role, content }));

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);
    setLoading(true);

    const payload = {
      message: text,
      history,
      api_key: apiKey,
      model,
      temperature,
      system_instruction: systemPrompt,
    };

    let acc = "";
    try {
      const res = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok || !res.body) throw new Error(`Request failed: ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        acc += decoder.decode(value, { stream: true });
        setMessages((prev) => {
          const next = [...prev];
          next[next.length - 1] = { role: "assistant", content: acc };
          return next;
        });
      }
    } catch (err: unknown) {
      const detail =
        err instanceof Error ? err.message : "Unknown connection error";
      setMessages((prev) => {
        const next = [...prev];
        next[next.length - 1] = {
          role: "assistant",
          content: `Connection failed: ${detail}`,
        };
        return next;
      });
    } finally {
      setLoading(false);
    }
  }, [input, loading, messages, apiKey, model, temperature, systemPrompt]);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-bg text-[#E6EDF3]">
      {sidebarOpen && (
        <aside className="flex w-72 shrink-0 flex-col gap-5 overflow-y-auto border-r border-borderline bg-surface p-4">
          <div className="text-lg font-bold text-white">⚡ Settings</div>

          <div>
            <label className="mb-1 block text-xs font-medium text-muted">
              Gemini API Key
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Leave blank to use env key"
              className="w-full rounded-md border border-borderline bg-bg px-3 py-2 text-sm outline-none placeholder:text-muted/60 focus:border-accent"
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-muted">
              Model
            </label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full rounded-md border border-borderline bg-bg px-3 py-2 text-sm outline-none focus:border-accent"
            >
              {MODELS.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 flex items-center justify-between text-xs font-medium text-muted">
              <span>Temperature</span>
              <span className="text-white">{temperature.toFixed(2)}</span>
            </label>
            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={temperature}
              onChange={(e) => setTemperature(Number(e.target.value))}
              className="w-full accent-[#58A6FF]"
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-muted">
              System Persona
            </label>
            <textarea
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              rows={5}
              className="w-full resize-none rounded-md border border-borderline bg-bg px-3 py-2 text-sm outline-none placeholder:text-muted/60 focus:border-accent"
            />
          </div>

          <button
            onClick={clearChat}
            className="rounded-lg border border-borderline bg-[#21262D] px-3 py-2 text-sm text-white transition-colors hover:border-accent hover:text-accent"
          >
            🗑️ Clear conversation
          </button>
        </aside>
      )}

      <main className="relative flex flex-1 flex-col">
        <header className="flex items-center gap-3 border-b border-borderline px-4 py-3">
          <button
            onClick={() => setSidebarOpen((v) => !v)}
            className="rounded-md border border-borderline bg-surface px-3 py-1.5 text-sm hover:border-accent"
          >
            ⚙️
          </button>
          <h1 className="text-lg font-semibold text-white">✨ Unwritten</h1>
        </header>

        <div className="mx-auto w-full max-w-3xl flex-1 space-y-4 overflow-y-auto px-4 py-6">
          {messages.length === 0 && !loading && (
            <p className="pt-16 text-center text-muted">
              Ask anything to begin your conversation.
            </p>
          )}

          {messages.map((m, i) => {
            const isUser = m.role === "user";
            const isLastAssistant =
              m.role === "assistant" && loading && i === messages.length - 1;
            return (
              <div
                key={i}
                className={`flex items-start gap-3 ${isUser ? "justify-end" : ""}`}
              >
                {!isUser && <Avatar emoji="🤖" />}
                <div
                  className={`bubble whitespace-pre-wrap ${
                    isUser ? "bubble-user text-right" : "bubble-assistant"
                  }`}
                >
                  {m.content ||
                    (isLastAssistant ? <span className="text-accent">▌</span> : "")}
                  {m.content && isLastAssistant ? <span className="text-accent">▌</span> : null}
                </div>
                {isUser && <Avatar emoji="👤" />}
              </div>
            );
          })}
          <div ref={endRef} />
        </div>

        <div className="border-t border-borderline bg-bg/80 p-4 backdrop-blur">
          <div className="mx-auto flex w-full max-w-3xl items-center gap-2 rounded-2xl border border-borderline bg-surface/90 p-2 transition-colors focus-within:border-accent focus-within:shadow-[0_0_0_2px_rgba(88,166,255,0.25)]">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send();
                }
              }}
              disabled={loading}
              placeholder="Ask anything..."
              className="flex-1 bg-transparent px-3 py-2 text-sm outline-none placeholder:text-muted"
            />
            <button
              onClick={send}
              disabled={loading || !input.trim()}
              className="rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-bg transition-opacity hover:opacity-90 disabled:opacity-40"
            >
              {loading ? "…" : "Send"}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}