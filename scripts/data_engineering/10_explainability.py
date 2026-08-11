"""
===============================================================================
Module        : Explainable AI
File          : 10_explainability.py
Project       : Insider Threat Behavioral Intelligence System

Description:
    Generates human-readable explanations for employee risk predictions
    produced by the multi-model anomaly detection pipeline.

Input
-----
datasets/exports/
    employee_final_risk_report.parquet

datasets/features/
    employee_features.parquet

reports/
    model_statistics.csv

Outputs
-------
reports/
    employee_explanations.csv
    feature_importance.csv
    top_behavioral_factors.csv
    critical_employee_summary.csv

plots/
    feature_importance.png
    behavioral_factor_ranking.png
    critical_employee_distribution.png

Author
------
Nandan Kabra
===============================================================================
"""

from pathlib import Path
import logging

import duckdb
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

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

RISK_FILE = EXPORT_DIR / "employee_final_risk_report.parquet"

FEATURE_FILE = FEATURE_DIR / "employee_features.parquet"

MODEL_STATS_FILE = REPORT_DIR / "model_statistics.csv"

# =============================================================================
# Explainability Class
# =============================================================================

class ExplainabilityEngine:

    def __init__(self):

        self.conn = duckdb.connect()

        logger.info("=" * 80)
        logger.info("EXPLAINABLE AI ENGINE")
        logger.info("=" * 80)

        self.risk_df = None

        self.feature_df = None

        self.model_stats = None

        self.df = None

        self.feature_columns = []
    # -------------------------------------------------------------------------
    # Load Datasets
    # -------------------------------------------------------------------------

    def load_data(self):

        logger.info("=" * 80)
        logger.info("LOADING DATASETS")
        logger.info("=" * 80)

        # -------------------------------------------------------------
        # Check Files
        # -------------------------------------------------------------

        if not RISK_FILE.exists():

            raise FileNotFoundError(
                f"Risk Report Not Found:\n{RISK_FILE}"
            )

        if not FEATURE_FILE.exists():

            raise FileNotFoundError(
                f"Feature Dataset Not Found:\n{FEATURE_FILE}"
            )

        if not MODEL_STATS_FILE.exists():

            raise FileNotFoundError(
                f"Model Statistics Not Found:\n{MODEL_STATS_FILE}"
            )

        # -------------------------------------------------------------
        # Load Risk Report
        # -------------------------------------------------------------

        logger.info("Loading Employee Risk Report...")

        self.risk_df = self.conn.execute(f"""

            SELECT *

            FROM read_parquet(

                '{RISK_FILE.as_posix()}'

            )

        """).fetchdf()

        # -------------------------------------------------------------
        # Load Feature Dataset
        # -------------------------------------------------------------

        logger.info("Loading Employee Features...")

        self.feature_df = self.conn.execute(f"""

            SELECT *

            FROM read_parquet(

                '{FEATURE_FILE.as_posix()}'

            )

        """).fetchdf()

        # -------------------------------------------------------------
        # Load Model Statistics
        # -------------------------------------------------------------

        logger.info("Loading Model Statistics...")

        self.model_stats = pd.read_csv(

            MODEL_STATS_FILE

        )

        # -------------------------------------------------------------
        # Merge Datasets
        # -------------------------------------------------------------

        logger.info("Merging Risk Report with Feature Dataset...")

        self.df = pd.merge(

            self.risk_df,

            self.feature_df,

            on="user",

            how="left"

        )

        # -------------------------------------------------------------
        # Remove Duplicate Columns
        # -------------------------------------------------------------

        self.df = self.df.loc[
            :,
            ~self.df.columns.duplicated()
        ]

        # -------------------------------------------------------------
        # Detect Numeric Features
        # -------------------------------------------------------------

        numeric = self.df.select_dtypes(

            include=np.number

        )

        self.feature_columns = list(

            numeric.columns

        )

        # -------------------------------------------------------------
        # Dataset Information
        # -------------------------------------------------------------

        logger.info(
            f"Employees Loaded : {len(self.df):,}"
        )

        logger.info(
            f"Risk Columns : {len(self.risk_df.columns)}"
        )

        logger.info(
            f"Feature Columns : {len(self.feature_df.columns)}"
        )

        logger.info(
            f"Numeric Features : {len(self.feature_columns)}"
        )

        logger.info(
            f"Models Evaluated : {len(self.model_stats)}"
        )

        logger.info("=" * 80)

    # -------------------------------------------------------------------------
    # Dataset Summary
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
            f"Numeric Features : {len(self.feature_columns)}"
        )

        logger.info(
            f"Risk Levels : "
            f"{self.df['risk_level'].nunique()}"
        )

        logger.info(
            f"Maximum Risk Score : "
            f"{self.df['weighted_score'].max():.2f}"
        )

        logger.info(
            f"Average Risk Score : "
            f"{self.df['weighted_score'].mean():.2f}"
        )

        logger.info("=" * 80)
            # -------------------------------------------------------------------------
    # Employee Explainability
    # -------------------------------------------------------------------------

    def generate_explanations(self):

        logger.info("=" * 80)
        logger.info("GENERATING EMPLOYEE EXPLANATIONS")
        logger.info("=" * 80)

        explanation_rows = []

        # ---------------------------------------------------------------------
        # Calculate Dataset Means
        # ---------------------------------------------------------------------

        means = {}

        important_features = [

            "after_hours_activity",

            "weekend_activity",

            "device_events",

            "web_events",

            "email_events",

            "file_events",

            "total_events",

            "active_days"

        ]

        for feature in important_features:

            if feature in self.df.columns:

                means[feature] = self.df[feature].mean()

        # ---------------------------------------------------------------------
        # Generate Explanation For Every Employee
        # ---------------------------------------------------------------------

        for _, row in self.df.iterrows():

            reasons = []

            # -------------------------------------------------------------
            # Consensus Percentage
            # -------------------------------------------------------------

            consensus = row.get(

                "Consensus_Percentage",

                row.get("consensus_percentage", 0)

            )

            if consensus >= 90:

                reasons.append(

                    "Detected consistently by nearly all anomaly detection models"

                )

            elif consensus >= 70:

                reasons.append(

                    "Detected by most anomaly detection models"

                )

            elif consensus >= 50:

                reasons.append(

                    "Detected by multiple anomaly detection models"

                )

            # -------------------------------------------------------------
            # After Hours Activity
            # -------------------------------------------------------------

            if (

                "after_hours_activity" in row.index

                and

                row["after_hours_activity"] >

                means.get("after_hours_activity", 0)

            ):

                reasons.append(

                    "High after-hours activity"

                )

            # -------------------------------------------------------------
            # Weekend Activity
            # -------------------------------------------------------------

            if (

                "weekend_activity" in row.index

                and

                row["weekend_activity"] >

                means.get("weekend_activity", 0)

            ):

                reasons.append(

                    "High weekend activity"

                )

            # -------------------------------------------------------------
            # Device Usage
            # -------------------------------------------------------------

            if (

                "device_events" in row.index

                and

                row["device_events"] >

                means.get("device_events", 0)

            ):

                reasons.append(

                    "Excessive device activity"

                )

            # -------------------------------------------------------------
            # Web Usage
            # -------------------------------------------------------------

            if (

                "web_events" in row.index

                and

                row["web_events"] >

                means.get("web_events", 0)

            ):

                reasons.append(

                    "High web browsing activity"

                )

            # -------------------------------------------------------------
            # Email Activity
            # -------------------------------------------------------------

            if (

                "email_events" in row.index

                and

                row["email_events"] >

                means.get("email_events", 0)

            ):

                reasons.append(

                    "High email communication"

                )

            # -------------------------------------------------------------
            # File Activity
            # -------------------------------------------------------------

            if (

                "file_events" in row.index

                and

                row["file_events"] >

                means.get("file_events", 0)

            ):

                reasons.append(

                    "Frequent file access"

                )

            # -------------------------------------------------------------
            # Total Events
            # -------------------------------------------------------------

            if (

                "total_events" in row.index

                and

                row["total_events"] >

                means.get("total_events", 0)

            ):

                reasons.append(

                    "Large volume of overall activity"

                )

            # -------------------------------------------------------------
            # Active Days
            # -------------------------------------------------------------

            if (

                "active_days" in row.index

                and

                row["active_days"] >

                means.get("active_days", 0)

            ):

                reasons.append(

                    "High number of active working days"

                )

            # -------------------------------------------------------------
            # Weighted Score
            # -------------------------------------------------------------

            score = row.get(

                "weighted_score",

                0

            )

            if score >= 90:

                reasons.append(

                    "Extremely high overall behavioral anomaly score"

                )

            elif score >= 75:

                reasons.append(

                    "Very high behavioral anomaly score"

                )

            elif score >= 60:

                reasons.append(

                    "Elevated behavioral anomaly score"

                )

            # -------------------------------------------------------------
            # Default Explanation
            # -------------------------------------------------------------

            if len(reasons) == 0:

                reasons.append(

                    "No significant behavioral anomalies detected"

                )

            # -------------------------------------------------------------
            # Store Employee Explanation
            # -------------------------------------------------------------

            explanation_rows.append(

                {

                    "user":

                        row["user"],

                    "risk_level":

                        row["risk_level"],

                    "weighted_score":

                        round(score, 2),

                    "Consensus_Percentage":

                        round(consensus, 2),

                    "Explanation":

                        " | ".join(reasons)

                }

            )

        # ---------------------------------------------------------------------
        # Export
        # ---------------------------------------------------------------------

        explanation_df = pd.DataFrame(

            explanation_rows

        )

        explanation_df.to_csv(

            REPORT_DIR /

            "employee_explanations.csv",

            index=False

        )

        self.explanation_df = explanation_df

        logger.info(

            "Employee Explanation Report Saved"

        )

        logger.info("=" * 80)

        print()

        print(

            explanation_df.head(20)

        )

        print()
            # -------------------------------------------------------------------------
    # Feature Importance Analysis
    # -------------------------------------------------------------------------

    def feature_importance(self):

        logger.info("=" * 80)
        logger.info("FEATURE IMPORTANCE ANALYSIS")
        logger.info("=" * 80)

        statistics = []

        excluded = [

            "Rank",
            "weighted_score",
            "Consensus_Percentage",
            "consensus_percentage"

        ]

        for column in self.feature_columns:

            if column in excluded:

                continue

            try:

                values = self.df[column].dropna()

                if len(values) == 0:

                    continue

                statistics.append(

                    {

                        "Feature": column,

                        "Mean": values.mean(),

                        "Median": values.median(),

                        "Minimum": values.min(),

                        "Maximum": values.max(),

                        "Standard Deviation": values.std(),

                        "Variance": values.var(),

                        "Coefficient of Variation":

                            (

                                values.std() /

                                values.mean()

                            )

                            if values.mean() != 0

                            else 0

                    }

                )

            except Exception:

                continue

        feature_df = pd.DataFrame(

            statistics

        )

        feature_df = feature_df.sort_values(

            "Coefficient of Variation",

            ascending=False

        )

        feature_df.to_csv(

            REPORT_DIR /

            "feature_importance.csv",

            index=False

        )

        self.feature_importance_df = feature_df

        logger.info(

            "Feature Importance Report Saved"

        )

        print()

        print(

            feature_df.head(15)

        )

        print()

        logger.info("=" * 80)

    # -------------------------------------------------------------------------
    # Behavioral Factor Ranking
    # -------------------------------------------------------------------------

    def behavioral_factor_ranking(self):

        logger.info("=" * 80)
        logger.info("BEHAVIORAL FACTOR RANKING")
        logger.info("=" * 80)

        candidate_features = [

            "after_hours_activity",

            "weekend_activity",

            "device_events",

            "web_events",

            "email_events",

            "file_events",

            "total_events",

            "active_days"

        ]

        ranking = []

        for feature in candidate_features:

            if feature not in self.df.columns:

                continue

            suspicious = self.df[

                self.df["risk_level"].isin(

                    [

                        "Critical",

                        "High"

                    ]

                )

            ]

            if len(suspicious) == 0:

                continue

            ranking.append(

                {

                    "Behavior":

                        feature,

                    "Average Value":

                        suspicious[feature].mean(),

                    "Maximum Value":

                        suspicious[feature].max(),

                    "Minimum Value":

                        suspicious[feature].min(),

                    "Standard Deviation":

                        suspicious[feature].std()

                }

            )

        ranking_df = pd.DataFrame(

            ranking

        )

        ranking_df = ranking_df.sort_values(

            "Average Value",

            ascending=False

        )

        ranking_df.insert(

            0,

            "Rank",

            range(

                1,

                len(ranking_df) + 1

            )

        )

        ranking_df.to_csv(

            REPORT_DIR /

            "top_behavioral_factors.csv",

            index=False

        )

        self.behavior_df = ranking_df

        logger.info(

            "Behavioral Factor Ranking Saved"

        )

        print()

        print(

            ranking_df

        )

        print()

        logger.info("=" * 80)
            # -------------------------------------------------------------------------
    # Critical Employee Summary
    # -------------------------------------------------------------------------

    def critical_employee_summary(self):

        logger.info("=" * 80)
        logger.info("GENERATING CRITICAL EMPLOYEE SUMMARY")
        logger.info("=" * 80)

        critical = self.df[

            self.df["risk_level"] == "Critical"

        ].copy()

        if len(critical) == 0:

            logger.warning(
                "No Critical Employees Found."
            )

            return

        critical = critical.sort_values(

            "weighted_score",

            ascending=False

        )

        summary_columns = [

            "user",

            "weighted_score",

            "Consensus_Percentage",

            "risk_level"

        ]

        optional_columns = [

            "department",

            "role",

            "after_hours_activity",

            "weekend_activity",

            "device_events",

            "web_events",

            "email_events",

            "file_events",

            "total_events"

        ]

        for column in optional_columns:

            if column in critical.columns:

                summary_columns.append(column)

        critical_summary = critical[summary_columns]

        critical_summary.to_csv(

            REPORT_DIR /

            "critical_employee_summary.csv",

            index=False

        )

        self.critical_summary = critical_summary

        logger.info(

            "Critical Employee Summary Saved"

        )

        print()

        print(

            critical_summary.head(20)

        )

        print()

        logger.info("=" * 80)

    # -------------------------------------------------------------------------
    # Risk Level Statistics
    # -------------------------------------------------------------------------

    def risk_statistics(self):

        logger.info("=" * 80)
        logger.info("RISK LEVEL STATISTICS")
        logger.info("=" * 80)

        statistics = []

        total = len(self.df)

        for level in [

            "Critical",

            "High",

            "Medium",

            "Low"

        ]:

            subset = self.df[

                self.df["risk_level"] == level

            ]

            if len(subset) == 0:

                continue

            statistics.append(

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

                    "Average Score":

                        round(

                            subset["weighted_score"].mean(),

                            2

                        ),

                    "Maximum Score":

                        round(

                            subset["weighted_score"].max(),

                            2

                        ),

                    "Minimum Score":

                        round(

                            subset["weighted_score"].min(),

                            2

                        )

                }

            )

        stats_df = pd.DataFrame(

            statistics

        )

        stats_df.to_csv(

            REPORT_DIR /

            "risk_level_statistics.csv",

            index=False

        )

        self.risk_stats = stats_df

        logger.info(

            "Risk Level Statistics Saved"

        )

        print()

        print(

            stats_df

        )

        print()

        logger.info("=" * 80)

    # -------------------------------------------------------------------------
    # Explainability Summary
    # -------------------------------------------------------------------------

    def explainability_summary(self):

        logger.info("=" * 80)
        logger.info("EXPLAINABILITY SUMMARY")
        logger.info("=" * 80)

        logger.info(

            f"Employees Processed : {len(self.df):,}"

        )

        logger.info(

            f"Critical Employees : "

            f"{len(self.df[self.df['risk_level']=='Critical'])}"

        )

        logger.info(

            f"High Risk Employees : "

            f"{len(self.df[self.df['risk_level']=='High'])}"

        )

        logger.info(

            f"Medium Risk Employees : "

            f"{len(self.df[self.df['risk_level']=='Medium'])}"

        )

        logger.info(

            f"Low Risk Employees : "

            f"{len(self.df[self.df['risk_level']=='Low'])}"

        )

        logger.info(

            f"Reports Folder : {REPORT_DIR}"

        )

        logger.info("=" * 80)
            # -------------------------------------------------------------------------
    # Feature Importance Chart
    # -------------------------------------------------------------------------

    def feature_importance_plot(self):

        logger.info("=" * 80)
        logger.info("GENERATING FEATURE IMPORTANCE CHART")
        logger.info("=" * 80)

        if self.feature_importance_df.empty:

            logger.warning("Feature Importance Dataset Empty.")

            return

        top_features = self.feature_importance_df.head(15)

        plt.figure(figsize=(12, 7))

        plt.barh(

            top_features["Feature"],

            top_features["Coefficient of Variation"]

        )

        plt.title(

            "Top Behavioral Features"

        )

        plt.xlabel(

            "Coefficient of Variation"

        )

        plt.ylabel(

            "Feature"

        )

        plt.grid(True)

        plot_file = PLOT_DIR / "feature_importance.png"

        plt.savefig(

            plot_file,

            dpi=300,

            bbox_inches="tight"

        )

        plt.close()

        logger.info(f"Saved : {plot_file}")

    # -------------------------------------------------------------------------
    # Behavioral Factor Ranking
    # -------------------------------------------------------------------------

    def behavioral_factor_plot(self):

        logger.info("=" * 80)
        logger.info("GENERATING BEHAVIORAL FACTOR CHART")
        logger.info("=" * 80)

        if self.behavior_df.empty:

            logger.warning("Behavior Dataset Empty.")

            return

        plt.figure(figsize=(10, 6))

        plt.bar(

            self.behavior_df["Behavior"],

            self.behavior_df["Average Value"]

        )

        plt.xticks(rotation=30)

        plt.title(

            "Behavioral Factor Ranking"

        )

        plt.ylabel(

            "Average Activity"

        )

        plt.grid(True)

        plot_file = PLOT_DIR / "behavioral_factor_ranking.png"

        plt.savefig(

            plot_file,

            dpi=300,

            bbox_inches="tight"

        )

        plt.close()

        logger.info(f"Saved : {plot_file}")

    # -------------------------------------------------------------------------
    # Risk Level Distribution
    # -------------------------------------------------------------------------

    def critical_distribution_plot(self):

        logger.info("=" * 80)
        logger.info("GENERATING RISK DISTRIBUTION")
        logger.info("=" * 80)

        distribution = self.df["risk_level"].value_counts()

        plt.figure(figsize=(8, 6))

        plt.bar(

            distribution.index,

            distribution.values

        )

        plt.title(

            "Employee Risk Level Distribution"

        )

        plt.xlabel(

            "Risk Level"

        )

        plt.ylabel(

            "Employees"

        )

        plt.grid(True)

        plot_file = PLOT_DIR / "critical_employee_distribution.png"

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
        logger.info("VISUALIZATIONS GENERATED")
        logger.info("=" * 80)

        logger.info(

            f"Feature Importance Plot : "

            f"{PLOT_DIR / 'feature_importance.png'}"

        )

        logger.info(

            f"Behavior Ranking Plot : "

            f"{PLOT_DIR / 'behavioral_factor_ranking.png'}"

        )

        logger.info(

            f"Risk Distribution Plot : "

            f"{PLOT_DIR / 'critical_employee_distribution.png'}"

        )

        logger.info("=" * 80)
        # =============================================================================
# Main
# =============================================================================

def main():

    engine = ExplainabilityEngine()

    engine.load_data()

    engine.dataset_summary()

    engine.generate_explanations()

    engine.feature_importance()

    engine.behavioral_factor_ranking()

    engine.critical_employee_summary()

    engine.risk_statistics()

    engine.feature_importance_plot()

    engine.behavioral_factor_plot()

    engine.critical_distribution_plot()

    engine.visualization_summary()

    engine.explainability_summary()

    logger.info("=" * 80)
    logger.info("EXPLAINABILITY PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("=" * 80)


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":

    main()
    