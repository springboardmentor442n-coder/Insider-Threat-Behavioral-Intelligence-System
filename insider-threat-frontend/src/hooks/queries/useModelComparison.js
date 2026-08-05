import { useQuery } from "@tanstack/react-query";
import analyticsService from "../../services/api/analyticsService";

export function useModelComparison() {
  return useQuery({
    queryKey: ["model-comparison"],
    queryFn: analyticsService.getModelComparison,
    staleTime: 5 * 60 * 1000,
  });
}
