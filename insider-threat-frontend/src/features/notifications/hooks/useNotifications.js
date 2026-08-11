import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import notificationService from "../api/notificationService";

const notificationKeys = {
  all: ["notifications"],
  list: () => ["notifications", "list"],
  unreadCount: () => ["notifications", "unread-count"],
};

export function useNotifications() {
  return useQuery({
    queryKey: notificationKeys.list(),
    queryFn: () =>
      notificationService.getNotifications(),

    staleTime: 5000,

    refetchInterval: 10000,

    refetchOnReconnect: true,

    refetchOnMount: true,
  });
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id) =>
      notificationService.markAsRead(id),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: notificationKeys.all,
      });
    },
  });
}

export function useMarkAllNotificationsRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () =>
      notificationService.markAllAsRead(),

    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: notificationKeys.all,
      });
    },
  });
}
