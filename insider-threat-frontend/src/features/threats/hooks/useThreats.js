import { useQuery } from "@tanstack/react-query";

import threatService from "../api/threatService";
import { threatQueryKeys } from "../api/threatQueryKeys";

export function useThreats(filters = {}) {
  return useQuery({
    queryKey: threatQueryKeys.list(filters),

    queryFn: () =>
      threatService.getThreats(filters),

    staleTime: 10000,
refetchInterval: 10000,
refetchOnReconnect: true,
refetchOnMount: true,
  });
}

export function useThreat(id) {
  return useQuery({
    queryKey: threatQueryKeys.detail(id),

    queryFn: () =>
      threatService.getThreat(id),

    enabled: Boolean(id),
  });
}
