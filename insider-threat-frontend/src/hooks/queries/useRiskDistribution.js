import { useQuery } from "@tanstack/react-query";
import analyticsService from "../../services/api/analyticsService";

export function useRiskDistribution() {
  return useQuery({
    queryKey: ["risk-distribution"],
    queryFn: analyticsService.getRiskDistribution,
    staleTime: 5 * 60 * 1000,
  });
}
