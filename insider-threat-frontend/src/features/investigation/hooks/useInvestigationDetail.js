import { useQuery } from "@tanstack/react-query";

import investigationService from "../api/investigationService";
import investigationQueryKeys from "../api/investigationQueryKeys";

/*
|--------------------------------------------------------------------------
| Investigation Detail Hook
|--------------------------------------------------------------------------
*/

export default function useInvestigationDetail(caseId) {
  const {
    data,
    isLoading,
    isFetching,
    error,
    refetch,
  } = useQuery({
    queryKey: investigationQueryKeys.details(caseId),

    queryFn: () =>
      investigationService.getCase(caseId),

    enabled: Boolean(caseId),

    staleTime: 10 * 1000,

    refetchOnWindowFocus: true,

    refetchOnReconnect: true,

    retry: 2,
  });

  return {
    caseData: data ?? null,

    loading: isLoading,

    fetching: isFetching,

    error,

    refetch,
  };
}
