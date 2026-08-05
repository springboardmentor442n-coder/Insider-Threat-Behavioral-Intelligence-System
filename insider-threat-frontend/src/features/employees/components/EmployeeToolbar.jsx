import {
  Search,
  Plus,
  Download,
} from "lucide-react";

export default function EmployeeToolbar({
  search,
  setSearch,

  department,
  setDepartment,

  riskLevel,
  setRiskLevel,

  onAdd,

  employees = [],
}) {
  const exportCSV = () => {
    if (!employees.length) return;

    const csv = [
      [
        "Employee Code",
        "Name",
        "Email",
        "Department",
        "Designation",
        "Risk Score",
        "Risk Level",
      ],
      ...employees.map((e) => [
        e.employee_code,
        e.full_name,
        e.email,
        e.department,
        e.designation,
        e.risk_score,
        e.risk_level,
      ]),
    ]
      .map((r) => r.join(","))
      .join("\n");

    const blob = new Blob([csv], {
      type: "text/csv;charset=utf-8;",
    });

    const url = window.URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;

    link.download = "employees.csv";

    link.click();

    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">

      <div className="flex flex-wrap gap-4 items-center">

        <div className="relative flex-1 min-w-[250px]">

          <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />

          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search employee..."
            className="w-full rounded-lg border border-slate-700 bg-slate-800 py-2 pl-10 pr-4 text-white"
          />

        </div>

        <select
          value={department}
          onChange={(e) => setDepartment(e.target.value)}
          className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white"
        >
          <option value="">All Departments</option>

          <option>Engineering</option>
          <option>Finance</option>
          <option>Human Resources</option>
          <option>IT Operations</option>
          <option>Legal</option>
          <option>Sales</option>
          <option>Security</option>

        </select>

        <select
          value={riskLevel}
          onChange={(e) => setRiskLevel(e.target.value)}
          className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white"
        >
          <option value="">All Risk Levels</option>

          <option value="low">Low</option>

          <option value="medium">Medium</option>

          <option value="high">High</option>

          <option value="critical">Critical</option>

        </select>

        <button
          onClick={exportCSV}
          className="flex items-center gap-2 rounded-lg bg-slate-700 px-4 py-2 text-white hover:bg-slate-600"
        >
          <Download className="h-4 w-4" />

          Export
        </button>

        <button
          onClick={onAdd}
          className="flex items-center gap-2 rounded-lg bg-cyan-500 px-4 py-2 font-semibold text-black hover:bg-cyan-400"
        >
          <Plus className="h-4 w-4" />

          Add Employee
        </button>

      </div>

    </div>
  );
}
