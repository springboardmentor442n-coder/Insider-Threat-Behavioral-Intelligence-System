import {
  Search,
  RefreshCcw,
} from "lucide-react";

export default function ExplainabilityToolbar({
  employeeId,
  setEmployeeId,
  onSearch,
  onRefresh,
  loading,
}) {
  return (
    <section
      className="
        flex
        flex-wrap
        items-center
        justify-between
        gap-4
        rounded-2xl
        border border-cyan-500/20
        bg-slate-900/70
        p-4
      "
    >
      <div className="relative">
        <Search
          size={18}
          className="
            absolute
            left-3
            top-1/2
            -translate-y-1/2
            text-slate-400
          "
        />

        <input
          value={employeeId}
          onChange={(event) =>
            setEmployeeId(event.target.value)
          }
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              onSearch();
            }
          }}
          placeholder="Enter employee ID..."
          className="
            w-80
            rounded-xl
            border
            border-slate-700
            bg-slate-800
            py-2
            pl-10
            pr-4
            text-white
            uppercase
            outline-none
            transition
            placeholder:text-slate-500
            focus:border-cyan-400
          "
        />
      </div>

      <div className="flex gap-3">
        <button
          type="button"
          onClick={onSearch}
          disabled={!employeeId.trim()}
          className="
            flex
            items-center
            gap-2
            rounded-xl
            border border-cyan-500/30
            bg-cyan-500/10
            px-4
            py-2
            text-cyan-300
            transition
            hover:bg-cyan-500/20
            disabled:cursor-not-allowed
            disabled:opacity-50
          "
        >
          <Search size={18} />
          Analyze
        </button>

        <button
          type="button"
          onClick={onRefresh}
          disabled={loading}
          className="
            flex
            items-center
            gap-2
            rounded-xl
            border border-emerald-500/30
            bg-emerald-500/10
            px-4
            py-2
            text-emerald-300
            transition
            hover:bg-emerald-500/20
            disabled:opacity-50
          "
        >
          <RefreshCcw
            size={18}
            className={
              loading
                ? "animate-spin"
                : ""
            }
          />

          Refresh
        </button>
      </div>
    </section>
  );
}
