import { useEffect, useState } from "react";
import {
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
} from "react-router-dom";
import { ChevronDown, Menu } from "lucide-react";
import Sidebar from "./components/Sidebar";
import ChatPage from "./pages/ChatPage";
import VespaPage from "./pages/VespaPage";
import useConversations from "./hooks/useConversations";

export default function App() {
  const conversations = useConversations();
  const [menu, setMenu] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const isExplorer = location.pathname.startsWith("/admin/vespa");
  useEffect(() => {
    const listener = (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        if (!conversations.busy) {
          conversations.newChat();
          navigate("/");
        }
      }
      if (event.key === "Escape") setMenu(false);
    };
    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, [conversations.busy, conversations.newChat, navigate]);
  return (
    <div className="flex h-dvh overflow-hidden">
      <Sidebar
        conversations={conversations}
        open={menu}
        onClose={() => setMenu(false)}
      />
      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-17 shrink-0 items-center gap-3 border-b border-transparent px-5 sm:px-9">
          <button
            onClick={() => setMenu(true)}
            className="icon-button md:hidden"
            aria-label="Ouvrir le menu"
            aria-expanded={menu}
          >
            <Menu size={20} />
          </button>
          <div className="flex items-center gap-2 text-sm font-medium">
            {isExplorer ? "Explorateur Vespa" : "Mistral Large 4"}
            {!isExplorer && <ChevronDown size={13} className="text-muted" />}
          </div>
          <span className="ml-auto hidden text-[11px] text-muted lg:inline">
            {isExplorer
              ? "Votre moteur de recherche, sous les yeux."
              : "Un peu d’inspiration. Beaucoup de possibilités."}
          </span>
        </header>
        <Routes>
          <Route
            path="/"
            element={<ChatPage conversations={conversations} />}
          />
          <Route path="/admin/vespa" element={<VespaPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}
