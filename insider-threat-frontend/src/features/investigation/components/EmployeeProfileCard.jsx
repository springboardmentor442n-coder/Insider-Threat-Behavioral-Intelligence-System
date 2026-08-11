import { motion } from "framer-motion";

import {
  User,
  Building2,
  ShieldAlert,
  BriefcaseBusiness,
  CalendarDays,
  Clock,
  Hash,
} from "lucide-react";

function displayValue(value) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "Not available";
  }

  return value;
}

function formatDate(value) {
  if (!value) {
    return "Not available";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleString();
}

export default function EmployeeProfileCard({
  employee,
}) {
  if (!employee) {
    return null;
  }

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 15,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="
        rounded-2xl
        border
        border-cyan-500/20
        bg-slate-900/60
        p-6
        backdrop-blur-lg
      "
    >
      {/* ======================================================
          EMPLOYEE HEADER
      ======================================================= */}

      <div className="flex items-center gap-4">
        <div
          className="
            flex
            h-16
            w-16
            shrink-0
            items-center
            justify-center
            rounded-full
            bg-cyan-500/20
          "
        >
          <User
            className="text-cyan-400"
            size={30}
          />
        </div>

        <div className="min-w-0">
          <h2 className="truncate text-xl font-bold text-white">
            {displayValue(
              employee.employee ??
                employee.employee_name ??
                employee.user
            )}
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            {displayValue(
              employee.risk_level ??
                employee.prediction
            )}
          </p>
        </div>
      </div>

      {/* ======================================================
          DETAILS
      ======================================================= */}

      <div className="mt-6 space-y-5">

        {/* Employee Code */}

        <div className="flex items-center gap-3 text-slate-300">
          <Hash
            size={18}
            className="text-cyan-400"
          />

          <div>
            <p className="text-xs text-slate-500">
              Employee Code
            </p>

            <p className="font-medium">
              {displayValue(
                employee.user ??
                  employee.employee
              )}
            </p>
          </div>
        </div>

        {/* Department */}

        <div className="flex items-center gap-3 text-slate-300">
          <Building2
            size={18}
            className="text-cyan-400"
          />

          <div>
            <p className="text-xs text-slate-500">
              Department
            </p>

            <p className="font-medium">
              {displayValue(
                employee.department
              )}
            </p>
          </div>
        </div>

        {/* Assigned To */}

        <div className="flex items-center gap-3 text-slate-300">
          <BriefcaseBusiness
            size={18}
            className="text-cyan-400"
          />

          <div>
            <p className="text-xs text-slate-500">
              Assigned To
            </p>

            <p className="font-medium">
              {displayValue(
                employee.assigned_to
              )}
            </p>
          </div>
        </div>

        {/* Prediction */}

        <div className="flex items-center gap-3 text-slate-300">
          <ShieldAlert
            size={18}
            className="text-red-400"
          />

          <div>
            <p className="text-xs text-slate-500">
              Behavioral Prediction
            </p>

            <p
              className={`
                font-medium
                ${
                  employee.risk_level ===
                  "Critical"
                    ? "text-red-400"
                    : employee.risk_level ===
                        "High"
                      ? "text-orange-400"
                      : employee.risk_level ===
                          "Medium"
                        ? "text-yellow-400"
                        : "text-emerald-400"
                }
              `}
            >
              {displayValue(
                employee.prediction ??
                  employee.risk_level
              )}
            </p>
          </div>
        </div>

        {/* Created */}

        <div className="flex items-center gap-3 text-slate-300">
          <CalendarDays
            size={18}
            className="text-cyan-400"
          />

          <div>
            <p className="text-xs text-slate-500">
              Created
            </p>

            <p className="font-medium">
              {formatDate(
                employee.created_at
              )}
            </p>
          </div>
        </div>

        {/* Last Updated */}

        <div className="flex items-center gap-3 text-slate-300">
          <Clock
            size={18}
            className="text-cyan-400"
          />

          <div>
            <p className="text-xs text-slate-500">
              Last Updated
            </p>

            <p className="font-medium">
              {formatDate(
                employee.updated_at ??
                  employee.last_updated
              )}
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
