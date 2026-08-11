import { useQuery } from "@tanstack/react-query";

import explainabilityService from "../api/explainabilityService";
import explainabilityQueryKeys from "../api/explainabilityQueryKeys";

export default function useExplainability(employeeId = "") {
  const featureImportanceQuery = useQuery({
    queryKey:
      explainabilityQueryKeys.featureImportance,

    queryFn:
      explainabilityService.getFeatureImportance,
  });

  const behavioralFactorsQuery = useQuery({
    queryKey:
      explainabilityQueryKeys.behavioralFactors,

    queryFn:
      explainabilityService.getTopBehavioralFactors,
  });

  const employeeQuery = useQuery({
    queryKey:
      explainabilityQueryKeys.employee(employeeId),

    queryFn: () =>
      explainabilityService.getEmployeeExplanation(
        employeeId
      ),

    enabled: Boolean(employeeId),
  });

  return {
    featureImportance:
      featureImportanceQuery.data ?? [],

    behavioralFactors:
      behavioralFactorsQuery.data ?? [],

    employeeExplanation:
      employeeQuery.data ?? null,

    loading:
      featureImportanceQuery.isLoading ||
      behavioralFactorsQuery.isLoading,

    employeeLoading:
      employeeQuery.isLoading,

    error:
      featureImportanceQuery.error ||
      behavioralFactorsQuery.error,

    employeeError: employeeQuery.error,

    refetchFeatureImportance:
      featureImportanceQuery.refetch,

    refetchBehavioralFactors:
      behavioralFactorsQuery.refetch,

    refetchEmployee:
      employeeQuery.refetch,
  };
}
