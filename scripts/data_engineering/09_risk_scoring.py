"""
===============================================================================
Module        : Employee Risk Scoring
File          : 09_risk_scoring.py
Project       : Insider Threat Behavioral Intelligence System

Description
-----------
Generates final employee risk scores using consensus from
multiple anomaly detection models.

Models Used
-----------
1. Isolation Forest
2. One-Class SVM
3. Local Outlier Factor
4. Elliptic Envelope
5. PCA
6. DBSCAN
7. KMeans

Author
------
Nandan Kabra
===============================================================================
"""

from pathlib import Path
import logging

import pandas as pd

# =============================================================================
# Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)
# =============================================================================
# Project Paths
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORT_DIR = PROJECT_ROOT / "reports"

EXPORT_DIR = PROJECT_ROOT / "datasets" / "exports"

EXPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

CONSENSUS_FILE = (
    REPORT_DIR /
    "consensus_predictions.csv"
)

MODEL_COMPARISON_FILE = (
    REPORT_DIR /
    "model_comparison.csv"
)

OUTPUT_CSV = (
    EXPORT_DIR /
    "employee_final_risk_report.csv"
)

OUTPUT_PARQUET = (
    EXPORT_DIR /
    "employee_final_risk_report.parquet"
)
# =============================================================================
# Risk Scoring
# =============================================================================

class RiskScoring:

    def __init__(self):

        logger.info("=" * 80)
        logger.info("EMPLOYEE RISK SCORING")
        logger.info("=" * 80)

        self.df = None

        self.model_stats = None
            # =========================================================================
    # Load Files
    # =========================================================================

    def load_data(self):

        logger.info("Loading Consensus Dataset...")

        self.df = pd.read_csv(
            CONSENSUS_FILE
        )

        logger.info("Loading Model Statistics...")

        self.model_stats = pd.read_csv(
            MODEL_COMPARISON_FILE
        )

        logger.info(
            f"Employees Loaded : {len(self.df):,}"
        )

        logger.info(
            f"Models : {len(self.model_stats)}"
        )

        logger.info("=" * 80)
            # =========================================================================
    # Calculate Final Risk Score
    # =========================================================================

    def calculate_risk_score(self):

        logger.info("=" * 80)
        logger.info("CALCULATING FINAL RISK SCORE")
        logger.info("=" * 80)

        # ---------------------------------------------------------------------
        # Model Weights
        # ---------------------------------------------------------------------

        weights = {

            "Isolation Forest":0.20,

            "One-Class SVM":0.15,

            "LOF":0.15,

            "Elliptic Envelope":0.10,

            "PCA":0.10,

            "DBSCAN":0.15,

            "KMeans":0.15

        }

        score = 0

        for model, weight in weights.items():

            column = model + "_Prediction"

            if column in self.df.columns:

                score += (

                    (self.df[column] == "Suspicious")

                    .astype(float)

                    * weight

                )

        self.df["weighted_score"] = score * 100

        logger.info("Weighted Risk Score Generated")

        logger.info("=" * 80)
            # =========================================================================
    # Assign Risk Levels
    # =========================================================================

    def assign_risk_levels(self):

        logger.info("=" * 80)
        logger.info("ASSIGNING RISK LEVELS")
        logger.info("=" * 80)

        conditions = [

            self.df["weighted_score"] >= 80,

            self.df["weighted_score"] >= 60,

            self.df["weighted_score"] >= 30,

            self.df["weighted_score"] < 30

        ]

        labels = [

            "Critical",

            "High",

            "Medium",

            "Low"

        ]

        self.df["risk_level"] = "Low"

        self.df.loc[
            self.df["weighted_score"] >= 30,
            "risk_level"
        ] = "Medium"

        self.df.loc[
            self.df["weighted_score"] >= 60,
            "risk_level"
        ] = "High"

        self.df.loc[
            self.df["weighted_score"] >= 80,
            "risk_level"
        ] = "Critical"

        logger.info("Risk Levels Assigned")

        logger.info("=" * 80)
            # =========================================================================
    # Employee Ranking
    # =========================================================================

    def rank_employees(self):

        logger.info("=" * 80)
        logger.info("RANKING EMPLOYEES")
        logger.info("=" * 80)

        self.df = self.df.sort_values(

            by=[

                "weighted_score",

                "Consensus_Percentage"

            ],

            ascending=False

        )

        self.df.reset_index(

            drop=True,

            inplace=True

        )

        self.df["Rank"] = self.df.index + 1

        logger.info("Ranking Completed")

        logger.info("=" * 80)
            # =========================================================================
    # Export Reports
    # =========================================================================

    def export_reports(self):

        logger.info("=" * 80)
        logger.info("EXPORTING FINAL REPORTS")
        logger.info("=" * 80)

        self.df.to_csv(
            OUTPUT_CSV,
            index=False
        )

        self.df.to_parquet(
            OUTPUT_PARQUET,
            index=False
        )

        logger.info(f"CSV Saved      : {OUTPUT_CSV}")
        logger.info(f"Parquet Saved  : {OUTPUT_PARQUET}")

        top100 = self.df.head(100)

        top100.to_csv(
            EXPORT_DIR / "top_100_high_risk.csv",
            index=False
        )

        critical = self.df[
            self.df["risk_level"] == "Critical"
        ]

        critical.to_csv(
            EXPORT_DIR / "critical_employees.csv",
            index=False
        )

        logger.info("Top 100 Report Saved")
        logger.info("Critical Employees Report Saved")

        logger.info("=" * 80)
            # =========================================================================
    # Dashboard Dataset
    # =========================================================================

    def dashboard_dataset(self):

        logger.info("=" * 80)
        logger.info("CREATING DASHBOARD DATASET")
        logger.info("=" * 80)

        dashboard_columns = [

            "Rank",

            "user",

            "weighted_score",

            "Consensus_Percentage",

            "Suspicious_Count",

            "risk_level"

        ]

        dashboard = self.df[dashboard_columns]

        dashboard.to_csv(

            EXPORT_DIR /

            "dashboard_dataset.csv",

            index=False

        )

        logger.info("Dashboard Dataset Saved")

        logger.info("=" * 80)
            # =========================================================================
    # Top 20 Employees
    # =========================================================================

    def top_employees(self):

        logger.info("=" * 80)
        logger.info("TOP 20 EMPLOYEES")
        logger.info("=" * 80)

        columns = [

            "Rank",

            "user",

            "weighted_score",

            "Consensus_Percentage",

            "risk_level"

        ]

        print()

        print(

            self.df[columns]

            .head(20)

        )

        print()

        logger.info("=" * 80)
            # =========================================================================
    # Summary
    # =========================================================================

    def summary(self):

        logger.info("=" * 80)
        logger.info("FINAL RISK SCORING SUMMARY")
        logger.info("=" * 80)

        logger.info(
            f"Employees Evaluated : {len(self.df):,}"
        )

        logger.info(
            f"Critical : {(self.df['risk_level']=='Critical').sum()}"
        )

        logger.info(
            f"High : {(self.df['risk_level']=='High').sum()}"
        )

        logger.info(
            f"Medium : {(self.df['risk_level']=='Medium').sum()}"
        )

        logger.info(
            f"Low : {(self.df['risk_level']=='Low').sum()}"
        )

        logger.info("=" * 80)

        logger.info("RISK SCORING COMPLETED SUCCESSFULLY")

        logger.info("=" * 80)
        # =============================================================================
# Main
# =============================================================================

def main():

    scorer = RiskScoring()

    scorer.load_data()

    scorer.calculate_risk_score()

    scorer.assign_risk_levels()

    scorer.rank_employees()

    scorer.export_reports()

    scorer.dashboard_dataset()

    scorer.top_employees()

    scorer.summary()


if __name__ == "__main__":

    main()
