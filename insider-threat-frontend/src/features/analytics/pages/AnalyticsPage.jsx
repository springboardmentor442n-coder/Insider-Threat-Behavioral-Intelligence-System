import { motion } from "framer-motion";
import { BarChart3 } from "lucide-react";

import useAnalytics from "../hooks/useAnalytics";

import AnalyticsOverviewCards from "../components/AnalyticsOverviewCards";
import AnalyticsToolbar from "../components/AnalyticsToolbar";
import AnalyticsSkeleton from "../components/AnalyticsSkeleton";

import ModelComparisonChart from "../charts/ModelComparisonChart";
import RiskDistributionChart from "../charts/RiskDistributionChart";
import MonthlyTrendChart from "../charts/MonthlyTrendChart";
import DepartmentRiskChart from "../charts/DepartmentRiskChart";

export default function AnalyticsPage() {

    const {

        modelComparison,
        trainingTimes,
        riskDistribution,
        datasetStatistics,
        featureStatistics,
        loading,

    } = useAnalytics();

    if (loading) {

        return <AnalyticsSkeleton />;

    }

    return (

        <motion.div

            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}

            className="space-y-6"

        >

            <section className="rounded-3xl border border-cyan-500/20 bg-slate-900/70 p-8">

                <div className="flex items-center gap-4">

                    <div className="rounded-2xl bg-cyan-500/20 p-4">

                        <BarChart3 className="h-8 w-8 text-cyan-400" />

                    </div>

                    <div>

                        <h1 className="text-4xl font-bold text-white">

                            Analytics Center

                        </h1>

                        <p className="mt-2 text-slate-400">

                            AI Model Performance, Dataset Statistics and Insider Threat Analytics

                        </p>

                    </div>

                </div>

            </section>

            <AnalyticsOverviewCards

                datasetStatistics={datasetStatistics}

            />

            <AnalyticsToolbar />

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">

                <ModelComparisonChart

                    data={modelComparison}

                />

                <RiskDistributionChart

                    data={riskDistribution}

                />

                <MonthlyTrendChart

                    data={trainingTimes}

                />

                <DepartmentRiskChart

                    data={featureStatistics}

                />

            </div>

        </motion.div>

    );

}
