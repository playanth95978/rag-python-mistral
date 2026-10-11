export async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`/api/v1${path}`, options);
  } catch (error) {
    if (error.name === "AbortError") throw error;
    throw new Error("Connexion impossible. Vérifiez que FastAPI est démarré.");
  }
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(
      typeof data?.detail === "string"
        ? data.detail
        : "Requête invalide ou service indisponible.",
    );
  }
  if (!data) throw new Error("Réponse du serveur invalide.");
  return data;
}

export async function sendMessages(messages, signal) {
  const data = await request("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
    signal,
  });
  if (typeof data.answer !== "string")
    throw new Error("Réponse Mistral invalide.");
  return data;
}

export const vespaApi = {
  collections: (signal) => request("/admin/vespa/collections", { signal }),
  documents: (collection, query, offset, signal) =>
    request(
      `/admin/vespa/${collection}/documents?${new URLSearchParams({ query, offset, limit: 20 })}`,
      { signal },
    ),
  detail: (collection, id, signal) =>
    request(`/admin/vespa/${collection}/documents/${encodeURIComponent(id)}`, {
      signal,
    }),
};
