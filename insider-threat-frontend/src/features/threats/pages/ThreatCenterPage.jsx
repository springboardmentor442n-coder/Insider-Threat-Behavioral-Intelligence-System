import { useMemo, useState } from "react";
import { ShieldAlert, Activity, Wifi, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

import { useThreats } from "../hooks/useThreats";
import PageHeader from "../../../components/shared/PageHeader";

import ThreatOverviewCards from "../components/ThreatOverviewCards";
import ThreatToolbar from "../components/ThreatToolbar";
import ThreatTable from "../components/ThreatTable";
import ThreatDetailsDrawer from "../components/ThreatDetailsDrawer";
import ResolveThreatDialog from "../components/ResolveThreatDialog";
import DeleteThreatDialog from "../components/DeleteThreatDialog";

export default function ThreatCenterPage() {
  const {
    data = [],
    isLoading,
    isError,
    error,
  } = useThreats();

  const threats = Array.isArray(data) ? data : [];

  const [search, setSearch] = useState("");
  const [severity, setSeverity] = useState("");
  const [status, setStatus] = useState("");
  const [sortBy, setSortBy] = useState("risk");

  const [selectedThreat, setSelectedThreat] = useState(null);

  const [resolveOpen, setResolveOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);

  const filteredThreats = useMemo(() => {
    let list = [...threats];

    list = list.filter((t) => {
      const matchesSearch =
        t.employee_name?.toLowerCase().includes(search.toLowerCase()) ||
        t.user?.toLowerCase().includes(search.toLowerCase()) ||
        t.employee_id?.toString().toLowerCase().includes(search.toLowerCase()) ||
        t.department?.toLowerCase().includes(search.toLowerCase()) ||
        t.threat_type?.toLowerCase().includes(search.toLowerCase());

      const matchesSeverity = !severity || t.severity === severity;
      const matchesStatus = !status || t.status === status;

      return matchesSearch && matchesSeverity && matchesStatus;
    });

    if (sortBy === "risk") {
      list.sort((a, b) => b.risk_score - a.risk_score);
    } else if (sortBy === "latest") {
      list.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    } else if (sortBy === "oldest") {
      list.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
    }

    return list;
  }, [threats, search, severity, status, sortBy]);

  if (isLoading) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center gap-3">
        <Loader2 className="h-8 w-8 animate-spin text-cyan-400" />
        <p className="text-sm font-semibold text-slate-300">Loading Threat Intelligence Console...</p>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-2xl border border-red-500/30 bg-red-500/10 p-6 text-red-300">
        <h3 className="text-lg font-bold">Failed to load threats</h3>
        <p className="mt-1 text-xs">{error?.message || "Unable to retrieve threat intelligence feeds."}</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="space-y-6 pb-8"
    >
      {/* Header */}
      <PageHeader
        icon={ShieldAlert}
        title="Threat Center"
        subtitle="Active enterprise anomaly monitoring & threat intelligence feed"
        badge={
          <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-0.5 text-[10px] font-semibold text-emerald-400">
            <Wifi className="h-3 w-3 animate-pulse" />
            Live Threat Stream
          </span>
        }
      >
        <span className="rounded-xl border border-cyan-500/20 bg-cyan-500/10 px-3 py-1.5 text-xs font-semibold text-cyan-300">
          100 Top Suspicious Records
        </span>
      </PageHeader>

      {/* Summary Metrics */}
      <ThreatOverviewCards threats={filteredThreats} />

      {/* Toolbar */}
      <ThreatToolbar
        search={search}
        setSearch={setSearch}
        severity={severity}
        setSeverity={setSeverity}
        status={status}
        setStatus={setStatus}
        sortBy={sortBy}
        setSortBy={setSortBy}
        total={filteredThreats.length}
      />

      {/* Threat Table */}
      <ThreatTable
        threats={filteredThreats}
        onRowClick={setSelectedThreat}
      />

      {/* Threat Details Drawer */}
      <ThreatDetailsDrawer
        open={selectedThreat !== null}
        threat={selectedThreat}
        onClose={() => setSelectedThreat(null)}
        onResolve={() => setResolveOpen(true)}
        onDelete={() => setDeleteOpen(true)}
      />

      {/* Dialogs */}
      <ResolveThreatDialog
        open={resolveOpen}
        threat={selectedThreat}
        onClose={() => setResolveOpen(false)}
      />

      <DeleteThreatDialog
        open={deleteOpen}
        threat={selectedThreat}
        onClose={() => setDeleteOpen(false)}
      />
    </motion.div>
  );
}
