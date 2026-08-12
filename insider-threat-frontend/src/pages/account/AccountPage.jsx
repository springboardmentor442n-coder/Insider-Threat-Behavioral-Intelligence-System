import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  User,
  Shield,
  KeyRound,
  CheckCircle2,
  Settings,
  LogOut,
  ShieldCheck,
  BadgeCheck,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import authService from "../../services/auth/authService";
import { useAuth } from "../../providers/AuthProvider";

export default function AccountPage() {
  const navigate = useNavigate();
  const { user: authUser, logout } = useAuth();
  const [user, setUser] = useState(authUser || null);
  const [loadingUser, setLoadingUser] = useState(!authUser);
  const [error, setError] = useState("");

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
        console.error("Failed to load account details:", err);
        if (mounted) {
          setError("Unable to load account information.");
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
    logout();
    navigate("/login");
  };

  const username = user?.username || user?.user || user?.name || "User";
  const role = user?.role
    ? user.role.charAt(0).toUpperCase() + user.role.slice(1)
    : "Security Analyst";
  const initial = username.charAt(0).toUpperCase();

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="space-y-6"
    >
      {/* Header */}
      <section className="relative overflow-hidden rounded-2xl border border-cyan-500/20 bg-gradient-to-r from-slate-900/90 via-slate-900/70 to-slate-950/90 p-5 md:p-6 backdrop-blur-xl shadow-lg shadow-cyan-950/20">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 to-blue-600 text-2xl font-extrabold text-white shadow-lg shadow-cyan-500/20">
            {initial}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl md:text-2xl font-bold tracking-tight text-white">
                {username}
              </h1>
              <span className="inline-flex items-center gap-1 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-2.5 py-0.5 text-xs font-semibold text-cyan-300">
                <BadgeCheck size={13} />
                {role}
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-400">
              User Identity & Security Access Profile
            </p>
          </div>
        </div>
      </section>

      {/* Profile Details */}
      <section className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur-sm shadow-xl">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <User className="text-cyan-400" size={22} />
            <div>
              <h2 className="text-lg font-semibold text-white">
                Account Details
              </h2>
              <p className="text-xs text-slate-400">
                Authenticated user identity and role assignment
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => navigate("/settings")}
            className="flex items-center gap-1.5 rounded-xl border border-slate-700 bg-slate-800/50 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-slate-700 hover:text-white"
          >
            <Settings size={14} />
            System Settings
          </button>
        </div>

        {loadingUser ? (
          <div className="rounded-xl bg-slate-800/40 p-6 text-center text-xs text-slate-400">
            Loading profile information...
          </div>
        ) : error ? (
          <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-xs text-red-400">
            {error}
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-xl border border-slate-700/80 bg-slate-800/40 p-4">
              <p className="text-xs font-medium text-slate-400">Username</p>
              <p className="mt-1.5 text-base font-bold text-white">{username}</p>
            </div>

            <div className="rounded-xl border border-slate-700/80 bg-slate-800/40 p-4">
              <p className="text-xs font-medium text-slate-400">Assigned Role</p>
              <p className="mt-1.5 text-base font-bold text-cyan-400">{role}</p>
            </div>

            <div className="rounded-xl border border-slate-700/80 bg-slate-800/40 p-4">
              <p className="text-xs font-medium text-slate-400">Account Status</p>
              <div className="mt-1.5 flex items-center gap-1.5 text-emerald-400 font-bold text-sm">
                <CheckCircle2 size={16} />
                Active & Verified
              </div>
            </div>
          </div>
        )}
      </section>

      {/* Role & Privileges */}
      <section className="rounded-2xl border border-slate-800/80 bg-slate-900/60 p-5 backdrop-blur-sm shadow-xl">
        <div className="mb-4 flex items-center gap-3">
          <ShieldCheck className="text-blue-400" size={22} />
          <div>
            <h2 className="text-lg font-semibold text-white">
              Role & Security Privileges
            </h2>
            <p className="text-xs text-slate-400">
              Role-Based Access Control (RBAC) permissions
            </p>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-start gap-3 rounded-xl border border-slate-800 bg-slate-950/40 p-3.5">
            <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-cyan-500/10 text-cyan-400">
              <Shield size={16} />
            </div>
            <div>
              <p className="text-xs font-bold text-white">
                {role} Permissions
              </p>
              <p className="mt-0.5 text-xs text-slate-400">
                Full access to Threat Center, Employee Intelligence, Behavioral Verification, ML Models, and Report Exports.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Sign Out */}
      <section className="rounded-2xl border border-red-500/20 bg-slate-900/60 p-5 backdrop-blur-sm">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-3">
            <KeyRound className="text-red-400" size={22} />
            <div>
              <h2 className="text-base font-semibold text-white">
                Session Control
              </h2>
              <p className="text-xs text-slate-400">
                End active security session and log out
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleLogout}
            className="flex items-center justify-center gap-2 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-2.5 text-xs font-semibold text-red-400 transition hover:bg-red-500/20"
          >
            <LogOut size={16} />
            Logout Session
          </button>
        </div>
      </section>
    </motion.div>
  );
}
