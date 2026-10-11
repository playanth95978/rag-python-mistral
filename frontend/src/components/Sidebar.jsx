import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { Database, MessageSquare, Plus, Search, Trash2, X } from "lucide-react";
import Logo from "./Logo";

export default function Sidebar({ conversations, open, onClose }) {
  const [filter, setFilter] = useState("");
  const navigate = useNavigate();
  const { chats, active, busy, newChat, selectChat, deleteChat } =
    conversations;
  const linkClass = ({ isActive }) =>
    `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm ${isActive ? "bg-white text-ink ring-1 ring-line" : "text-muted hover:bg-black/5"}`;
  return (
    <>
      {open && (
        <button
          aria-label="Fermer le menu"
          className="fixed inset-0 z-30 bg-black/20 md:hidden"
          onClick={onClose}
        />
      )}
      <aside
        className={`${open ? "visible translate-x-0" : "invisible -translate-x-full"} fixed inset-y-0 left-0 z-40 flex w-64 shrink-0 flex-col border-r border-line bg-panel p-4 transition-transform md:visible md:static md:translate-x-0`}
      >
        <div className="mb-8 flex items-center justify-between px-2 pt-4">
          <Link
            to="/"
            onClick={onClose}
            className="flex items-center gap-3"
            aria-label="Le Chat, accueil"
          >
            <Logo />
            <span className="text-[28px] font-semibold tracking-[-1.2px]">
              le Chat<span className="text-accent">.</span>
            </span>
          </Link>
          <button
            className="icon-button md:hidden"
            onClick={onClose}
            aria-label="Fermer la navigation"
          >
            <X size={18} />
          </button>
        </div>
        <button
          disabled={busy}
          className="button mb-5 justify-start py-3 font-medium"
          onClick={() => {
            newChat();
            navigate("/");
            onClose();
          }}
        >
          <Plus size={18} />
          Nouveau chat<span className="ml-auto text-xs text-muted">⌘ K</span>
        </button>
        <nav className="space-y-1" aria-label="Navigation principale">
          <NavLink to="/" end className={linkClass} onClick={onClose}>
            <MessageSquare size={17} />
            Conversations
          </NavLink>
          <NavLink to="/admin/vespa" className={linkClass} onClick={onClose}>
            <Database size={17} />
            Explorer Vespa
          </NavLink>
        </nav>
        <div className="mt-7 mb-3 flex items-center gap-2 px-2 text-muted">
          <Search size={15} />
          <input
            className="min-w-0 bg-transparent text-xs outline-none"
            placeholder="Rechercher un chat"
            aria-label="Rechercher une conversation"
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
          />
        </div>
        <div className="px-2 py-3 text-xs text-muted">Vos conversations</div>
        <nav
          className="min-h-0 flex-1 overflow-y-auto"
          aria-label="Conversations sauvegardées"
        >
          {chats
            .filter((chat) =>
              chat.title.toLowerCase().includes(filter.toLowerCase()),
            )
            .map((chat) => (
              <div
                key={chat.id}
                className={`group mb-1 flex items-center rounded-lg ${chat.id === active.id ? "bg-[#e9e6df]" : "hover:bg-black/4"}`}
              >
                <button
                  disabled={busy}
                  className="min-w-0 flex-1 truncate p-3 text-left text-xs"
                  onClick={() => {
                    selectChat(chat.id);
                    navigate("/");
                    onClose();
                  }}
                >
                  {chat.title}
                </button>
                <button
                  disabled={busy}
                  className="icon-button size-8 mr-1 opacity-60 hover:opacity-100"
                  aria-label={`Supprimer ${chat.title}`}
                  onClick={() => deleteChat(chat.id)}
                >
                  <Trash2 size={13} />
                </button>
              </div>
            ))}
        </nav>
        <div className="mt-4 border-t border-line pt-4">
          <div className="mb-4 flex items-center gap-2 px-2 text-xs text-muted">
            <span className="size-1.5 rounded-full bg-emerald-600" />
            Votre espace personnel
          </div>
          <div className="flex items-center gap-3 px-2">
            <span className="flex size-9 items-center justify-center rounded-full bg-[#e6e0d5] text-xs">
              V
            </span>
            <div className="text-sm">
              Vous
              <p className="mt-0.5 text-[10px] text-muted">
                Conversations sur cet appareil
              </p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
