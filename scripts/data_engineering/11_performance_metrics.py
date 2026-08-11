"""
===============================================================================
Module        : Performance Metrics
File          : 11_performance_metrics.py
Project       : Insider Threat Behavioral Intelligence System

Description:
    Generates comprehensive performance metrics for the complete
    Insider Threat Behavioral Intelligence System including:

    • Dataset Statistics
    • Feature Engineering Statistics
    • Multi-Model Performance
    • Consensus Analysis
    • Classification Metrics (if labels exist)
    • System Statistics

Input
-----
datasets/exports/
    employee_final_risk_report.parquet

datasets/features/
    employee_features.parquet

reports/
    model_statistics.csv
    training_times.csv
    consensus_predictions.csv

Outputs
-------
reports/
    dataset_statistics.csv
    performance_metrics.csv
    model_performance.csv
    classification_report.csv
    system_statistics.csv

plots/
    accuracy_comparison.png
    model_detection_rate.png
    training_time_analysis.png
    dataset_quality.png
    risk_level_summary.png

Author
------
Nandan Kabra
===============================================================================
"""

from pathlib import Path
import logging
import time

import duckdb
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

from sklearn.metrics import (

    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report

)

# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger(__name__)

# =============================================================================
# Paths
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_DIR = PROJECT_ROOT / "datasets"

EXPORT_DIR = DATASET_DIR / "exports"

FEATURE_DIR = DATASET_DIR / "features"

REPORT_DIR = PROJECT_ROOT / "reports"

PLOT_DIR = PROJECT_ROOT / "plots"

REPORT_DIR.mkdir(

    parents=True,

    exist_ok=True

)

PLOT_DIR.mkdir(

    parents=True,

    exist_ok=True

)

# =============================================================================
# Input Files
# =============================================================================

RISK_FILE = EXPORT_DIR / "employee_final_risk_report.parquet"

FEATURE_FILE = FEATURE_DIR / "employee_features.parquet"

MODEL_COMPARISON_FILE = REPORT_DIR / "model_comparison.csv"

MODEL_STATS_FILE = REPORT_DIR / "model_statistics.csv"

TRAINING_TIME_FILE = REPORT_DIR / "training_times.csv"

CONSENSUS_FILE = REPORT_DIR / "consensus_predictions.csv"

# =============================================================================
# Performance Metrics Class
# =============================================================================

class PerformanceMetrics:

    def __init__(self):

        self.conn = duckdb.connect()

        self.start_time = time.time()

        logger.info("=" * 80)
        logger.info("PERFORMANCE METRICS ENGINE")
        logger.info("=" * 80)

        self.risk_df = None

        self.feature_df = None

        self.model_stats = None

        self.training_df = None

        self.consensus_df = None

        self.df = None

        self.numeric_features = []

        self.dataset_metrics = {}

        self.performance_metrics = {}
    # -------------------------------------------------------------------------
    # Load Datasets
    # -------------------------------------------------------------------------

    def load_data(self):

        logger.info("=" * 80)
        logger.info("LOADING DATASETS")
        logger.info("=" * 80)

        # ---------------------------------------------------------------------
        # Validate Input Files
        # ---------------------------------------------------------------------

        input_files = {

            "Risk Report": RISK_FILE,

            "Feature Dataset": FEATURE_FILE,

            "Model Statistics": MODEL_STATS_FILE,

            "Training Times": TRAINING_TIME_FILE,

            "Consensus Predictions": CONSENSUS_FILE

        }

        for name, file in input_files.items():

            if not file.exists():

                raise FileNotFoundError(

                    f"{name} Not Found:\n{file}"

                )

        # ---------------------------------------------------------------------
        # Employee Risk Report
        # ---------------------------------------------------------------------

        logger.info("Loading Employee Risk Report...")

        self.risk_df = self.conn.execute(f"""

            SELECT *

            FROM read_parquet(

                '{RISK_FILE.as_posix()}'

            )

        """).fetchdf()

        # ---------------------------------------------------------------------
        # Employee Features
        # ---------------------------------------------------------------------

        logger.info("Loading Employee Features...")

        self.feature_df = self.conn.execute(f"""

            SELECT *

            FROM read_parquet(

                '{FEATURE_FILE.as_posix()}'

            )

        """).fetchdf()

        # ---------------------------------------------------------------------
        # Model Statistics
        # ---------------------------------------------------------------------

        logger.info("Loading Model Statistics...")

        self.model_stats = pd.read_csv(

            MODEL_COMPARISON_FILE

        )

        # ---------------------------------------------------------------------
        # Training Times
        # ---------------------------------------------------------------------

        logger.info("Loading Training Times...")

        self.training_df = pd.read_csv(

            TRAINING_TIME_FILE

        )

        # ---------------------------------------------------------------------
        # Consensus Predictions
        # ---------------------------------------------------------------------

        logger.info("Loading Consensus Predictions...")

        self.consensus_df = pd.read_csv(

            CONSENSUS_FILE

        )

        # ---------------------------------------------------------------------
        # Merge Datasets
        # ---------------------------------------------------------------------

        logger.info("Merging Risk Report with Feature Dataset...")

        self.df = pd.merge(

            self.risk_df,

            self.feature_df,

            on="user",

            how="left"

        )

        self.df = self.df.loc[

            :,

            ~self.df.columns.duplicated()

        ]

        # ---------------------------------------------------------------------
        # Feature Detection
        # ---------------------------------------------------------------------

        numeric = self.df.select_dtypes(

            include=np.number

        )

        categorical = self.df.select_dtypes(

            exclude=np.number

        )

        self.numeric_features = list(

            numeric.columns

        )

        self.categorical_features = list(

            categorical.columns

        )

        # ---------------------------------------------------------------------
        # Dataset Summary
        # ---------------------------------------------------------------------

        logger.info(

            f"Employees Loaded : {len(self.df):,}"

        )

        logger.info(

            f"Numeric Features : {len(self.numeric_features)}"

        )

        logger.info(

            f"Categorical Features : {len(self.categorical_features)}"

        )

        logger.info(

            f"Models Loaded : {len(self.model_stats)}"

        )

        logger.info(

            f"Consensus Records : {len(self.consensus_df):,}"

        )

        logger.info("=" * 80)

    # -------------------------------------------------------------------------
    # Initial Summary
    # -------------------------------------------------------------------------

    def dataset_summary(self):

        logger.info("=" * 80)
        logger.info("DATASET SUMMARY")
        logger.info("=" * 80)

        logger.info(

            f"Employees : {len(self.df):,}"

        )

        logger.info(

            f"Columns : {len(self.df.columns)}"

        )

        logger.info(

            f"Numeric Features : {len(self.numeric_features)}"

        )

        logger.info(

            f"Categorical Features : {len(self.categorical_features)}"

        )

        logger.info(

            f"Risk Levels : {self.df['risk_level'].nunique()}"

        )

        logger.info(

            f"Models Evaluated : {len(self.model_stats)}"

        )

        logger.info("=" * 80)
            # -------------------------------------------------------------------------
    # Dataset Statistics
    # -------------------------------------------------------------------------

    def dataset_statistics(self):

        logger.info("=" * 80)
        logger.info("DATASET STATISTICS")
        logger.info("=" * 80)

        total_records = len(self.df)

        total_columns = len(self.df.columns)

        duplicate_records = self.df.duplicated().sum()

        missing_values = self.df.isnull().sum().sum()

        missing_percentage = (

            missing_values /

            (total_records * total_columns)

        ) * 100

        completeness = 100 - missing_percentage

        memory_usage = (

            self.df.memory_usage(

                deep=True

            ).sum()

            / (1024 ** 2)

        )

        statistics = [

            {

                "Metric":

                    "Total Records",

                "Value":

                    total_records

            },

            {

                "Metric":

                    "Total Columns",

                "Value":

                    total_columns

            },

            {

                "Metric":

                    "Numeric Features",

                "Value":

                    len(self.numeric_features)

            },

            {

                "Metric":

                    "Categorical Features",

                "Value":

                    len(self.categorical_features)

            },

            {

                "Metric":

                    "Duplicate Records",

                "Value":

                    duplicate_records

            },

            {

                "Metric":

                    "Missing Values",

                "Value":

                    missing_values

            },

            {

                "Metric":

                    "Missing Percentage",

                "Value":

                    round(

                        missing_percentage,

                        2

                    )

            },

            {

                "Metric":

                    "Dataset Completeness (%)",

                "Value":

                    round(

                        completeness,

                        2

                    )

            },

            {

                "Metric":

                    "Memory Usage (MB)",

                "Value":

                    round(

                        memory_usage,

                        2

                    )

            }

        ]

        dataset_stats = pd.DataFrame(

            statistics

        )

        dataset_stats.to_csv(

            REPORT_DIR /

            "dataset_statistics.csv",

            index=False

        )

        self.dataset_statistics_df = dataset_stats

        logger.info(

            "Dataset Statistics Saved"

        )

        print()

        print(

            dataset_stats

        )

        print()

        logger.info("=" * 80)

    # -------------------------------------------------------------------------
    # Feature Engineering Statistics
    # -------------------------------------------------------------------------

    def feature_statistics(self):

        logger.info("=" * 80)
        logger.info("FEATURE ENGINEERING STATISTICS")
        logger.info("=" * 80)

        important_features = [

            "total_events",

            "active_days",

            "after_hours_activity",

            "weekend_activity",

            "device_events",

            "web_events",

            "email_events",

            "file_events"

        ]

        feature_summary = []

        for feature in important_features:

            if feature not in self.df.columns:

                continue

            values = self.df[feature]

            feature_summary.append(

                {

                    "Feature":

                        feature,

                    "Mean":

                        round(

                            values.mean(),

                            2

                        ),

                    "Median":

                        round(

                            values.median(),

                            2

                        ),

                    "Minimum":

                        round(

                            values.min(),

                            2

                        ),

                    "Maximum":

                        round(

                            values.max(),

                            2

                        ),

                    "Standard Deviation":

                        round(

                            values.std(),

                            2

                        )

                }

            )

        feature_df = pd.DataFrame(

            feature_summary

        )

        feature_df.to_csv(

            REPORT_DIR /

            "feature_engineering_statistics.csv",

            index=False

        )

        self.feature_statistics_df = feature_df

        logger.info(

            "Feature Engineering Statistics Saved"

        )

        print()

        print(

            feature_df

        )

        print()

        logger.info("=" * 80)

    # -------------------------------------------------------------------------
    # Risk Level Distribution
    # -------------------------------------------------------------------------

    def risk_distribution(self):

        logger.info("=" * 80)
        logger.info("RISK LEVEL DISTRIBUTION")
        logger.info("=" * 80)

        distribution = (

            self.df["risk_level"]

            .value_counts()

            .reset_index()

        )

        distribution.columns = [

            "Risk Level",

            "Employees"

        ]

        distribution["Percentage"] = (

            distribution["Employees"]

            /

            len(self.df)

            * 100

        ).round(2)

        distribution.to_csv(

            REPORT_DIR /

            "risk_level_distribution.csv",

            index=False

        )

        self.risk_distribution_df = distribution

        logger.info(

            "Risk Distribution Saved"

        )

        print()

        print(

            distribution

        )

        print()

        logger.info("=" * 80)
            # -------------------------------------------------------------------------
    # Model Performance Analysis
    # -------------------------------------------------------------------------

    def model_performance(self):

        logger.info("=" * 80)
        logger.info("MODEL PERFORMANCE ANALYSIS")
        logger.info("=" * 80)

        performance = []

        # -------------------------------------------------------------
        # Training Time Dictionary
        # -------------------------------------------------------------

        training_lookup = {}

        if "Model" in self.training_df.columns:

            for _, row in self.training_df.iterrows():

                training_lookup[

                    row["Model"]

                ] = row["Training Time"]

        # -------------------------------------------------------------
        # Iterate Over Models
        # -------------------------------------------------------------

        for _, row in self.model_stats.iterrows():

            model = row["Model"]

            suspicious = row["Suspicious Employees"]

            detection_rate = (

                suspicious /

                len(self.df)

            ) * 100

            performance.append(

                {

                    "Model":

                        model,

                    "Training Time (sec)":

                        round(

                            training_lookup.get(

                                model,

                                0

                            ),

                            4

                        ),

                    "Suspicious Employees":

                        suspicious,

                    "Detection Rate (%)":

                        round(

                            detection_rate,

                            2

                        ),

                    "Average Risk Score":

                        round(

                            row["Average Risk Score"],

                            3

                        ),

                    "Maximum Risk Score":

                        round(

                            row["Maximum Risk Score"],

                            3

                        ),

                    "Minimum Risk Score":

                        round(

                            row["Minimum Risk Score"],

                            3

                        )

                }

            )

        performance_df = pd.DataFrame(

            performance

        )

        performance_df = performance_df.sort_values(

            "Detection Rate (%)",

            ascending=False

        )

        performance_df.to_csv(

            REPORT_DIR /

            "model_performance.csv",

            index=False

        )

        self.performance_df = performance_df

        logger.info(

            "Model Performance Saved"

        )

        print()

        print(

            performance_df

        )

        print()

        logger.info("=" * 80)

    # -------------------------------------------------------------------------
    # Overall Performance Metrics
    # -------------------------------------------------------------------------

    def overall_performance(self):

        logger.info("=" * 80)
        logger.info("OVERALL PERFORMANCE")
        logger.info("=" * 80)

        fastest = self.performance_df.loc[

            self.performance_df[

                "Training Time (sec)"

            ].idxmin()

        ]

        slowest = self.performance_df.loc[

            self.performance_df[

                "Training Time (sec)"

            ].idxmax()

        ]

        highest_detection = self.performance_df.loc[

            self.performance_df[

                "Detection Rate (%)"

            ].idxmax()

        ]

        summary = [

            {

                "Metric":

                    "Fastest Model",

                "Value":

                    fastest["Model"]

            },

            {

                "Metric":

                    "Slowest Model",

                "Value":

                    slowest["Model"]

            },

            {

                "Metric":

                    "Highest Detection Model",

                "Value":

                    highest_detection["Model"]

            },

            {

                "Metric":

                    "Average Training Time",

                "Value":

                    round(

                        self.performance_df[

                            "Training Time (sec)"

                        ].mean(),

                        4

                    )

            },

            {

                "Metric":

                    "Average Detection Rate",

                "Value":

                    round(

                        self.performance_df[

                            "Detection Rate (%)"

                        ].mean(),

                        2

                    )

            }

        ]

        performance_summary = pd.DataFrame(

            summary

        )

        performance_summary.to_csv(

            REPORT_DIR /

            "performance_metrics.csv",

            index=False

        )

        self.performance_summary = performance_summary

        logger.info(

            "Performance Metrics Saved"

        )

        print()

        print(

            performance_summary

        )

        print()

        logger.info("=" * 80)

    # -------------------------------------------------------------------------
    # Training Time Ranking
    # -------------------------------------------------------------------------

    def training_time_ranking(self):

        logger.info("=" * 80)
        logger.info("TRAINING TIME RANKING")
        logger.info("=" * 80)

        ranking = self.performance_df.sort_values(

            "Training Time (sec)"

        ).copy()

        ranking.insert(

            0,

            "Rank",

            range(

                1,

                len(ranking) + 1

            )

        )

        ranking.to_csv(

            REPORT_DIR /

            "training_time_performance.csv",

            index=False

        )

        self.training_ranking = ranking

        logger.info(

            "Training Time Ranking Saved"

        )

        print()

        print(

            ranking

        )

        print()

        logger.info("=" * 80)
            # -------------------------------------------------------------------------
    # Consensus Analysis
    # -------------------------------------------------------------------------

    def consensus_analysis(self):

        logger.info("=" * 80)
        logger.info("CONSENSUS ANALYSIS")
        logger.info("=" * 80)

        total = len(self.df)

        summary = []

        for level in [

            "Critical",

            "High",

            "Medium",

            "Low"

        ]:

            subset = self.df[

                self.df["risk_level"] == level

            ]

            summary.append(

                {

                    "Risk Level":

                        level,

                    "Employees":

                        len(subset),

                    "Percentage":

                        round(

                            len(subset) * 100 / total,

                            2

                        ),

                    "Average Weighted Score":

                        round(

                            subset["weighted_score"].mean(),

                            2

                        )

                        if len(subset)

                        else 0

                }

            )

        consensus_summary = pd.DataFrame(

            summary

        )

        consensus_summary.to_csv(

            REPORT_DIR /

            "consensus_summary.csv",

            index=False

        )

        self.consensus_summary = consensus_summary

        logger.info(

            "Consensus Summary Saved"

        )

        print()

        print(

            consensus_summary

        )

        print()

        logger.info("=" * 80)

    # -------------------------------------------------------------------------
    # Classification Metrics
    # -------------------------------------------------------------------------

    def classification_metrics(self):

        logger.info("=" * 80)
        logger.info("CLASSIFICATION METRICS")
        logger.info("=" * 80)

        # -------------------------------------------------------------
        # Detect Ground Truth Labels
        # -------------------------------------------------------------

        possible_columns = [

            "label",

            "Label",

            "target",

            "Target",

            "ground_truth",

            "GroundTruth",

            "actual"

        ]

        label_column = None

        for column in possible_columns:

            if column in self.df.columns:

                label_column = column

                break

        # -------------------------------------------------------------
        # No Labels Available
        # -------------------------------------------------------------

        if label_column is None:

            logger.warning(

                "Ground Truth Labels Not Available."

            )

            logger.warning(

                "Classification Metrics Skipped."

            )

            report = pd.DataFrame(

                [

                    {

                        "Metric":

                            "Status",

                        "Value":

                            "Ground Truth Labels Not Available"

                    }

                ]

            )

            report.to_csv(

                REPORT_DIR /

                "classification_report.csv",

                index=False

            )

            self.classification_report = report

            logger.info("=" * 80)

            return

        # -------------------------------------------------------------
        # Binary Conversion
        # -------------------------------------------------------------

        y_true = self.df[

            label_column

        ]

        y_pred = (

            self.df["risk_level"]

            !=

            "Low"

        ).astype(int)

        # -------------------------------------------------------------
        # Metrics
        # -------------------------------------------------------------

        accuracy = accuracy_score(

            y_true,

            y_pred

        )

        precision = precision_score(

            y_true,

            y_pred,

            zero_division=0

        )

        recall = recall_score(

            y_true,

            y_pred,

            zero_division=0

        )

        f1 = f1_score(

            y_true,

            y_pred,

            zero_division=0

        )

        metrics = pd.DataFrame(

            [

                {

                    "Metric":

                        "Accuracy",

                    "Value":

                        round(

                            accuracy,

                            4

                        )

                },

                {

                    "Metric":

                        "Precision",

                    "Value":

                        round(

                            precision,

                            4

                        )

                },

                {

                    "Metric":

                        "Recall",

                    "Value":

                        round(

                            recall,

                            4

                        )

                },

                {

                    "Metric":

                        "F1 Score",

                    "Value":

                        round(

                            f1,

                            4

                        )

                }

            ]

        )

        metrics.to_csv(

            REPORT_DIR /

            "classification_report.csv",

            index=False

        )

        self.classification_report = metrics

        logger.info(

            "Classification Report Saved"

        )

        print()

        print(

            metrics

        )

        print()

        logger.info("=" * 80)

    # -------------------------------------------------------------------------
    # System Statistics
    # -------------------------------------------------------------------------

    def system_statistics(self):

        logger.info("=" * 80)
        logger.info("SYSTEM STATISTICS")
        logger.info("=" * 80)

        runtime = round(

            time.time() -

            self.start_time,

            2

        )

        system = [

            {

                "Metric":

                    "Employees Processed",

                "Value":

                    len(self.df)

            },

            {

                "Metric":

                    "Machine Learning Models",

                "Value":

                    len(self.model_stats)

            },

            {

                "Metric":

                    "Features Generated",

                "Value":

                    len(self.numeric_features)

            },

            {

                "Metric":

                    "Reports Generated",

                "Value":

                    8

            },

            {

                "Metric":

                    "Execution Time (sec)",

                "Value":

                    runtime

            }

        ]

        system_df = pd.DataFrame(

            system

        )

        system_df.to_csv(

            REPORT_DIR /

            "system_statistics.csv",

            index=False

        )

        self.system_statistics_df = system_df

        logger.info(

            "System Statistics Saved"

        )

        print()

        print(

            system_df

        )

        print()

        logger.info("=" * 80)
            # -------------------------------------------------------------------------
    # Training Time Analysis
    # -------------------------------------------------------------------------

    def training_time_plot(self):

        logger.info("=" * 80)
        logger.info("GENERATING TRAINING TIME CHART")
        logger.info("=" * 80)

        plt.figure(figsize=(10, 6))

        plt.bar(

            self.performance_df["Model"],

            self.performance_df["Training Time (sec)"]

        )

        plt.xticks(rotation=30)

        plt.xlabel("Model")

        plt.ylabel("Training Time (Seconds)")

        plt.title("Model Training Time Comparison")

        plt.grid(True)

        plot_file = PLOT_DIR / "training_time_analysis.png"

        plt.savefig(

            plot_file,

            dpi=300,

            bbox_inches="tight"

        )

        plt.close()

        logger.info(f"Saved : {plot_file}")

    # -------------------------------------------------------------------------
    # Detection Rate Chart
    # -------------------------------------------------------------------------

    def detection_rate_plot(self):

        logger.info("=" * 80)
        logger.info("GENERATING DETECTION RATE CHART")
        logger.info("=" * 80)

        plt.figure(figsize=(10, 6))

        plt.bar(

            self.performance_df["Model"],

            self.performance_df["Detection Rate (%)"]

        )

        plt.xticks(rotation=30)

        plt.xlabel("Model")

        plt.ylabel("Detection Rate (%)")

        plt.title("Model Detection Rate")

        plt.grid(True)

        plot_file = PLOT_DIR / "model_detection_rate.png"

        plt.savefig(

            plot_file,

            dpi=300,

            bbox_inches="tight"

        )

        plt.close()

        logger.info(f"Saved : {plot_file}")

    # -------------------------------------------------------------------------
    # Accuracy Comparison
    # -------------------------------------------------------------------------

    def accuracy_plot(self):

        logger.info("=" * 80)
        logger.info("GENERATING ACCURACY COMPARISON")
        logger.info("=" * 80)

        if len(self.classification_report) == 1:

            logger.warning(

                "Accuracy Plot Skipped (No Ground Truth Labels)."

            )

            return

        plt.figure(figsize=(7, 5))

        plt.bar(

            self.classification_report["Metric"],

            self.classification_report["Value"]

        )

        plt.ylabel("Score")

        plt.title("Classification Metrics")

        plt.grid(True)

        plot_file = PLOT_DIR / "accuracy_comparison.png"

        plt.savefig(

            plot_file,

            dpi=300,

            bbox_inches="tight"

        )

        plt.close()

        logger.info(f"Saved : {plot_file}")

    # -------------------------------------------------------------------------
    # Dataset Quality Chart
    # -------------------------------------------------------------------------

    def dataset_quality_plot(self):

        logger.info("=" * 80)
        logger.info("GENERATING DATASET QUALITY CHART")
        logger.info("=" * 80)

        quality = self.dataset_statistics_df[

            self.dataset_statistics_df["Metric"].isin(

                [

                    "Missing Percentage",

                    "Dataset Completeness (%)"

                ]

            )

        ]

        plt.figure(figsize=(6, 5))

        plt.bar(

            quality["Metric"],

            quality["Value"]

        )

        plt.title("Dataset Quality")

        plt.ylabel("Percentage")

        plt.grid(True)

        plot_file = PLOT_DIR / "dataset_quality.png"

        plt.savefig(

            plot_file,

            dpi=300,

            bbox_inches="tight"

        )

        plt.close()

        logger.info(f"Saved : {plot_file}")

    # -------------------------------------------------------------------------
    # Risk Level Summary
    # -------------------------------------------------------------------------

    def risk_level_summary_plot(self):

        logger.info("=" * 80)
        logger.info("GENERATING RISK LEVEL SUMMARY")
        logger.info("=" * 80)

        plt.figure(figsize=(8, 6))

        plt.bar(

            self.risk_distribution_df["Risk Level"],

            self.risk_distribution_df["Employees"]

        )

        plt.xlabel("Risk Level")

        plt.ylabel("Employees")

        plt.title("Employee Risk Level Distribution")

        plt.grid(True)

        plot_file = PLOT_DIR / "risk_level_summary.png"

        plt.savefig(

            plot_file,

            dpi=300,

            bbox_inches="tight"

        )

        plt.close()

        logger.info(f"Saved : {plot_file}")

    # -------------------------------------------------------------------------
    # Visualization Summary
    # -------------------------------------------------------------------------

    def visualization_summary(self):

        logger.info("=" * 80)
        logger.info("VISUALIZATION SUMMARY")
        logger.info("=" * 80)

        logger.info(

            f"Training Time Plot : "
            f"{PLOT_DIR/'training_time_analysis.png'}"

        )

        logger.info(

            f"Detection Rate Plot : "
            f"{PLOT_DIR/'model_detection_rate.png'}"

        )

        logger.info(

            f"Dataset Quality Plot : "
            f"{PLOT_DIR/'dataset_quality.png'}"

        )

        logger.info(

            f"Risk Level Plot : "
            f"{PLOT_DIR/'risk_level_summary.png'}"

        )

        logger.info("=" * 80)
        # =============================================================================
# Main
# =============================================================================

def main():

    metrics = PerformanceMetrics()

    metrics.load_data()

    metrics.dataset_summary()

    metrics.dataset_statistics()

    metrics.feature_statistics()

    metrics.risk_distribution()

    metrics.model_performance()

    metrics.overall_performance()

    metrics.training_time_ranking()

    metrics.consensus_analysis()

    metrics.classification_metrics()

    metrics.system_statistics()

    metrics.training_time_plot()

    metrics.detection_rate_plot()

    metrics.accuracy_plot()

    metrics.dataset_quality_plot()

    metrics.risk_level_summary_plot()

    metrics.visualization_summary()

    logger.info("=" * 80)
    logger.info("PERFORMANCE METRICS SUMMARY")
    logger.info("=" * 80)

    logger.info(
        f"Employees Evaluated : {len(metrics.df):,}"
    )

    logger.info(
        f"Models Evaluated : {len(metrics.model_stats)}"
    )

    logger.info(
        f"Numeric Features : {len(metrics.numeric_features)}"
    )

    logger.info(
        f"Reports Generated : 9"
    )

    logger.info(
        f"Plots Generated : 5"
    )

    logger.info(
        f"Reports Folder : {REPORT_DIR}"
    )

    logger.info(
        f"Plots Folder : {PLOT_DIR}"
    )

    logger.info("=" * 80)

    logger.info("PERFORMANCE METRICS COMPLETED SUCCESSFULLY")

    logger.info("=" * 80)


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":

    main()
    