import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "../../providers/AuthProvider";

export default function ProtectedRoute({
  children,
}) {
  const location = useLocation();

  const {
    isAuthenticated,
    loading,
  } = useAuth();

  // ============================================================
  // Authentication is still being checked
  // ============================================================

  if (loading) {
    return (
      <div className="min-h-screen bg-[#020617] flex items-center justify-center">
        <div className="text-center">
          <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-cyan-500/30 border-t-cyan-400" />

          <p className="text-sm text-slate-400">
            Verifying session...
          </p>
        </div>
      </div>
    );
  }

  // ============================================================
  // No authenticated user
  // ============================================================

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
        state={{
          from:
            location.pathname +
            location.search,
        }}
      />
    );
  }

  // ============================================================
  // Authenticated
  // ============================================================

  return children;
}
