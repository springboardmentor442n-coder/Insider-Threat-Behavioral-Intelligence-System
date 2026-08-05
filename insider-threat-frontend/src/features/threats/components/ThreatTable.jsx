import ThreatRow from "./ThreatRow";

export default function ThreatTable({
  threats,
  onRowClick,
}) {
  if (!threats.length) {
    return (
      <div
        className="
          rounded-3xl
          border
          border-white/10
          bg-white/5
          backdrop-blur-2xl
          shadow-xl
          shadow-cyan-500/10
          p-16
          text-center
        "
      >
        <h2 className="text-3xl font-bold">
          No Threats Found
        </h2>

        <p className="mt-4 text-slate-400">
          Try changing filters or search keywords.
        </p>
      </div>
    );
  }

  return (
    <div
      className="
        overflow-hidden

        rounded-3xl

        border
        border-white/10

        bg-white/5

        backdrop-blur-2xl

        shadow-2xl

        shadow-cyan-500/10
      "
    >
      <div className="overflow-x-auto">

        <table className="w-full min-w-[1200px]">

          <thead
            className="
              sticky

              top-0

              bg-slate-900/90

              backdrop-blur-xl

              border-b

              border-white/10
            "
          >
            <tr>

              <th className="px-6 py-5 text-left text-slate-300">
                Employee
              </th>

              <th className="px-6 text-left text-slate-300">
                Department
              </th>

              <th className="px-6 text-left text-slate-300">
                Threat
              </th>

              <th className="px-6 text-center text-slate-300">
                Risk
              </th>

              <th className="px-6 text-center text-slate-300">
                Severity
              </th>

              <th className="px-6 text-center text-slate-300">
                Status
              </th>

              <th className="px-6 text-center text-slate-300">
                Date
              </th>

            </tr>

          </thead>

          <tbody>

            {threats.map((threat) => (

              <ThreatRow
                key={threat.id}
                threat={threat}
                onClick={onRowClick}
              />

            ))}

          </tbody>

        </table>

      </div>

    </div>
  );
}
