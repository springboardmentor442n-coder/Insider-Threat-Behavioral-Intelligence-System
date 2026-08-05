import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import employeeService from "../api/employeeService";
import { employeeQueryKeys } from "../api/employeeQueryKeys";

// ======================================================
// CREATE EMPLOYEE
// ======================================================

export function useCreateEmployee() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload) => employeeService.createEmployee(payload),

    onSuccess: () => {
      toast.success("Employee added successfully");

      queryClient.invalidateQueries({
        queryKey: employeeQueryKeys.all,
      });
    },

    onError: (error) => {
      toast.error("Failed to add employee", {
        description:
          error?.response?.data?.detail ||
          error?.message ||
          "Unknown error",
      });
    },
  });
}

// ======================================================
// UPDATE EMPLOYEE
// ======================================================

export function useUpdateEmployee() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, payload }) =>
      employeeService.updateEmployee(id, payload),

    onSuccess: (_, variables) => {
      toast.success("Employee updated successfully");

      queryClient.invalidateQueries({
        queryKey: employeeQueryKeys.all,
      });

      queryClient.invalidateQueries({
        queryKey: employeeQueryKeys.detail(variables.id),
      });
    },

    onError: (error) => {
      toast.error("Failed to update employee", {
        description:
          error?.response?.data?.detail ||
          error?.message ||
          "Unknown error",
      });
    },
  });
}

// ======================================================
// DELETE EMPLOYEE
// ======================================================

export function useDeleteEmployee() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id) => employeeService.deleteEmployee(id),

    onSuccess: () => {
      toast.success("Employee deleted");

      queryClient.invalidateQueries({
        queryKey: employeeQueryKeys.all,
      });
    },

    onError: (error) => {
      toast.error("Failed to delete employee", {
        description:
          error?.response?.data?.detail ||
          error?.message ||
          "Unknown error",
      });
    },
  });
}
