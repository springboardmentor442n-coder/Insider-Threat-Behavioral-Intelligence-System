import { AnimatePresence, motion } from "framer-motion";
import { X, Mail, Building2, Briefcase, Hash, Pencil, Trash2 } from "lucide-react";
import RiskSummaryCard from "./RiskSummaryCard";
import EmployeeActivityTimeline from "./EmployeeActivityTimeline";

function InfoRow({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center gap-3 py-2">
      <div className="rounded-md bg-slate-800/80 p-1.5 text-slate-400">
        <Icon className="h-3.5 w-3.5" />
      </div>
      <div>
        <p className="text-[11px] uppercase tracking-wide text-slate-500">
          {label}
        </p>
        <p className="text-sm text-slate-200">{value || "—"}</p>
      </div>
    </div>
  );
}

export default function EmployeeProfileDrawer({
  open,
  employee,
  onClose,
  onEdit,
  onDelete,
}) {
  return (
    <AnimatePresence>
      {open && employee && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm"
            onClick={onClose}
          />

          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", stiffness: 320, damping: 32 }}
            className="relative flex h-full w-full max-w-md flex-col border-l border-slate-800 bg-slate-950 shadow-2xl sm:max-w-lg"
          >
            <div className="flex items-start justify-between border-b border-slate-800 px-6 py-5">
              <div>
                <p className="text-xs font-medium text-cyan-400">
                  {employee.employee_code}
                </p>
                <h2 className="mt-1 text-lg font-semibold text-slate-100">
                  {employee.full_name}
                </h2>
                <p className="text-xs text-slate-500">
                  {employee.designation} · {employee.department}
                </p>
              </div>
              <button
                type="button"
                onClick={onClose}
                className="rounded-lg p-1.5 text-slate-500 transition hover:bg-slate-800 hover:text-slate-300"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto px-6 py-5">
              <RiskSummaryCard employee={employee} />

              <div className="mt-5 rounded-xl border border-slate-800 bg-slate-900/40 p-4">
                <p className="mb-1 text-xs font-medium uppercase tracking-wide text-slate-500">
                  Employee Details
                </p>
                <InfoRow icon={Mail} label="Email" value={employee.email} />
                <InfoRow
                  icon={Building2}
                  label="Department"
                  value={employee.department}
                />
                <InfoRow
                  icon={Briefcase}
                  label="Designation"
                  value={employee.designation}
                />
                <InfoRow
                  icon={Hash}
                  label="Employee Code"
                  value={employee.employee_code}
                />
              </div>

              <div className="mt-6">
                <p className="mb-3 text-xs font-medium uppercase tracking-wide text-slate-500">
                  Activity Timeline
                </p>
                <EmployeeActivityTimeline employeeId={employee.id} />
              </div>
            </div>

            <div className="flex items-center gap-3 border-t border-slate-800 px-6 py-4">
              <button
                type="button"
                onClick={() => onEdit(employee)}
                className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-slate-800"
              >
                <Pencil className="h-4 w-4" />
                Edit
              </button>
              <button
                type="button"
                onClick={() => onDelete(employee)}
                className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-red-900/60 bg-red-950/30 px-4 py-2 text-sm font-medium text-red-400 transition hover:bg-red-950/60"
              >
                <Trash2 className="h-4 w-4" />
                Delete
              </button>
            </div>
          </motion.aside>
        </div>
      )}
    </AnimatePresence>
  );
}
