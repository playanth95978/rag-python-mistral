import { useState } from "react";
import { Braces, FileText, Fingerprint, ScanLine } from "lucide-react";

export default function DocumentDetail({ document, loading }) {
  const [tab, setTab] = useState("Texte");
  if (loading)
    return (
      <p role="status" className="p-8 text-sm text-muted">
        Chargement du document…
      </p>
    );
  if (!document)
    return (
      <div className="flex min-h-90 flex-col items-center justify-center px-8 text-center">
        <ScanLine size={32} strokeWidth={1} className="mb-5 text-[#c9b89f]" />
        <h3 className="text-lg font-medium">Regardez de plus près</h3>
        <p className="mt-3 max-w-70 text-sm leading-6 text-muted">
          Sélectionnez un morceau pour consulter son texte, ses métadonnées et
          son embedding.
        </p>
      </div>
    );
  const fields = document.fields || {};
  const metadata = Object.fromEntries(
    Object.entries(fields).filter(
      ([key]) => key !== "content" && !key.includes("embedding"),
    ),
  );
  if (typeof metadata.metadata === "string") {
    try {
      metadata.metadata = JSON.parse(metadata.metadata);
    } catch {
      /* Keep original metadata. */
    }
  }
  const name = Object.keys(fields).find((key) => key.includes("embedding"));
  const vector = name ? fields[name] : null;
  const values = Array.isArray(vector)
    ? vector
    : vector?.values || vector?.cells || [];
  return (
    <div className="p-6">
      <div className="flex items-center gap-2 text-xs text-muted">
        <FileText size={14} />
        Détail du morceau
      </div>
      <h3 className="mt-3 text-xl font-medium">
        {fields.title || "Sans titre"}
      </h3>
      <p className="mt-2 break-all font-mono text-[10px] leading-5 text-muted">
        {document.id}
      </p>
      <div
        role="tablist"
        aria-label="Vue du document"
        className="mt-6 flex gap-1 border-b border-line"
      >
        {[
          ["Texte", FileText],
          ["Métadonnées", Braces],
          ["Embedding", Fingerprint],
        ].map(([name, Icon]) => (
          <button
            key={name}
            id={`tab-${name}`}
            role="tab"
            aria-selected={tab === name}
            aria-controls="document-panel"
            onClick={() => setTab(name)}
            className={`flex items-center gap-1.5 border-b-2 px-2 py-3 text-xs sm:px-3 ${tab === name ? "border-accent text-orange-700" : "border-transparent text-muted hover:text-ink"}`}
          >
            <Icon size={13} />
            {name}
          </button>
        ))}
      </div>
      <div
        id="document-panel"
        role="tabpanel"
        aria-labelledby={`tab-${tab}`}
        className="mt-5 max-h-110 overflow-y-auto text-sm leading-7"
      >
        {tab === "Texte" && (
          <p className="whitespace-pre-wrap break-words">
            {fields.content || "Texte indisponible."}
          </p>
        )}
        {tab === "Métadonnées" && (
          <pre className="whitespace-pre-wrap break-all font-mono text-xs leading-6">
            {JSON.stringify(metadata, null, 2)}
          </pre>
        )}
        {tab === "Embedding" &&
          (vector ? (
            <>
              <div className="mb-5 rounded-lg bg-panel p-4">
                <div className="text-2xl font-medium">
                  {values.length.toLocaleString("fr-FR")}{" "}
                  <span className="text-xs font-normal text-muted">
                    coordonnées
                  </span>
                </div>
                <p className="mt-2 break-all font-mono text-[10px] text-muted">
                  {vector.type || name}
                </p>
              </div>
              <p className="mb-3 text-xs text-muted">
                Les 16 premières coordonnées du vecteur
              </p>
              <pre className="rounded-lg border border-line p-4 font-mono text-xs leading-6">
                {JSON.stringify(values.slice(0, 16), null, 2)}
              </pre>
            </>
          ) : (
            <p className="text-muted">
              Aucun embedding disponible pour ce morceau.
            </p>
          ))}
      </div>
    </div>
  );
}
