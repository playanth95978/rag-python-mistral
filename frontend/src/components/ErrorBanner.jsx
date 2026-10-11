import { AlertCircle } from "lucide-react";

export default function ErrorBanner({ children }) {
  if (!children) return null;
  return (
    <div
      role="alert"
      className="my-3 flex items-start gap-3 rounded-xl border border-orange-200 bg-orange-50 px-4 py-3 text-sm text-orange-900"
    >
      <AlertCircle size={17} className="mt-0.5 shrink-0" />
      <span>{children}</span>
    </div>
  );
}
