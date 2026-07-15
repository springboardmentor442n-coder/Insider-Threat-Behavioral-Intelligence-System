"""
===============================================================================
Module        : Multi-Model Evaluation
File          : 08_model_evaluation.py
Project       : Insider Threat Behavioral Intelligence System

Description
-----------
Evaluates all trained anomaly detection models and generates
comparison reports, statistics and visualizations.

Models
------
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
# Project Paths
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PREDICTION_DIR = PROJECT_ROOT / "datasets" / "predictions"

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

PREDICTION_FILE = (
    PREDICTION_DIR /
    "all_model_predictions.parquet"
)

MODEL_COMPARISON_FILE = (
    REPORT_DIR /
    "model_comparison.csv"
)

TRAINING_TIME_FILE = (
    REPORT_DIR /
    "training_times.csv"
)
# =============================================================================
# Model Evaluation Class
# =============================================================================

class ModelEvaluation:

    def __init__(self):

        logger.info("=" * 80)
        logger.info("MULTI MODEL EVALUATION")
        logger.info("=" * 80)

        self.predictions = None
        self.model_comparison = None
        self.training_times = None

    # =========================================================================
    # Load Data
    # =========================================================================

    def load_data(self):

        logger.info("Loading Prediction Dataset...")

        self.predictions = pd.read_parquet(
            PREDICTION_FILE
        )

        logger.info("Loading Model Comparison...")

        self.model_comparison = pd.read_csv(
            MODEL_COMPARISON_FILE
        )

        logger.info("Loading Training Times...")

        self.training_times = pd.read_csv(
            TRAINING_TIME_FILE
        )

        logger.info(
            f"Employees Loaded : {len(self.predictions):,}"
        )

        logger.info(
            f"Models Evaluated : {len(self.model_comparison)}"
        )

        logger.info("=" * 80)

    # =========================================================================
    # Dataset Summary
    # =========================================================================

    def dataset_summary(self):

        logger.info("=" * 80)
        logger.info("DATASET SUMMARY")
        logger.info("=" * 80)

        logger.info(
            f"Employees : {len(self.predictions):,}"
        )

        logger.info(
            f"Models : {len(self.model_comparison)}"
        )

        logger.info(
            f"Prediction Columns : {len(self.predictions.columns)}"
        )

        logger.info("=" * 80)
            # =========================================================================
    # Model Comparison
    # =========================================================================

    def model_comparison_report(self):

        logger.info("=" * 80)
        logger.info("MODEL COMPARISON")
        logger.info("=" * 80)

        comparison = self.model_comparison.sort_values(
            by="Suspicious Employees",
            ascending=False
        )

        print()
        print(comparison)
        print()

        comparison.to_csv(
            REPORT_DIR / "model_ranking.csv",
            index=False
        )

        logger.info("Model Ranking Saved")

        logger.info("=" * 80)
            # =========================================================================
    # Training Time Report
    # =========================================================================

    def training_time_report(self):

        logger.info("=" * 80)
        logger.info("TRAINING TIME REPORT")
        logger.info("=" * 80)

        training = self.training_times.sort_values(
            by="Training Time",
            ascending=True
        )

        print()
        print(training)
        print()

        training.to_csv(
            REPORT_DIR / "training_time_ranking.csv",
            index=False
        )

        fastest = training.iloc[0]

        slowest = training.iloc[-1]

        logger.info(
            f"Fastest Model : {fastest['Model']}"
        )

        logger.info(
            f"Slowest Model : {slowest['Model']}"
        )

        logger.info("=" * 80)
            # =========================================================================
    # Evaluation Summary
    # =========================================================================

    def evaluation_summary(self):

        logger.info("=" * 80)
        logger.info("EVALUATION SUMMARY")
        logger.info("=" * 80)

        summary_file = REPORT_DIR / "evaluation_summary.txt"

        with open(summary_file, "w") as f:

            f.write("=" * 70 + "\n")
            f.write("MULTI MODEL EVALUATION SUMMARY\n")
            f.write("=" * 70 + "\n\n")

            f.write(
                f"Employees Evaluated : {len(self.predictions):,}\n"
            )

            f.write(
                f"Models Evaluated : {len(self.model_comparison)}\n\n"
            )

            f.write("Model Comparison\n")
            f.write("-" * 70 + "\n")

            f.write(
                self.model_comparison.to_string(index=False)
            )

        logger.info(
            f"Summary Saved : {summary_file}"
        )

        logger.info("=" * 80)
            # =========================================================================
    # Consensus Analysis
    # =========================================================================

    def consensus_analysis(self):

        logger.info("=" * 80)
        logger.info("CONSENSUS ANALYSIS")
        logger.info("=" * 80)

        prediction_columns = [

            column

            for column in self.predictions.columns

            if column.endswith("_Prediction")

        ]

        consensus = self.predictions.copy()

        consensus["Suspicious_Count"] = (

            consensus[prediction_columns]

            == "Suspicious"

        ).sum(axis=1)

        consensus["Consensus_Percentage"] = (

            consensus["Suspicious_Count"]

            / len(prediction_columns)

        ) * 100

        consensus = consensus.sort_values(

            by="Consensus_Percentage",

            ascending=False

        )

        self.consensus = consensus

        consensus.to_csv(

            REPORT_DIR / "consensus_predictions.csv",

            index=False

        )

        logger.info("Consensus Report Saved")

        logger.info("=" * 80)
            # =========================================================================
    # Top Suspicious Employees
    # =========================================================================

    def top_suspicious(self):

        logger.info("=" * 80)
        logger.info("TOP SUSPICIOUS EMPLOYEES")
        logger.info("=" * 80)

        columns = [

            "user",

            "Suspicious_Count",

            "Consensus_Percentage"

        ]

        print()

        print(

            self.consensus[columns]

            .head(20)

        )

        print()

        self.consensus.head(100).to_csv(

            REPORT_DIR / "top_100_suspicious.csv",

            index=False

        )

        logger.info("Top 100 Report Saved")

        logger.info("=" * 80)
            # =========================================================================
    # Feature Statistics
    # =========================================================================

    def feature_statistics(self):

        logger.info("=" * 80)
        logger.info("MODEL STATISTICS")
        logger.info("=" * 80)

        score_columns = [

            column

            for column in self.predictions.columns

            if column.endswith("_Score")

        ]

        stats = self.predictions[

            score_columns

        ].describe().T

        stats.to_csv(

            REPORT_DIR /

            "model_statistics.csv"

        )

        logger.info(

            "Model Statistics Saved"

        )

        logger.info("=" * 80)
            # =========================================================================
    # Detection Comparison Chart
    # =========================================================================

    def detection_chart(self):

        logger.info("=" * 80)
        logger.info("GENERATING DETECTION COMPARISON")
        logger.info("=" * 80)

        plt.figure(figsize=(10,6))

        plt.bar(

            self.model_comparison["Model"],

            self.model_comparison["Suspicious Employees"]

        )

        plt.xticks(rotation=45)

        plt.ylabel("Employees")

        plt.title("Suspicious Employees Detected")

        plt.tight_layout()

        file = PLOT_DIR / "model_detection_comparison.png"

        plt.savefig(file, dpi=300)

        plt.close()

        logger.info(f"Saved : {file}")\
            # =========================================================================
    # Training Time Comparison
    # =========================================================================

    def training_time_chart(self):

        logger.info("=" * 80)
        logger.info("GENERATING TRAINING TIME CHART")
        logger.info("=" * 80)

        plt.figure(figsize=(10,6))

        plt.bar(

            self.training_times["Model"],

            self.training_times["Training Time"]

        )

        plt.xticks(rotation=45)

        plt.ylabel("Seconds")

        plt.title("Training Time Comparison")

        plt.tight_layout()

        file = PLOT_DIR / "training_time_comparison.png"

        plt.savefig(file, dpi=300)

        plt.close()

        logger.info(f"Saved : {file}")
            # =========================================================================
    # Consensus Histogram
    # =========================================================================

    def consensus_chart(self):

        logger.info("=" * 80)
        logger.info("GENERATING CONSENSUS HISTOGRAM")
        logger.info("=" * 80)

        plt.figure(figsize=(10,6))

        plt.hist(

            self.consensus["Consensus_Percentage"],

            bins=10

        )

        plt.xlabel("Consensus %")

        plt.ylabel("Employees")

        plt.title("Consensus Distribution")

        plt.grid(True)

        plt.tight_layout()

        file = PLOT_DIR / "consensus_distribution.png"

        plt.savefig(file, dpi=300)

        plt.close()

        logger.info(f"Saved : {file}")
            # =========================================================================
    # Final Summary
    # =========================================================================

    def summary(self):

        logger.info("=" * 80)
        logger.info("MODEL EVALUATION COMPLETED")
        logger.info("=" * 80)

        fastest = self.training_times.sort_values(
            "Training Time"
        ).iloc[0]

        slowest = self.training_times.sort_values(
            "Training Time"
        ).iloc[-1]

        best = self.model_comparison.sort_values(
            "Suspicious Employees",
            ascending=False
        ).iloc[0]

        logger.info(
            f"Employees Evaluated : {len(self.predictions):,}"
        )

        logger.info(
            f"Models Evaluated : {len(self.model_comparison)}"
        )

        logger.info(
            f"Fastest Model : {fastest['Model']}"
        )

        logger.info(
            f"Slowest Model : {slowest['Model']}"
        )

        logger.info(
            f"Highest Detection : {best['Model']}"
        )

        logger.info(f"Reports Folder : {REPORT_DIR}")

        logger.info(f"Plots Folder : {PLOT_DIR}")

        logger.info("=" * 80)
        # =============================================================================
# Main
# =============================================================================

def main():

    evaluator = ModelEvaluation()

    evaluator.load_data()

    evaluator.dataset_summary()

    evaluator.model_comparison_report()

    evaluator.training_time_report()

    evaluator.evaluation_summary()

    evaluator.consensus_analysis()

    evaluator.top_suspicious()

    evaluator.feature_statistics()

    evaluator.detection_chart()

    evaluator.training_time_chart()

    evaluator.consensus_chart()

    evaluator.summary()


if __name__ == "__main__":

    main()
    