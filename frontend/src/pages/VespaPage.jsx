import { useEffect, useRef, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Database,
  FileText,
  RefreshCw,
  Search,
  ShieldCheck,
} from "lucide-react";
import { vespaApi } from "../lib/api";
import DocumentDetail from "../components/DocumentDetail";
import ErrorBanner from "../components/ErrorBanner";

const names = { cv_user: "CV utilisateurs", job_chunks: "Offres d’emploi" };

export default function VespaPage() {
  const [collection, setCollection] = useState("cv_user");
  const [collections, setCollections] = useState([]);
  const [input, setInput] = useState("");
  const [query, setQuery] = useState("");
  const [offset, setOffset] = useState(0);
  const [refresh, setRefresh] = useState(0);
  const [page, setPage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);
  const [document, setDocument] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const detailRequest = useRef(null);

  useEffect(() => {
    window.document.title = "Vespa · Explorateur";
    return () => detailRequest.current?.abort();
  }, []);
  useEffect(() => {
    const controller = new AbortController();
    detailRequest.current?.abort();
    setSelected(null);
    setDocument(null);
    setDetailLoading(false);
    setError("");
    setLoading(true);
    setPage(null);
    Promise.all([
      vespaApi.collections(controller.signal),
      vespaApi.documents(collection, query, offset, controller.signal),
    ])
      .then(([indexData, pageData]) => {
        setCollections(indexData.collections);
        setPage(pageData);
      })
      .catch((err) => {
        if (err.name !== "AbortError") setError(err.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [collection, query, offset, refresh]);

  function switchCollection(name) {
    setCollection(name);
    setInput("");
    setQuery("");
    setOffset(0);
  }
  async function select(item) {
    detailRequest.current?.abort();
    const controller = new AbortController();
    detailRequest.current = controller;
    setSelected(item.id);
    setDocument(null);
    setDetailLoading(true);
    setError("");
    try {
      const result = await vespaApi.detail(
        collection,
        item.id,
        controller.signal,
      );
      if (!controller.signal.aborted) setDocument(result);
    } catch (err) {
      if (err.name !== "AbortError") setError(err.message);
    } finally {
      if (!controller.signal.aborted) setDetailLoading(false);
    }
  }
  const total = page?.total || 0;
  const items = page?.items || [];
  return (
    <div className="min-h-0 flex-1 overflow-y-auto">
      <div className="mx-auto max-w-7xl px-5 py-7 sm:px-9 lg:px-12">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-medium tracking-[-1px]">
              Vos données, en clair.
            </h1>
            <p className="mt-3 text-sm leading-6 text-muted">
              Explorez les documents et les vecteurs de votre moteur de
              recherche.
            </p>
          </div>
          <button
            className="button shrink-0"
            disabled={loading}
            onClick={() => setRefresh((value) => value + 1)}
            aria-label="Actualiser les collections"
          >
            <RefreshCw size={15} className={loading ? "animate-spin" : ""} />
            <span className="hidden sm:inline">Actualiser</span>
          </button>
        </div>
        <div
          className="mt-8 grid gap-3 sm:grid-cols-2"
          aria-label="Collections"
        >
          {Object.entries(names).map(([name, label]) => {
            const count = collections.find(
              (item) => item.name === name,
            )?.chunks;
            return (
              <button
                key={name}
                aria-pressed={collection === name}
                className={`flex items-center gap-4 rounded-xl border p-5 text-left ${collection === name ? "border-orange-300 bg-orange-50/50" : "border-line bg-white hover:bg-panel"}`}
                onClick={() => switchCollection(name)}
              >
                <div
                  className={`flex size-10 items-center justify-center rounded-lg ${collection === name ? "bg-orange-100 text-orange-700" : "bg-panel text-muted"}`}
                >
                  <Database size={19} />
                </div>
                <div>
                  <p className="text-sm font-medium">{label}</p>
                  <p className="mt-1 font-mono text-[11px] text-muted">
                    {name}
                  </p>
                </div>
                <div className="ml-auto text-right">
                  <strong className="text-2xl font-medium">
                    {count ?? "—"}
                  </strong>
                  <p className="text-[10px] text-muted">morceaux</p>
                </div>
              </button>
            );
          })}
        </div>
        <div className="mt-5 flex flex-wrap items-center gap-x-5 gap-y-2 text-[11px] text-muted">
          <span className="flex items-center gap-1.5">
            <ShieldCheck size={13} />
            Lecture seule
          </span>
          <span>Recherche lexicale</span>
          <span>Aucun appel Mistral</span>
        </div>
        <form
          className="mt-7"
          onSubmit={(event) => {
            event.preventDefault();
            setQuery(input.trim());
            setOffset(0);
            setRefresh((value) => value + 1);
          }}
        >
          <label
            htmlFor="vespa-query"
            className="mb-2 block text-xs font-medium"
          >
            Rechercher dans le contenu
          </label>
          <div className="flex gap-2">
            <div className="flex min-w-0 flex-1 items-center gap-3 rounded-xl border border-line bg-white px-4 focus-within:border-[#aea495]">
              <Search size={17} className="shrink-0 text-muted" />
              <input
                id="vespa-query"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                maxLength={500}
                placeholder="Python, FastAPI, expérience…"
                className="w-full min-w-0 bg-transparent py-3.5 text-sm outline-none placeholder:text-muted focus-visible:outline-none"
              />
            </div>
            <button
              type="submit"
              className="button border-ink bg-ink px-4 text-white hover:bg-black"
            >
              Rechercher
            </button>
          </div>
        </form>
        <ErrorBanner>{error}</ErrorBanner>
        <div className="mt-7 mb-4 flex items-center justify-between gap-3">
          <h2 className="text-sm font-medium">
            {query ? `Résultats pour « ${query} »` : "Morceaux de documents"}
          </h2>
          <span className="text-xs text-muted" aria-live="polite">
            {loading
              ? "Chargement…"
              : `${total} résultat${total === 1 ? "" : "s"}`}
          </span>
        </div>
        <div className="grid items-start gap-5 xl:grid-cols-[minmax(250px,0.8fr)_minmax(320px,1.2fr)]">
          <section
            aria-label="Morceaux"
            className="max-h-125 min-h-60 overflow-y-auto rounded-xl border border-line bg-white xl:max-h-165"
          >
            {loading ? (
              <p role="status" className="p-7 text-sm text-muted">
                Chargement des documents…
              </p>
            ) : !items.length ? (
              <div className="p-8 text-sm leading-7 text-muted">
                <FileText className="mb-3" size={24} strokeWidth={1} />
                {error
                  ? "Données indisponibles. Vérifiez Vespa et actualisez la page."
                  : query
                    ? "Aucun résultat. Essayez d’autres mots ou effacez la recherche."
                    : "Cette collection est vide. Indexez un document pour commencer."}
              </div>
            ) : (
              items.map((item) => (
                <button
                  key={item.id}
                  className={`block w-full border-b border-line p-5 text-left last:border-0 ${selected === item.id ? "bg-orange-50 shadow-[inset_3px_0_#f47719]" : "hover:bg-panel/70"}`}
                  onClick={() => select(item)}
                  aria-pressed={selected === item.id}
                >
                  <h3 className="text-sm font-medium">
                    {item.title || "Sans titre"}
                  </h3>
                  <p className="mt-2 line-clamp-3 text-xs leading-6 whitespace-pre-wrap break-words text-muted">
                    {item.content}
                  </p>
                  <div className="mt-3 flex items-center justify-between gap-2 font-mono text-[10px] text-muted">
                    <span>{item.locator || item.id}</span>
                    <span>{(item.content || "").length} car.</span>
                  </div>
                </button>
              ))
            )}
          </section>
          <section
            aria-label="Détail du morceau"
            className="min-h-90 overflow-hidden rounded-xl border border-line bg-white"
          >
            <DocumentDetail
              key={selected}
              document={document}
              loading={detailLoading}
            />
          </section>
        </div>
        <div className="mt-5 flex items-center justify-between">
          <button
            className="button text-xs"
            disabled={loading || offset === 0}
            onClick={() => setOffset((value) => Math.max(0, value - 20))}
          >
            <ArrowLeft size={13} />
            Précédent
          </button>
          <span className="text-[11px] text-muted">
            {total && items.length
              ? `${offset + 1}–${offset + items.length} sur ${total}`
              : "0 résultat"}
          </span>
          <button
            className="button text-xs"
            disabled={loading || offset + 20 >= total || offset + 20 > 1000}
            onClick={() => setOffset((value) => value + 20)}
          >
            Suivant
            <ArrowRight size={13} />
          </button>
        </div>
      </div>
    </div>
  );
}
