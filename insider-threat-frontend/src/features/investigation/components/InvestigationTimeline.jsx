import { motion } from "framer-motion";

import {
  AlertTriangle,
  CheckCircle2,
  CircleAlert,
  ShieldAlert,
  Activity,
} from "lucide-react";

/*
|--------------------------------------------------------------------------
| ML MODEL DEFINITIONS
|--------------------------------------------------------------------------
|
| These names and fields correspond to the seven anomaly detection
| models already produced by the backend ML pipeline.
|
|--------------------------------------------------------------------------
*/

const MODEL_DEFINITIONS = [
  {
    key: "isolation_forest",
    name: "Isolation Forest",
    predictionKey: "isolation_forest_prediction",
    scoreKey: "isolation_forest_score",
  },
  {
    key: "one_class_svm",
    name: "One-Class SVM",
    predictionKey: "one_class_svm_prediction",
    scoreKey: "one_class_svm_score",
  },
  {
    key: "lof",
    name: "LOF",
    predictionKey: "lof_prediction",
    scoreKey: "lof_score",
  },
  {
    key: "elliptic_envelope",
    name: "Elliptic Envelope",
    predictionKey: "elliptic_envelope_prediction",
    scoreKey: "elliptic_envelope_score",
  },
  {
    key: "pca",
    name: "PCA",
    predictionKey: "pca_prediction",
    scoreKey: "pca_score",
  },
  {
    key: "dbscan",
    name: "DBSCAN",
    predictionKey: "dbscan_prediction",
    scoreKey: "dbscan_score",
  },
  {
    key: "kmeans",
    name: "K-Means",
    predictionKey: "kmeans_prediction",
    scoreKey: "kmeans_score",
  },
];

/*
|--------------------------------------------------------------------------
| Helpers
|--------------------------------------------------------------------------
*/

function isSuspicious(prediction) {
  return (
    String(prediction ?? "")
      .trim()
      .toLowerCase() === "suspicious"
  );
}

function formatScore(score) {
  if (
    score === null ||
    score === undefined ||
    score === ""
  ) {
    return "—";
  }

  const numeric = Number(score);

  if (!Number.isFinite(numeric)) {
    return String(score);
  }

  return numeric.toFixed(4);
}

/*
|--------------------------------------------------------------------------
| Model Result Card
|--------------------------------------------------------------------------
*/

function ModelResultCard({
  model,
  prediction,
  score,
  index,
}) {
  const suspicious = isSuspicious(prediction);

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 8,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      transition={{
        duration: 0.2,
        delay: index * 0.04,
      }}
      className={`
        rounded-xl
        border
        p-4
        transition-all
        ${
          suspicious
            ? `
              border-red-500/30
              bg-red-500/[0.045]
              hover:border-red-500/50
            `
            : `
              border-slate-700
              bg-slate-800/40
              hover:border-cyan-500/30
            `
        }
      `}
    >
      <div className="flex items-center justify-between gap-4">
        <div className="flex min-w-0 items-center gap-3">
          <div
            className={`
              flex
              h-9
              w-9
              shrink-0
              items-center
              justify-center
              rounded-lg
              ${
                suspicious
                  ? "bg-red-500/10"
                  : "bg-emerald-500/10"
              }
            `}
          >
            {suspicious ? (
              <CircleAlert
                size={18}
                className="text-red-400"
              />
            ) : (
              <CheckCircle2
                size={18}
                className="text-emerald-400"
              />
            )}
          </div>

          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-slate-200">
              {model.name}
            </p>

            <p className="mt-0.5 text-xs text-slate-500">
              Model score
            </p>
          </div>
        </div>

        <div className="shrink-0 text-right">
          <p
            className={`
              text-sm
              font-semibold
              ${
                suspicious
                  ? "text-red-400"
                  : "text-emerald-400"
              }
            `}
          >
            {suspicious
              ? "Suspicious"
              : "Normal"}
          </p>

          <p className="mt-0.5 font-mono text-xs text-slate-500">
            {formatScore(score)}
          </p>
        </div>
      </div>
    </motion.div>
  );
}

/*
|--------------------------------------------------------------------------
| Investigation Timeline / ML Evidence
|--------------------------------------------------------------------------
*/

export default function InvestigationTimeline({
  employee,
  timeline = [],
}) {
  /*
  |--------------------------------------------------------------------------
  | Build model results from the selected employee
  |--------------------------------------------------------------------------
  */

  const modelResults = employee
    ? MODEL_DEFINITIONS.map((model) => ({
        ...model,
        prediction:
          employee[model.predictionKey],
        score:
          employee[model.scoreKey],
      }))
    : [];

  const availableModels = modelResults.filter(
    (model) =>
      model.prediction !== null &&
      model.prediction !== undefined
  );

  /*
  |--------------------------------------------------------------------------
  | Suspicious model count
  |--------------------------------------------------------------------------
  */

  const suspiciousModels =
    availableModels.filter((model) =>
      isSuspicious(model.prediction)
    );

  /*
  |--------------------------------------------------------------------------
  | If ML model data is unavailable
  |--------------------------------------------------------------------------
  */

  if (!employee || availableModels.length === 0) {
    return (
      <div
        className="
          rounded-2xl
          border
          border-slate-700
          bg-slate-900/60
          p-6
        "
      >
        <div className="flex items-center gap-3">
          <ShieldAlert
            size={22}
            className="text-cyan-400"
          />

          <h2 className="text-xl font-semibold text-white">
            Investigation Evidence
          </h2>
        </div>

        <div
          className="
            mt-5
            rounded-xl
            border
            border-slate-700
            bg-slate-800/40
            p-5
          "
        >
          <p className="text-slate-400">
            No ML model evidence is available for this
            investigation.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      className="
        rounded-2xl
        border
        border-slate-700
        bg-slate-900/60
        p-6
      "
    >
      {/* ======================================================
          HEADER
      ======================================================= */}

      <div
        className="
          mb-5
          flex
          flex-wrap
          items-center
          justify-between
          gap-4
        "
      >
        <div className="flex items-center gap-3">
          <div
            className="
              flex
              h-10
              w-10
              items-center
              justify-center
              rounded-xl
              bg-cyan-500/10
            "
          >
            <Activity
              size={21}
              className="text-cyan-400"
            />
          </div>

          <div>
            <h2 className="text-xl font-semibold text-white">
              ML Model Results
            </h2>

            <p className="mt-0.5 text-xs text-slate-500">
              Seven-model behavioral intelligence analysis
            </p>
          </div>
        </div>

        {/* Consensus badge */}

        <div
          className="
            flex
            items-center
            gap-3
            rounded-xl
            border
            border-cyan-500/20
            bg-cyan-500/5
            px-4
            py-2
          "
        >
          <div className="text-right">
            <p className="text-[11px] uppercase tracking-wide text-slate-500">
              Consensus
            </p>

            <p className="text-lg font-bold text-cyan-400">
              {Number(
                employee.consensus_percentage ?? 0
              ).toFixed(1)}
              %
            </p>
          </div>

          <div className="h-8 w-px bg-slate-700" />

          <div>
            <p className="text-[11px] uppercase tracking-wide text-slate-500">
              Suspicious
            </p>

            <p className="text-lg font-bold text-red-400">
              {suspiciousModels.length}/
              {availableModels.length}
            </p>
          </div>
        </div>
      </div>

      {/* ======================================================
          MODEL GRID
      ======================================================= */}

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {availableModels.map(
          (model, index) => (
            <ModelResultCard
              key={model.key}
              model={model}
              prediction={model.prediction}
              score={model.score}
              index={index}
            />
          )
        )}
      </div>

      {/* ======================================================
          WEIGHTED SCORE
      ======================================================= */}

      <div
        className="
          mt-5
          rounded-xl
          border
          border-cyan-500/20
          bg-cyan-500/[0.04]
          p-4
        "
      >
        <div
          className="
            flex
            flex-wrap
            items-center
            justify-between
            gap-4
          "
        >
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">
              Weighted Risk Score
            </p>

            <p className="mt-1 text-sm text-slate-400">
              Combined score produced by the behavioral
              intelligence ensemble.
            </p>
          </div>

          <p className="text-2xl font-bold text-cyan-400">
            {Number(
              employee.weighted_score ??
                employee.risk_score ??
                0
            ).toFixed(2)}
          </p>
        </div>
      </div>

      {/* ======================================================
          ADDITIONAL EVIDENCE
      ======================================================= */}

      {timeline.length > 0 && (
        <div className="mt-6">
          <div className="mb-3 flex items-center gap-2">
            <AlertTriangle
              size={18}
              className="text-red-400"
            />

            <h3 className="text-sm font-semibold text-slate-200">
              Behavioral Evidence
            </h3>

            <span
              className="
                rounded-full
                bg-red-500/10
                px-2.5
                py-1
                text-xs
                text-red-400
              "
            >
              {timeline.length}
            </span>
          </div>

          <div className="space-y-3">
            {timeline.map(
              (item, index) => (
                <motion.div
                  key={`${String(item)}-${index}`}
                  initial={{
                    opacity: 0,
                    x: 8,
                  }}
                  animate={{
                    opacity: 1,
                    x: 0,
                  }}
                  transition={{
                    duration: 0.2,
                    delay: index * 0.04,
                  }}
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
                  <div
                    className="
                      mt-0.5
                      flex
                      h-9
                      w-9
                      shrink-0
                      items-center
                      justify-center
                      rounded-lg
                      bg-red-500/10
                    "
                  >
                    <AlertTriangle
                      size={18}
                      className="text-red-400"
                    />
                  </div>

                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-slate-200">
                      {String(item)}
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      Behavioral evidence associated with this
                      investigation.
                    </p>
                  </div>
                </motion.div>
              )
            )}
          </div>
        </div>
      )}
    </div>
  );
}
