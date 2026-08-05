import { Users, Loader2 } from "lucide-react";
import EmployeeRow from "./EmployeeRow";

export default function EmployeeTable({
  employees = [],
  isLoading = false,
  onRowClick = () => {},
  onEdit = () => {},
  onDelete = () => {},
}) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center rounded-xl border border-slate-800 bg-slate-900 py-16">
        <Loader2 className="h-8 w-8 animate-spin text-cyan-400" />
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900 shadow-lg">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-800">
          <thead className="bg-slate-800">
            <tr>
              <th className="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">
                Employee Code
              </th>

              <th className="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">
                Name
              </th>

              <th className="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">
                Department
              </th>

              <th className="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">
                Designation
              </th>

              <th className="px-5 py-4 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">
                Risk
              </th>

              <th className="px-5 py-4 text-right text-xs font-semibold uppercase tracking-wider text-slate-400">
                Actions
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-800">
            {employees.length === 0 ? (
              <tr>
                <td
                  colSpan={6}
                  className="py-16 text-center text-slate-400"
                >
                  <Users className="mx-auto mb-3 h-10 w-10 text-slate-600" />

                  <p className="text-lg font-medium">
                    No Employees Found
                  </p>

                  <p className="mt-1 text-sm text-slate-500">
                    Try changing the filters or add a new employee.
                  </p>
                </td>
              </tr>
            ) : (
              employees.map((employee) => (
                <EmployeeRow
                  key={employee.id}
                  employee={employee}
                  onView={onRowClick}
                  onEdit={onEdit}
                  onDelete={onDelete}
                />
              ))
            )}
          </tbody>
        </table>
      </div>

      {employees.length > 0 && (
        <div className="border-t border-slate-800 bg-slate-900 px-5 py-3 text-sm text-slate-400">
          Total Employees:{" "}
          <span className="font-semibold text-white">
            {employees.length}
          </span>
        </div>
      )}
    </div>
  );
}
