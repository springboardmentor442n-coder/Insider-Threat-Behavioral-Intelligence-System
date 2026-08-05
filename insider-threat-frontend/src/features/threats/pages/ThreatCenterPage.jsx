import { useMemo, useState } from "react";
import { ShieldAlert, Activity, Wifi } from "lucide-react";
import { motion } from "framer-motion";

import { useThreats } from "../hooks/useThreats";

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

  const threats = Array.isArray(data)
    ? data
    : [];

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
        t.employee_name
          ?.toLowerCase()
          .includes(search.toLowerCase()) ||

        t.department
          ?.toLowerCase()
          .includes(search.toLowerCase()) ||

        t.threat_type
          ?.toLowerCase()
          .includes(search.toLowerCase());

      const matchesSeverity =
        !severity ||
        t.severity === severity;

      const matchesStatus =
        !status ||
        t.status === status;

      return (
        matchesSearch &&
        matchesSeverity &&
        matchesStatus
      );

    });

    if (sortBy === "risk") {

      list.sort(
        (a, b) =>
          b.risk_score - a.risk_score
      );

    }

    if (sortBy === "latest") {

      list.sort(
        (a, b) =>
          new Date(b.created_at) -
          new Date(a.created_at)
      );

    }

    if (sortBy === "oldest") {

      list.sort(
        (a, b) =>
          new Date(a.created_at) -
          new Date(b.created_at)
      );

    }

    return list;

  }, [
    threats,
    search,
    severity,
    status,
    sortBy,
  ]);

  if (isLoading)
    return (
      <div className="flex h-[60vh] items-center justify-center text-2xl">
        Loading Threat Center...
      </div>
    );

  if (isError)
    return (
      <div className="text-red-500">
        {error.message}
      </div>
    );

  return (

    <div className="mx-auto max-w-7xl space-y-8 pb-10">

      {/* Hero */}

      <motion.div

        initial={{
          opacity: 0,
          y: 25,
        }}

        animate={{
          opacity: 1,
          y: 0,
        }}

        className="
          relative

          overflow-hidden

          rounded-3xl

          border

          border-cyan-500/20

          bg-white/5

          backdrop-blur-3xl

          p-10

          shadow-[0_0_70px_rgba(6,182,212,.12)]
        "

      >

        <div className="absolute right-0 top-0 h-72 w-72 rounded-full bg-cyan-500/10 blur-[120px]" />

        <div className="absolute left-0 bottom-0 h-64 w-64 rounded-full bg-blue-500/10 blur-[120px]" />

        <div className="flex items-center justify-between">

          <div>

            <div className="flex items-center gap-3">

              <ShieldAlert
                size={38}
                className="text-cyan-400"
              />

              <h1 className="text-5xl font-bold">

                Threat Center

              </h1>

            </div>

            <p className="mt-4 max-w-2xl text-lg text-slate-400">

              AI-powered monitoring of insider threats,
              anomalous employee behaviour,
              suspicious activities and real-time investigations.

            </p>

          </div>

          <div className="space-y-4">

            <div className="flex items-center gap-3 rounded-full bg-green-500/15 px-5 py-3">

              <Wifi
                className="text-green-400"
                size={18}
              />

              <span className="font-semibold text-green-400">

                System Online

              </span>

            </div>

            <div className="flex items-center gap-3 rounded-full bg-cyan-500/15 px-5 py-3">

              <Activity
                className="text-cyan-400"
                size={18}
              />

              <span className="font-semibold text-cyan-300">

                Live Monitoring Enabled

              </span>

            </div>

          </div>

        </div>

      </motion.div>

      <ThreatOverviewCards
        threats={filteredThreats}
      />

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

      <ThreatTable
        threats={filteredThreats}
        onRowClick={setSelectedThreat}
      />

      <ThreatDetailsDrawer
        open={selectedThreat !== null}
        threat={selectedThreat}
        onClose={() => setSelectedThreat(null)}
        onResolve={() => setResolveOpen(true)}
        onDelete={() => setDeleteOpen(true)}
      />

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

    </div>

  );

}
