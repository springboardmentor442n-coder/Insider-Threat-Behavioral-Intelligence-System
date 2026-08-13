import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  X,
  UserPlus,
  Play,
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  Cpu,
  Activity,
  HardDrive,
  Clock,
  Globe,
  Mail,
  Sliders,
  Sparkles,
  Loader2,
  Save,
} from "lucide-react";

// Quick-Fill Presets
const PRESETS = {
  normal: {
    label: "Standard Low-Risk Profile",
    badgeColor: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    data: {
      user: "EMP_NORM_01",
      name: "Sarah Connor",
      department: "Marketing",
      role: "Content Specialist",
      after_hours_activity: 5,
      midnight_activity: 0,
      weekend_activity: 2,
      device_events: 1,
      file_events: 5,
      unique_files: 3,
      unique_pcs: 1,
      web_events: 450,
      unique_urls: 40,
      emails_sent: 45,
      total_events: 600,
    },
  },
  exfiltration: {
    label: "Data Exfiltrator Profile",
    badgeColor: "bg-rose-500/10 text-rose-400 border-rose-500/20",
    data: {
      user: "EMP_EXFIL_99",
      name: "Marcus Vance",
      department: "R&D Engineering",
      role: "Senior System Architect",
      after_hours_activity: 95,
      midnight_activity: 40,
      weekend_activity: 35,
      device_events: 42,
      file_events: 310,
      unique_files: 180,
      unique_pcs: 4,
      web_events: 1850,
      unique_urls: 210,
      emails_sent: 190,
      total_events: 4200,
    },
  },
  offhours: {
    label: "Off-Hours Insider Profile",
    badgeColor: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    data: {
      user: "EMP_NIGHT_77",
      name: "David Kim",
      department: "IT Support",
      role: "Network Administrator",
      after_hours_activity: 240,
      midnight_activity: 110,
      weekend_activity: 85,
      device_events: 12,
      file_events: 65,
      unique_files: 30,
      unique_pcs: 5,
      web_events: 1100,
      unique_urls: 90,
      emails_sent: 80,
      total_events: 2800,
    },
  },
};

const DEFAULT_FORM = PRESETS.exfiltration.data;

export default function CustomEmployeeAnalyzerModal({ open, onClose, onEmployeeAdded }) {
  const [formData, setFormData] = useState(DEFAULT_FORM);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [activeTab, setActiveTab] = useState("inputs"); // 'inputs' | 'results'

  const handleInputChange = (field, val) => {
    setFormData((prev) => ({
      ...prev,
      [field]: val,
    }));
  };

  const applyPreset = (presetKey) => {
    if (PRESETS[presetKey]) {
      setFormData({ ...PRESETS[presetKey].data });
      setAnalysisResult(null);
    }
  };

  const runThreatAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      const res = await fetch("/api/v1/verification/evaluate-custom", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: Failed to evaluate threat`);
      }

      const data = await res.json();
      setAnalysisResult(data);
      setActiveTab("results");
    } catch (err) {
      console.error("Live analysis failed:", err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSaveToSystem = async () => {
    setIsSaving(true);
    try {
      const res = await fetch("/api/v1/verification/add-custom", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!res.ok) {
        throw new Error("Failed to register employee");
      }

      const data = await res.json();
      if (onEmployeeAdded) {
        onEmployeeAdded(data);
      }
      onClose();
    } catch (err) {
      console.error("Error adding employee to system:", err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 overflow-y-auto">
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 bg-slate-950/80 backdrop-blur-md"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Modal Container */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="relative z-10 w-full max-w-4xl max-h-[90vh] flex flex-col rounded-2xl border border-slate-800 bg-slate-900/95 shadow-2xl overflow-hidden backdrop-blur-xl"
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-800/80 px-6 py-4 bg-slate-900/50">
              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-cyan-500/10 p-2.5 text-cyan-400 border border-cyan-500/20">
                  <UserPlus className="h-6 w-6" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
                    Add New Employee & Live Threat Analyzer
                    <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                      <Sparkles className="h-3 w-3" /> Live ML Inference
                    </span>
                  </h2>
                  <p className="text-xs text-slate-400">
                    Input custom behavioral metrics to run live evaluation across 7 ML models & CERT anomaly baselines.
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {/* Navigation Tabs */}
                <div className="flex rounded-lg bg-slate-800/60 p-1 border border-slate-700/50">
                  <button
                    onClick={() => setActiveTab("inputs")}
                    className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                      activeTab === "inputs"
                        ? "bg-cyan-500 text-slate-950 font-bold shadow-md"
                        : "text-slate-400 hover:text-white"
                    }`}
                  >
                    Feature Inputs
                  </button>
                  <button
                    onClick={() => {
                      if (analysisResult) setActiveTab("results");
                      else runThreatAnalysis();
                    }}
                    className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all flex items-center gap-1 ${
                      activeTab === "results"
                        ? "bg-cyan-500 text-slate-950 font-bold shadow-md"
                        : "text-slate-400 hover:text-white"
                    }`}
                  >
                    <Cpu className="h-3.5 w-3.5" />
                    Threat Analysis {analysisResult && "✓"}
                  </button>
                </div>

                <button
                  onClick={onClose}
                  className="rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Presets Bar */}
            <div className="px-6 py-3 border-b border-slate-800/60 bg-slate-950/40 flex items-center justify-between gap-4 flex-wrap">
              <span className="text-xs font-medium text-slate-400 flex items-center gap-1.5">
                <Sliders className="h-3.5 w-3.5 text-cyan-400" />
                Quick Presets:
              </span>
              <div className="flex items-center gap-2">
                {Object.entries(PRESETS).map(([key, p]) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => applyPreset(key)}
                    className={`px-3 py-1 text-xs font-semibold rounded-lg border transition-all ${p.badgeColor} hover:scale-105`}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Main Content Area */}
            <div className="p-6 overflow-y-auto flex-1 space-y-6">
              {activeTab === "inputs" ? (
                <div className="space-y-6">
                  {/* Identity Info */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 rounded-xl border border-slate-800 bg-slate-900/40">
                    <div>
                      <label className="text-xs font-medium text-slate-400 block mb-1">Employee ID / User</label>
                      <input
                        type="text"
                        value={formData.user}
                        onChange={(e) => handleInputChange("user", e.target.value)}
                        className="w-full px-3 py-2 text-sm bg-slate-950 border border-slate-700/80 rounded-lg text-white focus:border-cyan-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-medium text-slate-400 block mb-1">Full Name</label>
                      <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => handleInputChange("name", e.target.value)}
                        className="w-full px-3 py-2 text-sm bg-slate-950 border border-slate-700/80 rounded-lg text-white focus:border-cyan-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-medium text-slate-400 block mb-1">Department</label>
                      <input
                        type="text"
                        value={formData.department}
                        onChange={(e) => handleInputChange("department", e.target.value)}
                        className="w-full px-3 py-2 text-sm bg-slate-950 border border-slate-700/80 rounded-lg text-white focus:border-cyan-500 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="text-xs font-medium text-slate-400 block mb-1">Designation / Role</label>
                      <input
                        type="text"
                        value={formData.role}
                        onChange={(e) => handleInputChange("role", e.target.value)}
                        className="w-full px-3 py-2 text-sm bg-slate-950 border border-slate-700/80 rounded-lg text-white focus:border-cyan-500 focus:outline-none"
                      />
                    </div>
                  </div>

                  {/* Behavioral Metrics Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Temporal Vector */}
                    <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/40 space-y-3">
                      <div className="flex items-center gap-2 text-cyan-400 text-sm font-bold border-b border-slate-800 pb-2">
                        <Clock className="h-4 w-4" /> Temporal Anomaly Features
                      </div>
                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-xs text-slate-300 mb-1">
                            <span>After Hours Logins:</span>
                            <span className="font-semibold text-cyan-400">{formData.after_hours_activity}</span>
                          </div>
                          <input
                            type="range"
                            min="0"
                            max="300"
                            value={formData.after_hours_activity}
                            onChange={(e) => handleInputChange("after_hours_activity", Number(e.target.value))}
                            className="w-full accent-cyan-500"
                          />
                        </div>
                        <div>
                          <div className="flex justify-between text-xs text-slate-300 mb-1">
                            <span>Midnight Activity:</span>
                            <span className="font-semibold text-cyan-400">{formData.midnight_activity}</span>
                          </div>
                          <input
                            type="range"
                            min="0"
                            max="150"
                            value={formData.midnight_activity}
                            onChange={(e) => handleInputChange("midnight_activity", Number(e.target.value))}
                            className="w-full accent-cyan-500"
                          />
                        </div>
                        <div>
                          <div className="flex justify-between text-xs text-slate-300 mb-1">
                            <span>Weekend Logins:</span>
                            <span className="font-semibold text-cyan-400">{formData.weekend_activity}</span>
                          </div>
                          <input
                            type="range"
                            min="0"
                            max="100"
                            value={formData.weekend_activity}
                            onChange={(e) => handleInputChange("weekend_activity", Number(e.target.value))}
                            className="w-full accent-cyan-500"
                          />
                        </div>
                      </div>
                    </div>

                    {/* USB & File Vector */}
                    <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/40 space-y-3">
                      <div className="flex items-center gap-2 text-rose-400 text-sm font-bold border-b border-slate-800 pb-2">
                        <HardDrive className="h-4 w-4" /> USB & File Exfiltration Features
                      </div>
                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-xs text-slate-300 mb-1">
                            <span>USB Connections:</span>
                            <span className="font-semibold text-rose-400">{formData.device_events}</span>
                          </div>
                          <input
                            type="range"
                            min="0"
                            max="100"
                            value={formData.device_events}
                            onChange={(e) => handleInputChange("device_events", Number(e.target.value))}
                            className="w-full accent-rose-500"
                          />
                        </div>
                        <div>
                          <div className="flex justify-between text-xs text-slate-300 mb-1">
                            <span>File Copy Events:</span>
                            <span className="font-semibold text-rose-400">{formData.file_events}</span>
                          </div>
                          <input
                            type="range"
                            min="0"
                            max="500"
                            value={formData.file_events}
                            onChange={(e) => handleInputChange("file_events", Number(e.target.value))}
                            className="w-full accent-rose-500"
                          />
                        </div>
                        <div>
                          <div className="flex justify-between text-xs text-slate-300 mb-1">
                            <span>Unique Files Copies:</span>
                            <span className="font-semibold text-rose-400">{formData.unique_files}</span>
                          </div>
                          <input
                            type="range"
                            min="0"
                            max="250"
                            value={formData.unique_files}
                            onChange={(e) => handleInputChange("unique_files", Number(e.target.value))}
                            className="w-full accent-rose-500"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Web & Multi-PC */}
                    <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/40 space-y-3">
                      <div className="flex items-center gap-2 text-purple-400 text-sm font-bold border-b border-slate-800 pb-2">
                        <Globe className="h-4 w-4" /> Web Browsing & Multi-PC Access
                      </div>
                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-xs text-slate-300 mb-1">
                            <span>Unique PCs Logged Into:</span>
                            <span className="font-semibold text-purple-400">{formData.unique_pcs}</span>
                          </div>
                          <input
                            type="range"
                            min="1"
                            max="10"
                            value={formData.unique_pcs}
                            onChange={(e) => handleInputChange("unique_pcs", Number(e.target.value))}
                            className="w-full accent-purple-500"
                          />
                        </div>
                        <div>
                          <div className="flex justify-between text-xs text-slate-300 mb-1">
                            <span>HTTP Web Requests:</span>
                            <span className="font-semibold text-purple-400">{formData.web_events}</span>
                          </div>
                          <input
                            type="range"
                            min="0"
                            max="5000"
                            step="50"
                            value={formData.web_events}
                            onChange={(e) => handleInputChange("web_events", Number(e.target.value))}
                            className="w-full accent-purple-500"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Email & Volume */}
                    <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/40 space-y-3">
                      <div className="flex items-center gap-2 text-amber-400 text-sm font-bold border-b border-slate-800 pb-2">
                        <Mail className="h-4 w-4" /> Email & Volume Metrics
                      </div>
                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-xs text-slate-300 mb-1">
                            <span>Emails Sent:</span>
                            <span className="font-semibold text-amber-400">{formData.emails_sent}</span>
                          </div>
                          <input
                            type="range"
                            min="0"
                            max="500"
                            value={formData.emails_sent}
                            onChange={(e) => handleInputChange("emails_sent", Number(e.target.value))}
                            className="w-full accent-amber-500"
                          />
                        </div>
                        <div>
                          <div className="flex justify-between text-xs text-slate-300 mb-1">
                            <span>Total Telemetry Events:</span>
                            <span className="font-semibold text-amber-400">{formData.total_events}</span>
                          </div>
                          <input
                            type="range"
                            min="100"
                            max="8000"
                            step="100"
                            value={formData.total_events}
                            onChange={(e) => handleInputChange("total_events", Number(e.target.value))}
                            className="w-full accent-amber-500"
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                /* Results View */
                analysisResult && (
                  <div className="space-y-6">
                    {/* Risk Summary Banner */}
                    <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/60 flex items-center justify-between flex-wrap gap-4">
                      <div className="flex items-center gap-4">
                        <div className={`p-3.5 rounded-2xl font-black text-2xl border ${
                          analysisResult.risk_level === "Critical"
                            ? "bg-rose-500/20 text-rose-400 border-rose-500/40"
                            : analysisResult.risk_level === "High"
                            ? "bg-amber-500/20 text-amber-400 border-amber-500/40"
                            : analysisResult.risk_level === "Medium"
                            ? "bg-yellow-500/20 text-yellow-400 border-yellow-500/40"
                            : "bg-emerald-500/20 text-emerald-400 border-emerald-500/40"
                        }`}>
                          {analysisResult.risk_score}
                          <span className="text-xs block font-normal text-slate-400">Score / 100</span>
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="text-lg font-bold text-white">{analysisResult.name}</h3>
                            <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full uppercase border ${
                              analysisResult.risk_level === "Critical"
                                ? "bg-rose-500/10 text-rose-400 border-rose-500/20"
                                : analysisResult.risk_level === "High"
                                ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                                : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                            }`}>
                              {analysisResult.risk_level} Risk
                            </span>
                          </div>
                          <p className="text-xs text-slate-400 mt-1">
                            Consensus: <span className="text-cyan-400 font-semibold">{analysisResult.consensus_percentage}%</span> ({analysisResult.suspicious_model_count}/7 Models Flagged)
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <span className="text-xs font-medium text-slate-400 block">Behavioral Vectors</span>
                          <span className="text-sm font-bold text-white">
                            {analysisResult.anomalous_vector_count} / {analysisResult.total_vectors_tested} Anomalous
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Multi-Model Grid */}
                    <div>
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                        <Cpu className="h-4 w-4 text-cyan-400" /> Multi-Model Live Inference Breakdown (7 Models)
                      </h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        {Object.entries(analysisResult.model_predictions).map(([mName, pred]) => {
                          const isSusp = pred === "Suspicious";
                          return (
                            <div
                              key={mName}
                              className={`p-3 rounded-xl border transition-all ${
                                isSusp
                                  ? "bg-rose-500/10 border-rose-500/30 text-rose-300"
                                  : "bg-slate-800/40 border-slate-700/50 text-slate-400"
                              }`}
                            >
                              <div className="flex items-center justify-between text-xs font-semibold">
                                <span>{mName}</span>
                                {isSusp ? (
                                  <AlertTriangle className="h-3.5 w-3.5 text-rose-400" />
                                ) : (
                                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                                )}
                              </div>
                              <div className={`mt-1 text-sm font-bold ${isSusp ? "text-rose-400" : "text-emerald-400"}`}>
                                {pred}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* Behavioral Evidence Breakdown */}
                    <div>
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                        <Activity className="h-4 w-4 text-amber-400" /> CERT Behavioral Vector Validation vs Baselines
                      </h4>
                      <div className="space-y-2">
                        {analysisResult.behavioral_vectors.map((v) => (
                          <div
                            key={v.vector_id}
                            className={`p-3 rounded-xl border flex items-center justify-between gap-4 text-xs ${
                              v.anomalous
                                ? "bg-amber-500/10 border-amber-500/30 text-amber-200"
                                : "bg-slate-900/40 border-slate-800 text-slate-400"
                            }`}
                          >
                            <div>
                              <span className="font-bold text-white block">{v.vector_name}</span>
                              <span className="text-[11px] opacity-80">{v.evidence}</span>
                            </div>
                            <div className="text-right whitespace-nowrap">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                v.anomalous ? "bg-rose-500/20 text-rose-400" : "bg-emerald-500/20 text-emerald-400"
                              }`}>
                                {v.anomalous ? "ANOMALOUS" : "NORMAL"}
                              </span>
                              <span className="block text-[10px] opacity-75 mt-0.5">Top 10% Baseline: {v.population_p90}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )
              )}
            </div>

            {/* Modal Footer */}
            <div className="border-t border-slate-800 px-6 py-4 bg-slate-950/60 flex items-center justify-between">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
              >
                Cancel
              </button>

              <div className="flex items-center gap-3">
                {activeTab === "inputs" ? (
                  <button
                    type="button"
                    onClick={runThreatAnalysis}
                    disabled={isAnalyzing}
                    className="flex items-center gap-2 px-5 py-2.5 text-xs font-bold rounded-xl bg-cyan-500 text-slate-950 hover:bg-cyan-400 transition-all shadow-lg disabled:opacity-50"
                  >
                    {isAnalyzing ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                    {isAnalyzing ? "Running Multi-Model Inference..." : "Run Threat Analysis"}
                  </button>
                ) : (
                  <>
                    <button
                      type="button"
                      onClick={() => setActiveTab("inputs")}
                      className="px-4 py-2 text-xs font-semibold rounded-xl border border-slate-700 text-slate-300 hover:bg-slate-800"
                    >
                      Edit Inputs
                    </button>
                    <button
                      type="button"
                      onClick={handleSaveToSystem}
                      disabled={isSaving}
                      className="flex items-center gap-2 px-5 py-2.5 text-xs font-bold rounded-xl bg-emerald-500 text-slate-950 hover:bg-emerald-400 transition-all shadow-lg disabled:opacity-50"
                    >
                      {isSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                      {isSaving ? "Saving to System..." : "Save Employee to System"}
                    </button>
                  </>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
