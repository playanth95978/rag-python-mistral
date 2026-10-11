import { useCallback, useEffect, useRef, useState } from "react";
import {
  createConversation,
  readConversations,
  STORAGE_KEY,
} from "../lib/conversations";
import { sendMessages } from "../lib/api";

export default function useConversations() {
  const [chats, setChats] = useState(() => {
    const saved = readConversations();
    return saved.length ? saved : [createConversation()];
  });
  const [activeId, setActiveId] = useState(() => chats[0].id);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const sending = useRef(false);
  const active = chats.find((chat) => chat.id === activeId) || chats[0];

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(chats));
    } catch {
      setError(
        "Stockage local plein. Les nouvelles conversations ne pourront pas être sauvegardées.",
      );
    }
  }, [chats]);

  const newChat = useCallback(() => {
    if (sending.current) return;
    const chat = createConversation();
    setChats((old) => [chat, ...old]);
    setActiveId(chat.id);
    setError("");
  }, []);

  function selectChat(id) {
    if (!sending.current) {
      setActiveId(id);
      setError("");
    }
  }
  function deleteChat(id) {
    if (sending.current) return;
    const remaining = chats.filter((chat) => chat.id !== id);
    const next = remaining.length ? remaining : [createConversation()];
    setChats(next);
    if (active.id === id) setActiveId(next[0].id);
  }

  async function send(text) {
    if (sending.current || !text.trim()) return false;
    if (active.messages.length >= 98) {
      setError(
        "Ouvrez un nouveau chat pour continuer cette conversation devenue longue.",
      );
      return false;
    }
    const id = active.id;
    const previous = active.messages;
    const messages = [...previous, { role: "user", content: text.trim() }];
    sending.current = true;
    setBusy(true);
    setError("");
    setChats((old) =>
      old.map((chat) =>
        chat.id === id
          ? {
              ...chat,
              messages,
              title: previous.length ? chat.title : text.trim().slice(0, 45),
            }
          : chat,
      ),
    );
    try {
      const data = await sendMessages(messages);
      setChats((old) =>
        old.map((chat) =>
          chat.id === id
            ? {
                ...chat,
                messages: [
                  ...messages,
                  { role: "assistant", content: data.answer },
                ],
              }
            : chat,
        ),
      );
      return true;
    } catch (err) {
      setChats((old) =>
        old.map((chat) =>
          chat.id === id ? { ...chat, messages: previous } : chat,
        ),
      );
      setError(err.message);
      return false;
    } finally {
      sending.current = false;
      setBusy(false);
    }
  }

  return { chats, active, busy, error, newChat, selectChat, deleteChat, send };
}
