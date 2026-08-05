import { useQuery } from "@tanstack/react-query";
import analyticsService from "../../services/api/analyticsService";

export function useTopSuspicious() {
  return useQuery({
    queryKey: ["top-suspicious"],
    queryFn: analyticsService.getTopSuspicious,
    staleTime: 5 * 60 * 1000,
  });
}
