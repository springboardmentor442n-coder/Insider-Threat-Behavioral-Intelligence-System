import { useQuery } from "@tanstack/react-query";

import investigationService from "../api/investigationService";
import investigationQueryKeys from "../api/investigationQueryKeys";

/*
|--------------------------------------------------------------------------
| Investigation List Hook
|--------------------------------------------------------------------------
*/

export default function useInvestigation() {
  const {
    data = [],
    isLoading,
    isFetching,
    error,
    refetch,
  } = useQuery({
    queryKey: investigationQueryKeys.cases(),

    queryFn: investigationService.getCases,

    /*
    | Keep Investigation reasonably fresh.
    | Threat Center uses a 10 second refresh interval, so Investigation
    | should follow the same live-monitoring behaviour.
    */
    staleTime: 10 * 1000,

    refetchInterval: 10 * 1000,

    refetchOnReconnect: true,

    refetchOnMount: true,

    refetchOnWindowFocus: true,

    retry: 2,
  });

  return {
    cases: Array.isArray(data) ? data : [],

    loading: isLoading,

    fetching: isFetching,

    error,

    refetch,
  };
}
