import { useState } from "react";
import { Check, Copy } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import Logo from "./Logo";

export default function Message({ message }) {
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState("");
  if (message.role === "user")
    return (
      <article className="mb-8 ml-auto w-fit max-w-[88%] rounded-[20px_20px_4px_20px] bg-[#f0ede6] px-5 py-3 text-[15px] leading-7 whitespace-pre-wrap break-words">
        {message.content}
      </article>
    );
  async function copy() {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
    } catch {
      setCopyError("Copie indisponible");
    }
  }
  return (
    <article className="mb-9">
      <div className="mb-3 flex items-center gap-2.5 text-xs font-semibold">
        <Logo className="h-4 w-5" />
        Mistral
      </div>
      <div className="markdown">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{ img: ({ alt }) => <span>[Image : {alt}]</span> }}
        >
          {message.content}
        </ReactMarkdown>
      </div>
      <button
        onClick={copy}
        className="mt-3 flex items-center gap-1.5 text-xs text-muted hover:text-ink"
      >
        {copied ? <Check size={13} /> : <Copy size={13} />}
        {copyError || (copied ? "Copié" : "Copier")}
      </button>
    </article>
  );
}
