export const STORAGE_KEY = "mistral-local-chats-v1";

export function createConversation() {
  return { id: crypto.randomUUID(), title: "Nouveau chat", messages: [] };
}

export function readConversations() {
  try {
    const data = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    if (!Array.isArray(data)) return [];
    return data.filter(
      (chat) =>
        chat &&
        typeof chat.id === "string" &&
        typeof chat.title === "string" &&
        Array.isArray(chat.messages) &&
        chat.messages.every(
          (message) =>
            ["user", "assistant"].includes(message.role) &&
            typeof message.content === "string",
        ),
    );
  } catch {
    return [];
  }
}
