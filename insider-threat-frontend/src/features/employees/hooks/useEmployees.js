import { useQuery } from "@tanstack/react-query";
import employeeService from "../api/employeeService";
import { employeeQueryKeys } from "../api/employeeQueryKeys";

export function useEmployees(filters = {}) {
  return useQuery({
    queryKey: employeeQueryKeys.list(filters),

    queryFn: () => employeeService.getEmployees(filters),

    staleTime: 30000,
  });
}

export function useEmployee(id) {
  return useQuery({
    queryKey: employeeQueryKeys.detail(id),

    queryFn: () => employeeService.getEmployeeById(id),

    enabled: !!id,
  });
}

export function useEmployeeActivity(id) {
  return useQuery({
    queryKey: ["employee-activity", id],

    queryFn: () => employeeService.getEmployeeActivity(id),

    enabled: !!id,

    staleTime: 15000,
  });
}
