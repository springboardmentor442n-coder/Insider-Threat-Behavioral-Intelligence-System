import { Search, Filter, ArrowUpDown } from "lucide-react";
import { motion } from "framer-motion";

export default function ThreatToolbar({
  search,
  setSearch,
  severity,
  setSeverity,
  status,
  setStatus,
  sortBy,
  setSortBy,
  total,
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl border border-slate-800/80 bg-slate-900/70 p-5 backdrop-blur-xl shadow-lg"
    >
      <div className="flex flex-wrap gap-4 items-center justify-between">
        {/* Search */}
        <div className="relative flex-1 min-w-[280px]">
          <Search
            size={18}
            className="absolute left-3.5 top-3 text-cyan-400"
          />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search employee ID, department, or threat pattern..."
            className="w-full rounded-xl border border-slate-700/80 bg-slate-950/80 pl-10 pr-4 py-2 text-xs md:text-sm text-slate-100 placeholder-slate-500 outline-none transition focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/30"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Severity */}
          <div className="flex items-center gap-2">
            <Filter size={16} className="text-cyan-400" />
            <select
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
              className="rounded-xl border border-slate-700/80 bg-slate-950/80 px-3 py-2 text-xs md:text-sm text-slate-200 outline-none transition focus:border-cyan-500"
            >
              <option value="">All Severities</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>

          {/* Status */}
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="rounded-xl border border-slate-700/80 bg-slate-950/80 px-3 py-2 text-xs md:text-sm text-slate-200 outline-none transition focus:border-cyan-500"
          >
            <option value="">All Statuses</option>
            <option value="Open">Open</option>
            <option value="Investigating">Investigating</option>
            <option value="Resolved">Resolved</option>
          </select>

          {/* Sort */}
          <div className="flex items-center gap-2">
            <ArrowUpDown size={16} className="text-cyan-400" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="rounded-xl border border-slate-700/80 bg-slate-950/80 px-3 py-2 text-xs md:text-sm text-slate-200 outline-none transition focus:border-cyan-500"
            >
              <option value="risk">Highest Risk First</option>
              <option value="latest">Newest First</option>
              <option value="oldest">Oldest First</option>
            </select>
          </div>
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-slate-800/80 pt-3 text-xs">
        <span className="text-slate-400">
          Displaying <span className="font-bold text-cyan-400">{total}</span> threat records
        </span>

        <span className="inline-flex items-center gap-1.5 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-[11px] font-semibold text-cyan-300">
          <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 animate-pulse" />
          Active ML Detection Feed
        </span>
      </div>
    </motion.div>
  );
}
