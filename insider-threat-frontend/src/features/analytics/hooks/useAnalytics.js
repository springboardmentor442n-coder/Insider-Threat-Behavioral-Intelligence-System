import { useQueries } from "@tanstack/react-query";

import analyticsService from "../api/analyticsService";
import analyticsQueryKeys from "../api/analyticsQueryKeys";

export default function useAnalytics() {

    const results = useQueries({

        queries: [

            {
                queryKey: analyticsQueryKeys.modelComparison,
                queryFn: async () => {
                    console.log("Fetching Model Comparison...");
                    return analyticsService.getModelComparison();
                },
            },

            {
                queryKey: analyticsQueryKeys.trainingTimes,
                queryFn: async () => {
                    console.log("Fetching Training Times...");
                    return analyticsService.getTrainingTimes();
                },
            },

            {
                queryKey: analyticsQueryKeys.riskDistribution,
                queryFn: async () => {
                    console.log("Fetching Risk Statistics...");
                    return analyticsService.getRiskDistribution();
                },
            },

            {
                queryKey: analyticsQueryKeys.datasetStatistics,
                queryFn: async () => {
                    console.log("Fetching Dataset Statistics...");
                    return analyticsService.getDatasetStatistics();
                },
            },

            {
                queryKey: analyticsQueryKeys.featureStatistics,
                queryFn: async () => {
                    console.log("Fetching Feature Statistics...");
                    return analyticsService.getFeatureStatistics();
                },
            },

        ],

    });

    return {

        modelComparison: results[0].data ?? [],
        trainingTimes: results[1].data ?? [],
        riskDistribution: results[2].data ?? [],
        datasetStatistics: results[3].data ?? [],
        featureStatistics: results[4].data ?? [],

        loading: results.some((query) => query.isLoading),

        error: results.find((query) => query.isError)?.error,

    };

}
