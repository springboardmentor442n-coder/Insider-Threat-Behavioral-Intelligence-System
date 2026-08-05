import { AnimatePresence, motion } from "framer-motion";
import {
  Trash2,
  AlertTriangle,
} from "lucide-react";

import { useDeleteThreat } from "../hooks/useThreatMutations";

export default function DeleteThreatDialog({
  open,
  threat,
  onClose,
}) {
  const remove = useDeleteThreat();

  if (!open || !threat) return null;

  function handleDelete() {
    remove.mutate(threat.id, {
      onSuccess() {
        onClose();
      },
    });
  }

  return (
    <AnimatePresence>

      <motion.div

        initial={{opacity:0}}

        animate={{opacity:1}}

        exit={{opacity:0}}

        className="
          fixed
          inset-0
          z-[90]

          flex
          items-center
          justify-center

          bg-black/75

          backdrop-blur-md

          p-5
        "

      >

        <motion.div

          initial={{
            scale:.85,
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

            border-red-500/30

            bg-slate-950/90

            backdrop-blur-2xl

            shadow-[0_0_80px_rgba(239,68,68,.15)]
          "

        >

          {/* Header */}

          <div className="border-b border-white/10 p-8">

            <div className="flex items-center gap-5">

              <div
                className="
                  rounded-full

                  bg-red-500/15

                  p-5
                "
              >

                <Trash2
                  size={34}
                  className="text-red-400"
                />

              </div>

              <div>

                <h2 className="text-3xl font-bold">

                  Delete Threat

                </h2>

                <p className="text-slate-400">

                  Permanent operation

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

              <p className="text-slate-400">

                Employee

              </p>

              <h2 className="text-2xl font-bold">

                {threat.employee_name}

              </h2>

              <div className="mt-6 grid grid-cols-2 gap-5">

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

                    Risk

                  </p>

                  <h3 className="text-red-400 text-2xl font-bold">

                    {threat.risk_score}

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

                border-red-500/30

                bg-red-500/10

                p-5
              "
            >

              <AlertTriangle
                className="text-red-400"
              />

              <p>

                This action permanently removes this threat record.

                <strong>

                  {" "}This cannot be undone.

                </strong>

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
              onClick={handleDelete}
              disabled={remove.isPending}
              className="
                rounded-xl

                bg-red-600

                px-6

                py-3

                font-semibold

                transition

                hover:bg-red-700
              "
            >

              {remove.isPending
                ? "Deleting..."
                : "Delete Threat"}

            </button>

          </div>

        </motion.div>

      </motion.div>

    </AnimatePresence>
  );
}
