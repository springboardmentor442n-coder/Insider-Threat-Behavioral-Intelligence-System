import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import {
  BrainCircuit,
  AlertCircle,
} from "lucide-react";
import { toast } from "sonner";

import useExplainability from "../hooks/useExplainability";

import ExplainabilityOverviewCards from "../components/ExplainabilityOverviewCards";
import FeatureImportanceTable from "../components/FeatureImportanceTable";
import BehavioralFactors from "../components/BehavioralFactors";
import EmployeeExplanation from "../components/EmployeeExplanation";
import ExplainabilityToolbar from "../components/ExplainabilityToolbar";
import PageHeader from "../../../components/shared/PageHeader";

export default function ExplainabilityPage() {
  const [searchParams] = useSearchParams();
  const queryEmployee = searchParams.get("employee") || "";

  const [employeeInput, setEmployeeInput] = useState(queryEmployee);
  const [selectedEmployee, setSelectedEmployee] = useState(queryEmployee);

  useEffect(() => {
    if (queryEmployee && queryEmployee !== selectedEmployee) {
      setSelectedEmployee(queryEmployee);
      setEmployeeInput(queryEmployee);
    }
  }, [queryEmployee]);

  const {
    featureImportance,
    behavioralFactors,
    employeeExplanation,
    loading,
    employeeLoading,
    error,
    employeeError,
    refetchFeatureImportance,
    refetchBehavioralFactors,
    refetchEmployee,
  } = useExplainability(selectedEmployee);

  const handleSearch = () => {
    const value =
      employeeInput.trim().toUpperCase();

    if (!value) {
      toast.error(
        "Please enter an employee ID."
      );

      return;
    }

    setSelectedEmployee(value);
  };

  const handleRefresh = async () => {
    try {
      await Promise.all([
        refetchFeatureImportance(),
        refetchBehavioralFactors(),
        selectedEmployee
          ? refetchEmployee()
          : Promise.resolve(),
      ]);

      toast.success(
        "Explainability data refreshed."
      );
    } catch {
      toast.error(
        "Failed to refresh explainability data."
      );
    }
  };

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 10,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="space-y-5 pb-6"
    >
      {/* Header */}
      <PageHeader
        icon={BrainCircuit}
        title="Explainability Center"
        subtitle="Why was this employee flagged? Understand the behavioral factors, SHAP importance, and statistical signals behind anomaly predictions."
      />

      {/* Toolbar */}

      <ExplainabilityToolbar
        employeeId={employeeInput}
        setEmployeeId={setEmployeeInput}
        onSearch={handleSearch}
        onRefresh={handleRefresh}
        loading={
          loading || employeeLoading
        }
      />

      {/* Backend error */}

      {error && (
        <div
          className="
            flex
            items-center
            gap-3
            rounded-xl
            border border-red-500/30
            bg-red-500/10
            p-4
          "
        >
          <AlertCircle
            size={20}
            className="text-red-400"
          />

          <p className="text-red-300">
            Failed to load explainability reports.
          </p>
        </div>
      )}

      {/* Overview */}

      <ExplainabilityOverviewCards
        featureImportance={featureImportance}
        behavioralFactors={behavioralFactors}
      />

      {/* Behavioral factors */}

      <BehavioralFactors
        data={behavioralFactors}
      />

      {/* Feature importance */}

      <FeatureImportanceTable
        data={featureImportance}
      />

      {/* Employee explanation */}

      {employeeError && (
        <div
          className="
            rounded-xl
            border border-red-500/30
            bg-red-500/10
            p-4
          "
        >
          <p className="text-red-300">
            Employee explanation not found for{" "}
            <strong>
              {selectedEmployee}
            </strong>
            .
          </p>
        </div>
      )}

      {employeeLoading ? (
        <div
          className="
            rounded-2xl
            border border-cyan-500/20
            bg-slate-900/60
            p-6
            text-cyan-300
          "
        >
          Loading employee explanation...
        </div>
      ) : (
        <EmployeeExplanation
          explanation={employeeExplanation}
        />
      )}
    </motion.div>
  );
}
