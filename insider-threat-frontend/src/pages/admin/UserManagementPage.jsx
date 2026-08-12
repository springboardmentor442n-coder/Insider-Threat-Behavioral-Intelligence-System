import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Users, Shield, UserCheck, UserX, RefreshCw, CheckCircle2, AlertCircle } from "lucide-react";
import api from "../../services/api/axiosClient";
import PageHeader from "../../components/shared/PageHeader";

const ROLES = [
  "Security Analyst",
  "SOC Engineer",
  "Security Manager",
  "Administrator"
];

export default function UserManagementPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updatingId, setUpdatingId] = useState(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const { data } = await api.get("/auth/users");
      setUsers(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load users:", err);
      setError("Failed to fetch registered users. Only Administrators have access.");
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      setUpdatingId(userId);
      await api.patch(`/auth/users/${userId}/role?role=${encodeURIComponent(newRole)}`);
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, role: newRole } : u))
      );
    } catch (err) {
      console.error("Failed to update role:", err);
      alert("Failed to update role. Please ensure you are logged in as an Administrator.");
    } finally {
      setUpdatingId(null);
    }
  };

  const handleToggleStatus = async (userId, currentStatus) => {
    const nextStatus = !currentStatus;
    try {
      setUpdatingId(userId);
      await api.patch(`/auth/users/${userId}/status?is_active=${nextStatus}`);
      setUsers((prev) =>
        prev.map((u) => (u.id === userId ? { ...u, is_active: nextStatus } : u))
      );
    } catch (err) {
      console.error("Failed to toggle status:", err);
      alert("Failed to toggle user status.");
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="space-y-5 pb-6">
      <PageHeader
        icon={Users}
        title="User Management"
        subtitle="Administrator panel: Manage user accounts, role-based access control, and activation status"
      >
        <button
          type="button"
          onClick={fetchUsers}
          className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} /> Refresh
        </button>
      </PageHeader>

      {error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-xs text-red-300">
          <AlertCircle className="mr-2 inline h-4 w-4" /> {error}
        </div>
      )}

      <div className="overflow-hidden rounded-2xl border border-cyan-500/20 bg-slate-900/60 backdrop-blur-xl">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-800/80 text-xs uppercase tracking-wider text-slate-400">
            <tr>
              <th className="px-6 py-3.5">User ID</th>
              <th className="px-6 py-3.5">Username</th>
              <th className="px-6 py-3.5">Role</th>
              <th className="px-6 py-3.5">Account Status</th>
              <th className="px-6 py-3.5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {loading ? (
              <tr>
                <td colSpan={5} className="py-12 text-center text-slate-400">
                  Loading registered users...
                </td>
              </tr>
            ) : users.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-12 text-center text-slate-400">
                  No registered users found.
                </td>
              </tr>
            ) : (
              users.map((u) => (
                <tr key={u.id} className="hover:bg-slate-800/40">
                  <td className="px-6 py-4 font-mono text-xs text-slate-400">#{u.id}</td>
                  <td className="px-6 py-4 font-bold text-white">{u.username}</td>
                  <td className="px-6 py-4">
                    <select
                      value={u.role || "Security Analyst"}
                      disabled={updatingId === u.id}
                      onChange={(e) => handleRoleChange(u.id, e.target.value)}
                      className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1 text-xs text-slate-200 focus:border-cyan-500 focus:outline-none"
                    >
                      {ROLES.map((r) => (
                        <option key={r} value={r}>
                          {r}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                        u.is_active
                          ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                          : "bg-red-500/20 text-red-400 border border-red-500/30"
                      }`}
                    >
                      {u.is_active ? <UserCheck className="h-3 w-3" /> : <UserX className="h-3 w-3" />}
                      {u.is_active ? "Active" : "Deactivated"}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleToggleStatus(u.id, u.is_active)}
                      disabled={updatingId === u.id}
                      className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                        u.is_active
                          ? "bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/30"
                          : "bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 border border-emerald-500/30"
                      }`}
                    >
                      {u.is_active ? "Deactivate" : "Activate"}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
