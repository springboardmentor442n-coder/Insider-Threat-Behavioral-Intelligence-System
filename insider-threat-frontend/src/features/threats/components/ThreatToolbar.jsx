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
      initial={{
        opacity: 0,
        y: 15,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="
        rounded-3xl

        border
        border-white/10

        bg-white/5

        backdrop-blur-2xl

        shadow-xl

        shadow-cyan-500/10

        p-6
      "
    >
      <div
        className="
          flex

          flex-wrap

          gap-4

          items-center
        "
      >
        {/* Search */}

        <div className="relative flex-1 min-w-[280px]">

          <Search
            size={20}
            className="
              absolute

              left-4

              top-3.5

              text-cyan-400
            "
          />

          <input
            value={search}
            onChange={(e) =>
              setSearch(e.target.value)
            }
            placeholder="Search employee, department or threat..."
            className="
              w-full

              rounded-2xl

              border
              border-white/10

              bg-slate-900/60

              pl-12

              pr-4

              py-3

              outline-none

              transition

              focus:border-cyan-400

              focus:ring-2

              focus:ring-cyan-500/20
            "
          />

        </div>

        {/* Severity */}

        <div className="flex items-center gap-2">

          <Filter
            size={18}
            className="text-cyan-400"
          />

          <select
            value={severity}
            onChange={(e) =>
              setSeverity(e.target.value)
            }
            className="
              rounded-xl

              border

              border-white/10

              bg-slate-900/60

              px-4

              py-3

              outline-none
            "
          >
            <option value="">All Severity</option>
            <option>Critical</option>
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
          </select>

        </div>

        {/* Status */}

        <select
          value={status}
          onChange={(e) =>
            setStatus(e.target.value)
          }
          className="
            rounded-xl

            border

            border-white/10

            bg-slate-900/60

            px-4

            py-3
          "
        >
          <option value="">All Status</option>
          <option>Open</option>
          <option>Resolved</option>
          <option>Investigating</option>
        </select>

        {/* Sort */}

        <div className="flex items-center gap-2">

          <ArrowUpDown
            size={18}
            className="text-cyan-400"
          />

          <select
            value={sortBy}
            onChange={(e) =>
              setSortBy(e.target.value)
            }
            className="
              rounded-xl

              border

              border-white/10

              bg-slate-900/60

              px-4

              py-3
            "
          >
            <option value="risk">
              Highest Risk
            </option>

            <option value="latest">
              Newest
            </option>

            <option value="oldest">
              Oldest
            </option>

          </select>

        </div>

      </div>

      <div
        className="
          mt-6

          flex

          items-center

          justify-between

          border-t

          border-white/10

          pt-5
        "
      >
        <span className="text-slate-400">
          Showing
          <span className="ml-2 font-semibold text-cyan-400">
            {total}
          </span>
          {" "}threats
        </span>

        <div
          className="
            rounded-full

            border

            border-cyan-500/30

            bg-cyan-500/10

            px-4

            py-2

            text-sm

            text-cyan-300
          "
        >
          Live Monitoring
        </div>

      </div>

    </motion.div>
  );
}
