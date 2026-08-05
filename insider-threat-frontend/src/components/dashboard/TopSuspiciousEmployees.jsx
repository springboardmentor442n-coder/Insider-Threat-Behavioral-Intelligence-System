import GlassCard from "../ui/GlassCard";

export default function TopSuspiciousEmployees({ employees = [] }) {
  return (
    <GlassCard className="p-6">
      <div className="flex items-center justify-between mb-6">

        <h2 className="text-2xl font-bold">
          Top Suspicious Employees
        </h2>

        <span className="text-cyan-400 text-sm">
          {employees.length} Results
        </span>

      </div>

      <div className="overflow-x-auto">

        <table className="w-full">

          <thead>

            <tr className="border-b border-cyan-500/20">

              <th className="py-4 text-left">Employee</th>

              <th className="text-left">Department</th>

              <th className="text-left">Role</th>

              <th className="text-center">Risk</th>

              <th className="text-center">Severity</th>

            </tr>

          </thead>

          <tbody>

            {employees.map((emp) => (

              <tr
                key={emp.user}
                className="
                border-b
                border-white/5

                hover:bg-cyan-500/10

                transition
                duration-300
              "
              >

                <td className="py-5">

                  <div>

                    <h3 className="font-semibold">
                      {emp.employee_name}
                    </h3>

                    <p className="text-slate-400 text-sm">
                      {emp.user}
                    </p>

                  </div>

                </td>

                <td>{emp.department}</td>

                <td>{emp.role}</td>

                <td className="text-center">

                  <div className="font-bold text-cyan-400">
                    {emp.risk_score}
                  </div>

                </td>

                <td className="text-center">

                  <span
                    className={`
                    rounded-full
                    px-4
                    py-1
                    text-sm

                    ${
                      emp.severity === "Critical"
                        ? "bg-red-500/20 text-red-400"
                        : emp.severity === "High"
                        ? "bg-orange-500/20 text-orange-400"
                        : emp.severity === "Medium"
                        ? "bg-yellow-500/20 text-yellow-400"
                        : "bg-green-500/20 text-green-400"
                    }
                  `}
                  >
                    {emp.severity}
                  </span>

                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

    </GlassCard>
  );
}
