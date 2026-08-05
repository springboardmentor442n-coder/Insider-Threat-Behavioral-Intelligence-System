import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X, Pencil, Loader2 } from "lucide-react";
import { useUpdateEmployee } from "../hooks/useEmployeeMutations";
import EmployeeFormFields, {
  validateEmployeeForm,
} from "./EmployeeFormFields";

function toFormValues(employee) {
  return {
    full_name: employee?.full_name ?? "",
    email: employee?.email ?? "",
    employee_code: employee?.employee_code ?? "",
    department: employee?.department ?? "",
    designation: employee?.designation ?? "",
    risk_score: employee?.risk_score?.toString() ?? "",
    risk_level: employee?.risk_level ?? "low",
  };
}

export default function EditEmployeeDialog({ open, employee, onClose }) {
  const [values, setValues] = useState(toFormValues(employee));
  const [errors, setErrors] = useState({});
  const updateEmployee = useUpdateEmployee();

  // Resync form state whenever a different employee is opened for editing.
  useEffect(() => {
    if (open) {
      setValues(toFormValues(employee));
      setErrors({});
    }
  }, [open, employee]);

  const handleChange = (field, value) => {
    setValues((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const validationErrors = validateEmployeeForm(values);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    updateEmployee.mutate(
      {
        id: employee.id,
        payload: {
          ...values,
          risk_score: Number(values.risk_score),
        },
      },
      {
        onSuccess: onClose,
      }
    );
  };

  if (!employee) return null;

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm"
            onClick={updateEmployee.isPending ? undefined : onClose}
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 12 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 12 }}
            transition={{ duration: 0.18, ease: "easeOut" }}
            className="relative w-full max-w-2xl overflow-hidden rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl shadow-cyan-950/40"
          >
            <div className="flex items-center justify-between border-b border-slate-800 px-6 py-4">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-amber-500/10 p-2 text-amber-400">
                  <Pencil className="h-5 w-5" />
                </div>
                <div>
                  <h2 className="text-sm font-semibold text-slate-100">
                    Edit Employee
                  </h2>
                  <p className="text-xs text-slate-500">
                    {employee.employee_code} · {employee.full_name}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={onClose}
                disabled={updateEmployee.isPending}
                className="rounded-lg p-1.5 text-slate-500 transition hover:bg-slate-800 hover:text-slate-300 disabled:opacity-40"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="px-6 py-5">
              <EmployeeFormFields
                values={values}
                errors={errors}
                onChange={handleChange}
                disabled={updateEmployee.isPending}
              />

              <div className="mt-6 flex items-center justify-end gap-3 border-t border-slate-800 pt-4">
                <button
                  type="button"
                  onClick={onClose}
                  disabled={updateEmployee.isPending}
                  className="rounded-lg px-4 py-2 text-sm font-medium text-slate-400 transition hover:bg-slate-800 hover:text-slate-200 disabled:opacity-40"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updateEmployee.isPending}
                  className="flex items-center gap-2 rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-amber-400 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {updateEmployee.isPending && (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  )}
                  {updateEmployee.isPending ? "Saving..." : "Save changes"}
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
