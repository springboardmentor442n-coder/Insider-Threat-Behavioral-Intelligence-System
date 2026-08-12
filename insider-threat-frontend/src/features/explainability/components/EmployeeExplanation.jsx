import { motion } from "framer-motion";
import {
  UserSearch,
  ShieldAlert,
  BrainCircuit,
  CheckCircle,
} from "lucide-react";
import { formatPercent, formatScore } from "../../../utils/formatters";

export default function EmployeeExplanation({
  explanation,
}) {
  if (!explanation) {
    return (
      <section
        className="
          rounded-2xl
          border border-slate-700
          bg-slate-900/60
          p-6
        "
      >
        <div className="flex items-center gap-3">
          <UserSearch
            className="text-cyan-400"
            size={22}
          />

          <h2 className="text-xl font-semibold text-white">
            Employee Explanation
          </h2>
        </div>

        <p className="mt-4 text-slate-400">
          Enter an employee ID to view its explainability
          report.
        </p>
      </section>
    );
  }

  const explanations =
    explanation.Explanation
      ? explanation.Explanation.split("|")
          .map((item) => item.trim())
          .filter(Boolean)
      : [];

  return (
    <motion.section
      initial={{
        opacity: 0,
        y: 10,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="
        rounded-2xl
        border border-cyan-500/20
        bg-slate-900/60
        p-6
      "
    >
      <div className="flex items-center gap-3">
        <UserSearch
          className="text-cyan-400"
          size={22}
        />

        <h2 className="text-xl font-semibold text-white">
          Employee Explanation
        </h2>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-slate-700 bg-slate-800/40 p-4">
          <p className="text-xs text-slate-500">
            Employee
          </p>

          <p className="mt-1 font-semibold text-white">
            {explanation.user}
          </p>
        </div>

        <div className="rounded-xl border border-slate-700 bg-slate-800/40 p-4">
          <p className="text-xs text-slate-500">
            Risk Level
          </p>

          <p className="mt-1 font-semibold text-red-400">
            {explanation.risk_level}
          </p>
        </div>

        <div className="rounded-xl border border-slate-700 bg-slate-800/40 p-4">
          <p className="text-xs text-slate-500">
            Weighted Score
          </p>

          <p className="mt-1 font-semibold text-orange-400">
            {formatScore(explanation.weighted_score)}
          </p>
        </div>
      </div>

      <div className="mt-4 rounded-xl border border-slate-700 bg-slate-800/40 p-4">
        <div className="flex items-center gap-3">
          <BrainCircuit
            size={20}
            className="text-purple-400"
          />

          <div>
            <p className="text-xs text-slate-500">
              Consensus
            </p>

            <p className="font-semibold text-purple-400">
              {formatPercent(explanation.Consensus_Percentage)}
            </p>
          </div>
        </div>
      </div>

      <div className="mt-6">
        <h3 className="mb-4 font-semibold text-white">
          Behavioral Explanation
        </h3>

        <div className="space-y-3">
          {explanations.map((item, index) => (
            <div
              key={`${item}-${index}`}
              className="
                flex
                items-start
                gap-3
                rounded-xl
                border
                border-slate-700
                bg-slate-800/40
                p-4
              "
            >
              <CheckCircle
                size={19}
                className="mt-0.5 shrink-0 text-cyan-400"
              />

              <p className="text-sm text-slate-300">
                {item}
              </p>
            </div>
          ))}
        </div>
      </div>
    </motion.section>
  );
}
