import { useEffect, useRef, useState } from "react";
import { ArrowUp, Code2, Lightbulb, PenLine, Sparkles } from "lucide-react";
import Logo from "../components/Logo";
import Message from "../components/Message";
import ErrorBanner from "../components/ErrorBanner";

const suggestions = [
  [
    PenLine,
    "Rédiger un texte",
    "Aide-moi à rédiger un email professionnel clair et concis.",
  ],
  [
    Sparkles,
    "Comprendre un sujet",
    "Explique-moi simplement comment fonctionne un modèle de langage.",
  ],
  [
    Lightbulb,
    "Trouver l’inspiration",
    "Donne-moi cinq idées originales pour un projet Python utile.",
  ],
  [Code2, "Écrire du code", "Aide-moi à écrire une API FastAPI en Python."],
];

export default function ChatPage({ conversations }) {
  const { active, busy, error, send } = conversations;
  const [prompt, setPrompt] = useState("");
  const textarea = useRef(null);
  const scroll = useRef(null);
  useEffect(() => {
    document.title = "Le Chat · Mistral";
  }, []);
  useEffect(() => {
    setPrompt("");
    textarea.current?.focus();
  }, [active.id]);
  useEffect(() => {
    if (scroll.current) scroll.current.scrollTop = scroll.current.scrollHeight;
  }, [active.messages, busy]);
  useEffect(() => {
    if (textarea.current) {
      textarea.current.style.height = "auto";
      textarea.current.style.height = `${Math.min(textarea.current.scrollHeight, 180)}px`;
    }
  }, [prompt]);
  async function submit(event) {
    event.preventDefault();
    const text = prompt.trim();
    if (!text || busy) return;
    setPrompt("");
    if (!(await send(text))) setPrompt(text);
    requestAnimationFrame(() => textarea.current?.focus());
  }
  return (
    <div className="flex min-h-0 flex-1 flex-col">
      {active.messages.length ? (
        <section
          ref={scroll}
          className="min-h-0 flex-1 overflow-y-auto px-5 pt-7 md:px-10"
          aria-label="Messages"
          aria-live="polite"
        >
          <div className="mx-auto max-w-190">
            {active.messages.map((message, index) => (
              <Message key={`${active.id}-${index}`} message={message} />
            ))}
            {busy && (
              <p className="mb-8 flex items-center gap-2 text-sm text-muted">
                <span className="size-2 animate-pulse rounded-full bg-accent" />
                Mistral réfléchit…
              </p>
            )}
          </div>
        </section>
      ) : (
        <section className="flex min-h-0 flex-1 items-center justify-center overflow-y-auto px-5 py-8 text-center">
          <div className="max-w-3xl">
            <Logo className="mx-auto mb-7 h-11 w-14" />
            <h1 className="text-[28px] font-medium tracking-[-1.2px] sm:text-4xl">
              Comment puis-je vous aider ?
            </h1>
            <p className="mt-4 text-sm text-muted">
              Une idée, une question, un projet. On commence ?
            </p>
            <div className="mt-8 flex flex-wrap justify-center gap-2.5">
              {suggestions.map(([Icon, label, text]) => (
                <button
                  key={label}
                  className="button px-4 py-3 text-xs text-muted"
                  onClick={() => {
                    setPrompt(text);
                    textarea.current?.focus();
                  }}
                >
                  <Icon size={16} className="text-accent" />
                  {label}
                </button>
              ))}
            </div>
          </div>
        </section>
      )}
      <div className="mx-auto w-full max-w-200 px-4 pb-4 sm:px-6">
        <ErrorBanner>{error}</ErrorBanner>
        <form
          onSubmit={submit}
          className="rounded-[20px] border border-[#dbd5cb] bg-white p-4 shadow-[0_4px_20px_#28201705] focus-within:border-[#aea495] sm:p-5"
        >
          <textarea
            ref={textarea}
            disabled={busy}
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            onKeyDown={(event) => {
              if (
                event.key === "Enter" &&
                !event.shiftKey &&
                !event.nativeEvent.isComposing
              ) {
                event.preventDefault();
                event.currentTarget.form.requestSubmit();
              }
            }}
            rows={1}
            maxLength={32000}
            required
            aria-label="Votre message"
            placeholder="Demandez ce que vous voulez…"
            className="block max-h-45 min-h-9 w-full resize-none bg-transparent text-[15px] leading-7 outline-none placeholder:text-[#a2998d] focus-visible:outline-none"
          />
          <div className="mt-3 flex items-center justify-between">
            <span className="text-[11px] text-muted">Mistral Large 4</span>
            <button
              disabled={busy || !prompt.trim()}
              type="submit"
              aria-label="Envoyer le message"
              className="flex size-9 items-center justify-center rounded-xl bg-ink text-white hover:bg-black"
            >
              <ArrowUp size={22} />
            </button>
          </div>
        </form>
        <p className="mt-3 text-center text-[10px] text-muted">
          L’IA peut se tromper. Vérifiez les informations importantes.
        </p>
      </div>
    </div>
  );
}
