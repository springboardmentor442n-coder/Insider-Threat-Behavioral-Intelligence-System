import { AnimatePresence, motion } from "framer-motion";
import {
  CheckCircle2,
  AlertTriangle,
  ShieldCheck,
} from "lucide-react";

import { useResolveThreat } from "../hooks/useThreatMutations";

export default function ResolveThreatDialog({
  open,
  threat,
  onClose,
}) {
  const resolve = useResolveThreat();

  if (!open || !threat) return null;

  function handleResolve() {
    resolve.mutate(threat.id, {
      onSuccess() {
        onClose();
      },
    });
  }

  return (
    <AnimatePresence>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="
          fixed
          inset-0
          z-[80]

          flex
          items-center
          justify-center

          bg-black/70
          backdrop-blur-md

          p-5
        "
      >

        <motion.div
          initial={{
            scale: .8,
            opacity:0,
          }}

          animate={{
            scale:1,
            opacity:1,
          }}

          exit={{
            scale:.9,
            opacity:0,
          }}

          className="
            w-full

            max-w-xl

            rounded-3xl

            border

            border-cyan-500/20

            bg-slate-950/90

            backdrop-blur-2xl

            shadow-[0_0_80px_rgba(6,182,212,.15)]
          "
        >

          {/* Header */}

          <div className="border-b border-white/10 p-8">

            <div className="flex items-center gap-5">

              <div
                className="
                  rounded-full

                  bg-green-500/15

                  p-5
                "
              >
                <ShieldCheck
                  className="text-green-400"
                  size={34}
                />
              </div>

              <div>

                <h2 className="text-3xl font-bold">

                  Resolve Threat

                </h2>

                <p className="text-slate-400">

                  Confirm investigation closure

                </p>

              </div>

            </div>

          </div>

          {/* Body */}

          <div className="space-y-6 p-8">

            <div
              className="
                rounded-2xl

                border

                border-white/10

                bg-white/5

                p-6
              "
            >

              <div className="grid grid-cols-2 gap-5">

                <div>

                  <p className="text-slate-400">

                    Employee

                  </p>

                  <h3 className="font-semibold">

                    {threat.employee_name}

                  </h3>

                </div>

                <div>

                  <p className="text-slate-400">

                    Risk Score

                  </p>

                  <h3 className="text-red-400 text-2xl font-bold">

                    {threat.risk_score}

                  </h3>

                </div>

                <div>

                  <p className="text-slate-400">

                    Department

                  </p>

                  <h3>

                    {threat.department}

                  </h3>

                </div>

                <div>

                  <p className="text-slate-400">

                    Severity

                  </p>

                  <h3>

                    {threat.severity}

                  </h3>

                </div>

              </div>

            </div>

            <div
              className="
                flex

                gap-4

                rounded-2xl

                border

                border-yellow-500/30

                bg-yellow-500/10

                p-5
              "
            >

              <AlertTriangle
                className="text-yellow-400"
              />

              <p>

                This investigation will be marked as

                <strong>

                  {" "}Resolved

                </strong>

                but will remain available for future audits.

              </p>

            </div>

          </div>

          {/* Footer */}

          <div className="flex justify-end gap-4 border-t border-white/10 p-8">

            <button
              onClick={onClose}
              className="
                rounded-xl

                bg-slate-700

                px-6

                py-3

                hover:bg-slate-600
              "
            >
              Cancel
            </button>

            <button
              onClick={handleResolve}
              disabled={resolve.isPending}
              className="
                rounded-xl

                bg-green-600

                px-6

                py-3

                font-semibold

                transition

                hover:bg-green-700
              "
            >

              {resolve.isPending
                ? "Resolving..."
                : "Resolve Threat"}

            </button>

          </div>

        </motion.div>

      </motion.div>

    </AnimatePresence>
  );
}
