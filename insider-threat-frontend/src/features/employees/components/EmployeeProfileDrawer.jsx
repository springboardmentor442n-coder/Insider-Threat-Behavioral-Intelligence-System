import { AnimatePresence, motion } from "framer-motion";
import {
  X,
  Mail,
  Building2,
  Briefcase,
  Hash,
  Pencil,
  Trash2,
} from "lucide-react";

import RiskSummaryCard from "./RiskSummaryCard";
import EmployeeActivityTimeline from "./EmployeeActivityTimeline";

function InfoRow({ icon: Icon, label, value }) {
  return (
    <div className="flex items-start gap-3 border-b border-slate-800/70 py-3 last:border-b-0">
      <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-slate-800/70">
        <Icon className="h-4 w-4 text-cyan-400" />
      </div>

      <div className="min-w-0 flex-1">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
          {label}
        </p>

        <p className="mt-1 break-words text-sm text-slate-200">
          {value || "—"}
        </p>
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
        <div className="fixed inset-0 z-[9999] overflow-hidden">
          {/* =====================================================
              FULL SCREEN BACKDROP
              ===================================================== */}

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.18 }}
            className="absolute inset-0 bg-black/70 backdrop-blur-md"
            onClick={onClose}
          />

          {/* =====================================================
              EMPLOYEE DRAWER

              IMPORTANT:
              vw is intentional.

              Unlike fixed px widths, vw keeps the visual
              proportion stable when Chrome zoom changes.
              ===================================================== */}

          <motion.aside
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{
              type: "spring",
              stiffness: 320,
              damping: 32,
            }}
            onClick={(e) => e.stopPropagation()}
            className="
              absolute
              right-0
              top-0
              bottom-0

              flex
              flex-col

              w-[52vw]
              max-w-[52vw]
              min-w-[620px]

              overflow-hidden

              border-l
              border-slate-800

              bg-slate-950

              shadow-2xl
              shadow-black/60
            "
          >
            {/* =================================================
                HEADER
                ================================================= */}

            <div
              className="
                flex
                shrink-0
                items-start
                justify-between
                gap-4

                border-b
                border-slate-800

                px-8
                py-6
              "
            >
              <div className="min-w-0">
                <p className="text-xs font-semibold uppercase tracking-wide text-cyan-400">
                  CERT Employee Intelligence
                </p>

                <h2 className="mt-1 truncate text-2xl font-bold text-white">
                  {employee.user ||
                    employee.employee_code ||
                    employee.full_name ||
                    "Employee"}
                </h2>
              </div>

              <button
                type="button"
                onClick={onClose}
                aria-label="Close employee profile"
                className="
                  flex
                  h-11
                  w-11
                  shrink-0
                  items-center
                  justify-center

                  rounded-xl

                  border
                  border-slate-700

                  bg-slate-900/70

                  text-slate-400

                  transition-all
                  duration-200

                  hover:border-cyan-500/30
                  hover:bg-slate-800
                  hover:text-white
                "
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* =================================================
                CONTENT
                ================================================= */}

            <div
              className="
                min-h-0
                flex-1

                overflow-y-auto
                overflow-x-hidden

                px-8
                py-6

                scrollbar-thin
                scrollbar-thumb-cyan-500/20
                scrollbar-track-transparent
              "
            >
              <RiskSummaryCard employee={employee} />

              {/* EMPLOYEE DETAILS */}

              <div
                className="
                  mt-6
                  rounded-2xl

                  border
                  border-slate-800

                  bg-slate-900/40

                  p-5
                "
              >
                <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
                  Employee Details
                </p>

                <InfoRow
                  icon={Mail}
                  label="Email"
                  value={employee.email}
                />

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
                  value={
                    employee.employee_code ||
                    employee.user
                  }
                />
              </div>

              {/* ACTIVITY TIMELINE */}

              <div className="mt-6">
                <p className="mb-3 text-xs font-medium uppercase tracking-wide text-slate-500">
                  Activity Timeline
                </p>

                <EmployeeActivityTimeline
                  employeeId={
                    employee.id ||
                    employee.user
                  }
                />
              </div>
            </div>

            {/* =================================================
                FOOTER
                ================================================= */}

            <div
              className="
                flex
                shrink-0
                items-center
                gap-3

                border-t
                border-slate-800

                bg-slate-950

                px-8
                py-4
              "
            >
              <button
                type="button"
                onClick={() => onEdit(employee)}
                className="
                  flex
                  flex-1
                  items-center
                  justify-center
                  gap-2

                  rounded-xl

                  border
                  border-slate-700

                  bg-slate-900

                  px-4
                  py-2.5

                  text-sm
                  font-medium
                  text-slate-200

                  transition-all

                  hover:border-cyan-500/30
                  hover:bg-slate-800
                  hover:text-white
                "
              >
                <Pencil className="h-4 w-4" />
                Edit
              </button>

              <button
                type="button"
                onClick={() => onDelete(employee)}
                className="
                  flex
                  flex-1
                  items-center
                  justify-center
                  gap-2

                  rounded-xl

                  border
                  border-red-900/60

                  bg-red-950/30

                  px-4
                  py-2.5

                  text-sm
                  font-medium
                  text-red-400

                  transition-all

                  hover:border-red-800
                  hover:bg-red-950/60
                  hover:text-red-300
                "
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
