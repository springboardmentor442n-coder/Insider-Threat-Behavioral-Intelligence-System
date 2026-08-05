import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import threatService from "../api/threatService";
import { threatQueryKeys } from "../api/threatQueryKeys";

// ======================================================
// CREATE
// ======================================================

export function useCreateThreat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: threatService.createThreat,

    onSuccess: () => {
      toast.success("Threat created successfully.");

      queryClient.invalidateQueries({
        queryKey: threatQueryKeys.all,
      });
    },

    onError: (error) => {
      toast.error(
        error?.response?.data?.detail ??
          "Unable to create threat."
      );
    },
  });
}

// ======================================================
// UPDATE
// ======================================================

export function useUpdateThreat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, payload }) =>
      threatService.updateThreat(id, payload),

    onSuccess: () => {
      toast.success("Threat updated successfully.");

      queryClient.invalidateQueries({
        queryKey: threatQueryKeys.all,
      });
    },

    onError: (error) => {
      toast.error(
        error?.response?.data?.detail ??
          "Unable to update threat."
      );
    },
  });
}

// ======================================================
// RESOLVE
// ======================================================

export function useResolveThreat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: threatService.resolveThreat,

    onMutate: async (id) => {
      await queryClient.cancelQueries({
        queryKey: threatQueryKeys.all,
      });

      const previous =
        queryClient.getQueryData(
          threatQueryKeys.list({})
        );

      queryClient.setQueryData(
        threatQueryKeys.list({}),
        (old = []) =>
          old.map((threat) =>
            threat.id === id
              ? {
                  ...threat,
                  status: "Resolved",
                }
              : threat
          )
      );

      return { previous };
    },

    onError: (error, variables, context) => {
      if (context?.previous) {
        queryClient.setQueryData(
          threatQueryKeys.list({}),
          context.previous
        );
      }

      toast.error(
        error?.response?.data?.detail ??
          "Unable to resolve threat."
      );
    },

    onSuccess: () => {
      toast.success("Threat resolved successfully.");
    },

    onSettled: () => {
      queryClient.invalidateQueries({
        queryKey: threatQueryKeys.all,
      });
    },
  });
}

// ======================================================
// DELETE
// ======================================================

export function useDeleteThreat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: threatService.deleteThreat,

    onMutate: async (id) => {
      await queryClient.cancelQueries({
        queryKey: threatQueryKeys.all,
      });

      const previous =
        queryClient.getQueryData(
          threatQueryKeys.list({})
        );

      queryClient.setQueryData(
        threatQueryKeys.list({}),
        (old = []) =>
          old.filter(
            (threat) => threat.id !== id
          )
      );

      return { previous };
    },

    onError: (error, variables, context) => {
      if (context?.previous) {
        queryClient.setQueryData(
          threatQueryKeys.list({}),
          context.previous
        );
      }

      toast.error(
        error?.response?.data?.detail ??
          "Unable to delete threat."
      );
    },

    onSuccess: () => {
      toast.success("Threat deleted successfully.");
    },

    onSettled: () => {
      queryClient.invalidateQueries({
        queryKey: threatQueryKeys.all,
      });
    },
  });
}
