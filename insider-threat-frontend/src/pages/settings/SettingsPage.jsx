import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Settings,
  User,
  Shield,
  LogOut,
  KeyRound,
  CheckCircle2,
  Moon,
  Sun,
} from "lucide-react";

import authService from "../../services/auth/authService";
import { useTheme } from "../../providers/ThemeProvider";

export default function SettingsPage() {
  const [user, setUser] = useState(null);
  const [loadingUser, setLoadingUser] = useState(true);
  const [error, setError] = useState("");

  const { isDark, toggleTheme } = useTheme();

  useEffect(() => {
    let mounted = true;

    async function loadUser() {
      try {
        setLoadingUser(true);
        setError("");

        const data = await authService.me();

        if (mounted) {
          setUser(data);
        }
      } catch (err) {
        console.error("Failed to load current user:", err);

        if (mounted) {
          setError("Unable to load current user information.");
        }
      } finally {
        if (mounted) {
          setLoadingUser(false);
        }
      }
    }

    loadUser();

    return () => {
      mounted = false;
    };
  }, []);

  const handleLogout = () => {
    authService.logout();

    window.location.href = "/login";
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="space-y-6"
    >
      {/* Header */}
      <section className="rounded-3xl border border-cyan-500/20 bg-slate-900/70 p-8">
        <div className="flex items-center gap-4">
          <div className="rounded-2xl bg-cyan-500/20 p-4">
            <Settings className="h-8 w-8 text-cyan-400" />
          </div>

          <div>
            <h1 className="text-4xl font-bold text-white">
              Settings
            </h1>

            <p className="mt-2 text-slate-400">
              Manage your account, appearance and security session.
            </p>
          </div>
        </div>
      </section>

      {/* Account */}
      <section className="rounded-3xl border border-slate-700 bg-slate-900/70 p-6">
        <div className="mb-6 flex items-center gap-3">
          <User className="text-cyan-400" size={24} />

          <div>
            <h2 className="text-xl font-semibold text-white">
              Account
            </h2>

            <p className="text-sm text-slate-400">
              Current authenticated user
            </p>
          </div>
        </div>

        {loadingUser ? (
          <div className="rounded-2xl bg-slate-800/60 p-5 text-slate-400">
            Loading account information...
          </div>
        ) : error ? (
          <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-5 text-red-400">
            {error}
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-slate-700 bg-slate-800/50 p-5">
              <p className="text-sm text-slate-400">
                Username
              </p>

              <p className="mt-2 text-lg font-semibold text-white">
                {user?.username ||
                  user?.user ||
                  user?.name ||
                  "Unknown"}
              </p>
            </div>

            <div className="rounded-2xl border border-slate-700 bg-slate-800/50 p-5">
              <p className="text-sm text-slate-400">
                Role
              </p>

              <p className="mt-2 text-lg font-semibold capitalize text-cyan-400">
                {user?.role || "User"}
              </p>
            </div>
          </div>
        )}
      </section>

      {/* Security */}
      <section className="rounded-3xl border border-slate-700 bg-slate-900/70 p-6">
        <div className="mb-6 flex items-center gap-3">
          <Shield className="text-green-400" size={24} />

          <div>
            <h2 className="text-xl font-semibold text-white">
              Security
            </h2>

            <p className="text-sm text-slate-400">
              Current session status
            </p>
          </div>
        </div>

        <div className="flex items-center justify-between rounded-2xl border border-green-500/20 bg-green-500/10 p-5">
          <div className="flex items-center gap-3">
            <CheckCircle2
              className="text-green-400"
              size={22}
            />

            <div>
              <p className="font-semibold text-green-400">
                Session Active
              </p>

              <p className="text-sm text-slate-400">
                Your authentication session is currently active.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Appearance */}
      <section className="rounded-3xl border border-slate-700 bg-slate-900/70 p-6">
        <div className="mb-6 flex items-center gap-3">
          {isDark ? (
            <Moon className="text-cyan-400" size={24} />
          ) : (
            <Sun className="text-yellow-400" size={24} />
          )}

          <div>
            <h2 className="text-xl font-semibold text-white">
              Appearance
            </h2>

            <p className="text-sm text-slate-400">
              Choose your preferred interface theme.
            </p>
          </div>
        </div>

        <div className="flex items-center justify-between rounded-2xl border border-slate-700 bg-slate-800/50 p-5">
          <div>
            <p className="font-semibold text-white">
              Dark Mode
            </p>

            <p className="text-sm text-slate-400">
              {isDark
                ? "Dark mode is enabled."
                : "Light mode is enabled."}
            </p>
          </div>

          <button
            type="button"
            onClick={toggleTheme}
            className={`relative h-7 w-14 rounded-full transition ${
              isDark
                ? "bg-cyan-500"
                : "bg-slate-600"
            }`}
            aria-label="Toggle dark mode"
          >
            <span
              className={`absolute top-1 h-5 w-5 rounded-full bg-white transition ${
                isDark
                  ? "left-8"
                  : "left-1"
              }`}
            />
          </button>
        </div>
      </section>

      {/* Logout */}
      <section className="rounded-3xl border border-red-500/20 bg-slate-900/70 p-6">
        <div className="flex flex-col gap-5 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-3">
            <KeyRound
              className="text-red-400"
              size={24}
            />

            <div>
              <h2 className="text-xl font-semibold text-white">
                Sign Out
              </h2>

              <p className="text-sm text-slate-400">
                End your current authenticated session.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleLogout}
            className="
              flex
              items-center
              justify-center
              gap-2
              rounded-xl
              border
              border-red-500/30
              bg-red-500/10
              px-5
              py-3
              font-semibold
              text-red-400
              transition
              hover:bg-red-500/20
            "
          >
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </section>
    </motion.div>
  );
}
