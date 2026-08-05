import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X, UserPlus, Loader2 } from "lucide-react";

import { useCreateEmployee } from "../hooks/useEmployeeMutations";
import EmployeeFormFields, {
  validateEmployeeForm,
} from "./EmployeeFormFields";

const EMPTY_FORM = {
  employee_code: "",
  full_name: "",
  email: "",
  department: "",
  designation: "",
  risk_score: "",
  risk_level: "low",
};

export default function AddEmployeeDialog({ open, onClose }) {
  const createEmployee = useCreateEmployee();

  const [values, setValues] = useState(EMPTY_FORM);
  const [errors, setErrors] = useState({});

  const handleChange = (field, value) => {
    setValues((prev) => ({
      ...prev,
      [field]: value,
    }));

    if (errors[field]) {
      setErrors((prev) => ({
        ...prev,
        [field]: undefined,
      }));
    }
  };

  const resetForm = () => {
    setValues(EMPTY_FORM);
    setErrors({});
  };

  const handleClose = () => {
    if (createEmployee.isPending) return;

    resetForm();
    onClose();
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const validationErrors = validateEmployeeForm(values);

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    createEmployee.mutate(
      {
        ...values,
        risk_score: Number(values.risk_score),
      },
      {
        onSuccess: () => {
          resetForm();
          onClose();
        },
      }
    );
  };

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">

          {/* Background */}
          <motion.div
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
          />

          {/* Dialog */}
          <motion.div
            initial={{
              opacity: 0,
              y: 20,
              scale: 0.97,
            }}
            animate={{
              opacity: 1,
              y: 0,
              scale: 1,
            }}
            exit={{
              opacity: 0,
              y: 20,
              scale: 0.97,
            }}
            transition={{
              duration: 0.2,
            }}
            className="relative w-full max-w-2xl rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl"
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-slate-800 px-6 py-4">
              <div className="flex items-center gap-3">

                <div className="rounded-lg bg-cyan-500/10 p-2 text-cyan-400">
                  <UserPlus className="h-5 w-5" />
                </div>

                <div>
                  <h2 className="text-lg font-semibold text-white">
                    Add Employee
                  </h2>

                  <p className="text-sm text-slate-400">
                    Create a new employee
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={handleClose}
                disabled={createEmployee.isPending}
                className="rounded-lg p-2 text-slate-400 hover:bg-slate-800"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Form */}
            <form
              onSubmit={handleSubmit}
              className="space-y-6 p-6"
            >
              <EmployeeFormFields
                values={values}
                errors={errors}
                onChange={handleChange}
                disabled={createEmployee.isPending}
              />

              <div className="flex justify-end gap-3 border-t border-slate-800 pt-5">

                <button
                  type="button"
                  onClick={handleClose}
                  disabled={createEmployee.isPending}
                  className="rounded-lg border border-slate-700 px-5 py-2 text-slate-300 hover:bg-slate-800"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={createEmployee.isPending}
                  className="flex items-center gap-2 rounded-lg bg-cyan-500 px-5 py-2 font-semibold text-slate-950 hover:bg-cyan-400 disabled:opacity-60"
                >
                  {createEmployee.isPending && (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  )}

                  {createEmployee.isPending
                    ? "Adding..."
                    : "Add Employee"}
                </button>

              </div>
            </form>

          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
