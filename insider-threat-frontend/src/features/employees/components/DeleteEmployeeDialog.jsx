import { AnimatePresence, motion } from "framer-motion";
import { AlertTriangle, X, Loader2, Trash2 } from "lucide-react";
import { useDeleteEmployee } from "../hooks/useEmployeeMutations";

export default function DeleteEmployeeDialog({ open, employee, onClose }) {
  const deleteEmployee = useDeleteEmployee();

  if (!employee) return null;

  const handleConfirm = () => {
    deleteEmployee.mutate(employee.id, {
      onSuccess: onClose,
    });
  };

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm"
            onClick={deleteEmployee.isPending ? undefined : onClose}
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 12 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 12 }}
            transition={{ duration: 0.18, ease: "easeOut" }}
            className="relative w-full max-w-md overflow-hidden rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl shadow-red-950/30"
          >
            <div className="flex items-center justify-between border-b border-slate-800 px-6 py-4">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-red-500/10 p-2 text-red-400">
                  <AlertTriangle className="h-5 w-5" />
                </div>
                <h2 className="text-sm font-semibold text-slate-100">
                  Delete Employee
                </h2>
              </div>
              <button
                type="button"
                onClick={onClose}
                disabled={deleteEmployee.isPending}
                className="rounded-lg p-1.5 text-slate-500 transition hover:bg-slate-800 hover:text-slate-300 disabled:opacity-40"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="px-6 py-5">
              <p className="text-sm text-slate-300">
                This will permanently remove{" "}
                <span className="font-semibold text-slate-100">
                  {employee.full_name}
                </span>{" "}
                <span className="text-slate-500">
                  ({employee.employee_code})
                </span>{" "}
                from the system, including all associated risk history. This
                action cannot be undone.
              </p>
            </div>

            <div className="flex items-center justify-end gap-3 border-t border-slate-800 px-6 py-4">
              <button
                type="button"
                onClick={onClose}
                disabled={deleteEmployee.isPending}
                className="rounded-lg px-4 py-2 text-sm font-medium text-slate-400 transition hover:bg-slate-800 hover:text-slate-200 disabled:opacity-40"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirm}
                disabled={deleteEmployee.isPending}
                className="flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {deleteEmployee.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Trash2 className="h-4 w-4" />
                )}
                {deleteEmployee.isPending ? "Deleting..." : "Delete employee"}
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
