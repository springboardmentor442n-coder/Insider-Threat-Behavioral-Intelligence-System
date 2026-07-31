import { useState } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import {
  PlayCircle,
  Database,
  Brain,
  CheckCircle,
  AlertCircle,
  FileText,
  Users,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react";

import Layout from "../components/Layout";

export default function Pipeline() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const [message, setMessage] = useState("");
  const [isSuccess, setIsSuccess] = useState(false);

  const [lastRun, setLastRun] = useState("");

  const runPipeline = async () => {
    try {
      setLoading(true);
      setMessage("");
      setResult(null);

      const response = await axios.post(
        "http://127.0.0.1:8000/run-pipeline"
      );

      setResult(response.data);

      setMessage(
        "Pipeline completed successfully. Predictions have been generated."
      );

      setIsSuccess(true);

      setLastRun(new Date().toLocaleString());
    } catch (err) {
      console.error(err);

      setMessage(
        "Pipeline execution failed. Please check the data source and try again."
      );

      setIsSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout title="Threat Detection Pipeline">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-4xl font-bold text-white">
          Threat Detection Pipeline
        </h1>

        <p className="mt-2 text-slate-400">
          Run the behavioral analysis pipeline to process employee activity and
          generate insider threat predictions.
        </p>
      </motion.div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        {/* Pipeline Status */}

        <div className="rounded-2xl border border-slate-700 bg-slate-900 p-8 shadow-xl">
          <h2 className="mb-6 text-2xl font-bold text-white">
            Pipeline Status
          </h2>

          <div className="space-y-6">
            <div className="flex items-center gap-4">
              <Database className="text-cyan-400" />

              <div>
                <p className="text-slate-400">Data Source</p>
                <p className="font-semibold text-green-400">Ready</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <Brain className="text-cyan-400" />

              <div>
                <p className="text-slate-400">AI Model</p>
                <p className="font-semibold text-white">
                  Random Forest
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <CheckCircle className="text-green-400" />

              <div>
                <p className="text-slate-400">Status</p>
                <p className="font-semibold text-green-400">
                  Ready to Run
                </p>
              </div>
            </div>
          </div>

          <button
            onClick={runPipeline}
            disabled={loading}
            className="mt-8 flex w-full items-center justify-center gap-3 rounded-xl bg-cyan-600 px-6 py-4 font-semibold text-white transition hover:bg-cyan-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <PlayCircle size={22} />

            {loading ? "Running Pipeline..." : "Run Pipeline"}
          </button>
        </div>

        {/* Status Message */}

        <div className="rounded-2xl border border-slate-700 bg-slate-900 p-8 shadow-xl">
          <h2 className="mb-6 text-2xl font-bold text-white">
            Execution Status
          </h2>

          {message ? (
            <div
              className={`rounded-xl p-5 ${
                isSuccess
                  ? "border border-green-600 bg-green-500/10"
                  : "border border-red-600 bg-red-500/10"
              }`}
            >
              <div className="flex items-center gap-3">
                {isSuccess ? (
                  <CheckCircle className="text-green-400" />
                ) : (
                  <AlertCircle className="text-red-400" />
                )}

                <span
                  className={
                    isSuccess ? "text-green-300" : "text-red-300"
                  }
                >
                  {message}
                </span>
              </div>
            </div>
          ) : (
            <p className="text-slate-400">
              The pipeline is ready. Click the button to begin
              processing.
            </p>
          )}

          {lastRun && (
            <div className="mt-8 rounded-xl bg-slate-800 p-4">
              <p className="text-sm text-slate-400">
                Last Run
              </p>

              <p className="mt-1 font-medium text-white">
                {lastRun}
              </p>
            </div>
          )}
        </div>
      </div>

      {result && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-8 grid gap-6 md:grid-cols-2 xl:grid-cols-5"
        >
          <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6">
            <FileText className="mb-4 text-cyan-400" />
            <p className="text-slate-400">Rows Processed</p>
            <h2 className="mt-2 text-3xl font-bold text-white">
              {Number(result.rows_processed).toLocaleString()}
            </h2>
          </div>

          <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6">
            <Users className="mb-4 text-cyan-400" />
            <p className="text-slate-400">Employees</p>
            <h2 className="mt-2 text-3xl font-bold text-white">
              {Number(result.employees_imported).toLocaleString()}
            </h2>
          </div>

          <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6">
            <ShieldAlert className="mb-4 text-red-400" />
            <p className="text-slate-400">High Risk</p>
            <h2 className="mt-2 text-3xl font-bold text-red-400">
              {Number(result.high_risk).toLocaleString()}
            </h2>
          </div>

          <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6">
            <ShieldCheck className="mb-4 text-green-400" />
            <p className="text-slate-400">Low Risk</p>
            <h2 className="mt-2 text-3xl font-bold text-green-400">
              {Number(result.low_risk).toLocaleString()}
            </h2>
          </div>

          <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6">
            <Brain className="mb-4 text-cyan-400" />
            <p className="text-slate-400">Predictions Saved</p>
            <h2 className="mt-2 text-3xl font-bold text-white">
              {Number(result.predictions_saved).toLocaleString()}
            </h2>
          </div>
        </motion.div>
      )}
    </Layout>
  );
}