import { motion } from "framer-motion";
import { BarChart3, Activity } from "lucide-react";

import PageHeader from "../../../components/shared/PageHeader";
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

            className="space-y-5 pb-6"

        >

            {/* PAGE HEADER */}
            <PageHeader
                icon={BarChart3}
                title="Analytics Center"
                subtitle="AI Model Performance, Dataset Statistics and Insider Threat Analytics"
                badge={
                    <span className="inline-flex items-center gap-1.5 rounded-xl border border-cyan-500/20 bg-cyan-500/10 px-3 py-1.5 text-xs font-semibold text-cyan-300">
                        <Activity className="h-3.5 w-3.5 text-cyan-400" />
                        7-Model Ensemble
                    </span>
                }
            />

            <AnalyticsOverviewCards

                datasetStatistics={datasetStatistics}

            />

            <AnalyticsToolbar />

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">

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
