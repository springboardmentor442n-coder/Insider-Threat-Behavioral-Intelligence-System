import { useQuery } from "@tanstack/react-query";

import reportsService from "../api/reportsService";
import reportsQueryKeys from "../api/reportsQueryKeys";

export default function useReports() {
    const reportListQuery = useQuery({
        queryKey: reportsQueryKeys.list,

        queryFn: reportsService.getAvailableReports,

        staleTime: 15 * 1000,

        refetchInterval: 30 * 1000,

        refetchOnWindowFocus: true,

        retry: 2,
    });

    const reportsQuery = useQuery({
        queryKey: reportsQueryKeys.reports,

        queryFn: reportsService.getAllReports,

        staleTime: 15 * 1000,

        refetchInterval: 30 * 1000,

        refetchOnWindowFocus: true,

        retry: 2,
    });

    return {
        reportList: reportListQuery.data ?? [],

        reports: reportsQuery.data ?? {},

        loading:
            reportListQuery.isLoading ||
            reportsQuery.isLoading,

        refreshing:
            reportListQuery.isFetching ||
            reportsQuery.isFetching,

        error:
            reportListQuery.error ||
            reportsQuery.error,

        refetch: async () => {
            await Promise.all([
                reportListQuery.refetch(),
                reportsQuery.refetch(),
            ]);
        },
    };
}
