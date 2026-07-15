"""
===============================================================================
Module        : Multi-Model Training Pipeline
File          : 07_model_training.py
Project       : Insider Threat Behavioral Intelligence System

Description
-----------
Trains multiple anomaly detection models for insider threat detection.

Models
------
1. Isolation Forest
2. One-Class SVM
3. Local Outlier Factor
4. Elliptic Envelope
5. PCA Reconstruction
6. DBSCAN
7. KMeans Distance

Author
------
Nandan Kabra
===============================================================================
"""

from pathlib import Path
import logging
import warnings
import time

import duckdb
import joblib
import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler

from sklearn.ensemble import IsolationForest

from sklearn.svm import OneClassSVM

from sklearn.neighbors import LocalOutlierFactor

from sklearn.covariance import EllipticEnvelope

from sklearn.decomposition import PCA

from sklearn.cluster import DBSCAN

from sklearn.cluster import KMeans

warnings.filterwarnings("ignore")
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

FEATURE_FILE = (

    PROJECT_ROOT /

    "datasets" /

    "features" /

    "employee_features.parquet"

)

MODEL_DIR = PROJECT_ROOT / "models"

REPORT_DIR = PROJECT_ROOT / "reports"

PREDICTION_DIR = (

    PROJECT_ROOT /

    "datasets" /

    "predictions"

)

MODEL_DIR.mkdir(

    parents=True,

    exist_ok=True

)

REPORT_DIR.mkdir(

    parents=True,

    exist_ok=True

)

PREDICTION_DIR.mkdir(

    parents=True,

    exist_ok=True

)

SCALER_FILE = MODEL_DIR / "scaler.pkl"
# =============================================================================
# Model Trainer
# =============================================================================

class ModelTrainer:

    def __init__(self):

        self.conn = duckdb.connect()

        self.models = {}

        self.training_times = {}

        self.predictions = {}

        self.feature_columns = []

        logger.info("=" * 80)
        logger.info("MULTI MODEL TRAINING PIPELINE")
        logger.info("=" * 80)
            # =========================================================================
    # Load Feature Dataset
    # =========================================================================

    def load_dataset(self):

        logger.info("=" * 80)
        logger.info("LOADING FEATURE DATASET")
        logger.info("=" * 80)

        self.df = self.conn.execute(f"""
            SELECT *
            FROM read_parquet('{FEATURE_FILE.as_posix()}')
        """).fetchdf()

        logger.info(f"Employees Loaded : {len(self.df):,}")
        logger.info(f"Columns Loaded   : {len(self.df.columns)}")

        logger.info("=" * 80)
            # =========================================================================
    # Prepare Features
    # =========================================================================

    def prepare_features(self):

        logger.info("Preparing Features...")

        ignore_columns = [

            "user",

            "first_activity",

            "last_activity"

        ]

        self.feature_columns = [

            column

            for column in self.df.columns

            if column not in ignore_columns

        ]

        self.features = self.df[self.feature_columns].copy()

        logger.info(f"Features Selected : {len(self.feature_columns)}")
        logger.info("Handling Missing Values...")

        self.features = self.features.fillna(0)
        logger.info("Scaling Features...")

        self.scaler = StandardScaler()

        self.X = self.scaler.fit_transform(

            self.features

        )

        joblib.dump(

            self.scaler,

            SCALER_FILE

        )

        logger.info(f"Scaler Saved : {SCALER_FILE}")

        logger.info("=" * 80)
            # =========================================================================
    # Dataset Statistics
    # =========================================================================

    def dataset_statistics(self):

        logger.info("=" * 80)
        logger.info("DATASET STATISTICS")
        logger.info("=" * 80)

        logger.info(f"Rows       : {self.features.shape[0]:,}")

        logger.info(f"Columns    : {self.features.shape[1]:,}")

        logger.info(

            f"Memory(MB) : {self.features.memory_usage().sum()/1024**2:.2f}"

        )

        logger.info("=" * 80)
            # =========================================================================
    # Save Model
    # =========================================================================

    def save_model(self, model, filename):

        path = MODEL_DIR / filename

        joblib.dump(

            model,

            path

        )

        logger.info(f"Saved : {path}")


    # =========================================================================
    # Timer
    # =========================================================================

    def start_timer(self):

        return time.time()


    def stop_timer(self, start):

        return round(

            time.time() - start,

            2

        )
        # =========================================================================
    # Isolation Forest
    # =========================================================================

    def train_isolation_forest(self):

        logger.info("=" * 80)
        logger.info("TRAINING ISOLATION FOREST")
        logger.info("=" * 80)

        start = self.start_timer()

        model = IsolationForest(
            n_estimators=300,
            contamination=0.03,
            random_state=42,
            n_jobs=-1
        )

        model.fit(self.X)

        self.models["Isolation Forest"] = model

        self.training_times["Isolation Forest"] = self.stop_timer(start)

        self.save_model(
            model,
            "isolation_forest.pkl"
        )

        logger.info(
            f"Training Time : {self.training_times['Isolation Forest']} sec"
        )

        logger.info("Generating Predictions...")

        scores = -model.score_samples(self.X)

        predictions = np.where(
            model.predict(self.X) == -1,
            "Suspicious",
            "Normal"
        )

        self.predictions["Isolation Forest"] = pd.DataFrame({

            "user": self.df["user"],

            "risk_score": scores,

            "prediction": predictions

        })

        logger.info(
            f"Suspicious Employees : {(predictions=='Suspicious').sum()}"
        )

        logger.info("=" * 80)
            # =========================================================================
    # Export Individual Prediction
    # =========================================================================

    def export_prediction(self, model_name):

        filename = (

            model_name

            .replace(" ", "_")

            .lower()

            + ".parquet"

        )

        path = PREDICTION_DIR / filename

        self.predictions[model_name].to_parquet(

            path,

            index=False

        )

        logger.info(f"Prediction Saved : {path}")
            # =========================================================================
    # One-Class SVM
    # =========================================================================

    def train_oneclass_svm(self):

        logger.info("=" * 80)
        logger.info("TRAINING ONE-CLASS SVM")
        logger.info("=" * 80)

        start = self.start_timer()

        model = OneClassSVM(
            kernel="rbf",
            gamma="scale",
            nu=0.03
        )

        model.fit(self.X)

        self.models["One-Class SVM"] = model

        self.training_times["One-Class SVM"] = self.stop_timer(start)

        self.save_model(
            model,
            "one_class_svm.pkl"
        )

        scores = -model.score_samples(self.X)

        prediction = np.where(
            model.predict(self.X) == -1,
            "Suspicious",
            "Normal"
        )

        self.predictions["One-Class SVM"] = pd.DataFrame({

            "user": self.df["user"],

            "risk_score": scores,

            "prediction": prediction

        })

        self.export_prediction("One-Class SVM")

        logger.info(
            f"Training Time : {self.training_times['One-Class SVM']} sec"
        )

        logger.info(
            f"Suspicious Employees : {(prediction=='Suspicious').sum()}"
        )

        logger.info("=" * 80)
            # =========================================================================
    # Local Outlier Factor
    # =========================================================================

    def train_lof(self):

        logger.info("=" * 80)
        logger.info("TRAINING LOCAL OUTLIER FACTOR")
        logger.info("=" * 80)

        start = self.start_timer()

        model = LocalOutlierFactor(
            n_neighbors=20,
            contamination=0.03,
            novelty=True
        )

        model.fit(self.X)

        self.models["LOF"] = model

        self.training_times["LOF"] = self.stop_timer(start)

        self.save_model(
            model,
            "lof.pkl"
        )

        scores = -model.score_samples(self.X)

        prediction = np.where(
            model.predict(self.X) == -1,
            "Suspicious",
            "Normal"
        )

        self.predictions["LOF"] = pd.DataFrame({

            "user": self.df["user"],

            "risk_score": scores,

            "prediction": prediction

        })

        self.export_prediction("LOF")

        logger.info(
            f"Training Time : {self.training_times['LOF']} sec"
        )

        logger.info(
            f"Suspicious Employees : {(prediction=='Suspicious').sum()}"
        )

        logger.info("=" * 80)
            # =========================================================================
    # Elliptic Envelope
    # =========================================================================

    def train_elliptic_envelope(self):

        logger.info("=" * 80)
        logger.info("TRAINING ELLIPTIC ENVELOPE")
        logger.info("=" * 80)

        start = self.start_timer()

        model = EllipticEnvelope(
            contamination=0.03,
            random_state=42
        )

        model.fit(self.X)

        self.models["Elliptic Envelope"] = model

        self.training_times["Elliptic Envelope"] = self.stop_timer(start)

        self.save_model(
            model,
            "elliptic_envelope.pkl"
        )

        scores = -model.score_samples(self.X)

        prediction = np.where(
            model.predict(self.X) == -1,
            "Suspicious",
            "Normal"
        )

        self.predictions["Elliptic Envelope"] = pd.DataFrame({

            "user": self.df["user"],

            "risk_score": scores,

            "prediction": prediction

        })

        self.export_prediction("Elliptic Envelope")

        logger.info(
            f"Training Time : {self.training_times['Elliptic Envelope']} sec"
        )

        logger.info(
            f"Suspicious Employees : {(prediction=='Suspicious').sum()}"
        )

        logger.info("=" * 80)
            # =========================================================================
    # PCA Reconstruction
    # =========================================================================

    def train_pca(self):

        logger.info("=" * 80)
        logger.info("TRAINING PCA RECONSTRUCTION")
        logger.info("=" * 80)

        start = self.start_timer()

        model = PCA(
            n_components=0.95,
            random_state=42
        )

        model.fit(self.X)

        self.models["PCA"] = model

        self.training_times["PCA"] = self.stop_timer(start)

        self.save_model(
            model,
            "pca.pkl"
        )

        transformed = model.transform(self.X)

        reconstructed = model.inverse_transform(transformed)

        scores = np.mean(
            np.square(self.X - reconstructed),
            axis=1
        )

        threshold = np.percentile(scores, 97)

        prediction = np.where(
            scores >= threshold,
            "Suspicious",
            "Normal"
        )

        self.predictions["PCA"] = pd.DataFrame({

            "user": self.df["user"],

            "risk_score": scores,

            "prediction": prediction

        })

        self.export_prediction("PCA")

        logger.info(
            f"Training Time : {self.training_times['PCA']} sec"
        )

        logger.info(
            f"Suspicious Employees : {(prediction=='Suspicious').sum()}"
        )

        logger.info("=" * 80)
            # =========================================================================
    # DBSCAN
    # =========================================================================

    def train_dbscan(self):

        logger.info("=" * 80)
        logger.info("TRAINING DBSCAN")
        logger.info("=" * 80)

        start = self.start_timer()

        model = DBSCAN(
            eps=3.5,
            min_samples=10
        )

        labels = model.fit_predict(self.X)

        self.models["DBSCAN"] = model

        self.training_times["DBSCAN"] = self.stop_timer(start)

        self.save_model(
            model,
            "dbscan.pkl"
        )

        scores = np.where(labels == -1, 1.0, 0.0)

        prediction = np.where(
            labels == -1,
            "Suspicious",
            "Normal"
        )

        self.predictions["DBSCAN"] = pd.DataFrame({

            "user": self.df["user"],

            "risk_score": scores,

            "prediction": prediction

        })

        self.export_prediction("DBSCAN")

        logger.info(
            f"Training Time : {self.training_times['DBSCAN']} sec"
        )

        logger.info(
            f"Suspicious Employees : {(prediction=='Suspicious').sum()}"
        )

        logger.info("=" * 80)
            # =========================================================================
    # KMeans Distance Anomaly Detection
    # =========================================================================

    def train_kmeans(self):

        logger.info("=" * 80)
        logger.info("TRAINING KMEANS")
        logger.info("=" * 80)

        start = self.start_timer()

        model = KMeans(
            n_clusters=5,
            random_state=42,
            n_init=20
        )

        model.fit(self.X)

        self.models["KMeans"] = model

        self.training_times["KMeans"] = self.stop_timer(start)

        self.save_model(
            model,
            "kmeans.pkl"
        )

        distances = np.min(
            model.transform(self.X),
            axis=1
        )

        threshold = np.percentile(
            distances,
            97
        )

        prediction = np.where(
            distances >= threshold,
            "Suspicious",
            "Normal"
        )

        self.predictions["KMeans"] = pd.DataFrame({

            "user": self.df["user"],

            "risk_score": distances,

            "prediction": prediction

        })

        self.export_prediction("KMeans")

        logger.info(
            f"Training Time : {self.training_times['KMeans']} sec"
        )

        logger.info(
            f"Suspicious Employees : {(prediction=='Suspicious').sum()}"
        )

        logger.info("=" * 80)
            # =========================================================================
    # Compare Models
    # =========================================================================

    def compare_models(self):

        logger.info("=" * 80)
        logger.info("MODEL COMPARISON")
        logger.info("=" * 80)

        comparison = []

        for model_name, prediction_df in self.predictions.items():

            comparison.append({

                "Model": model_name,

                "Suspicious Employees":
                    (prediction_df["prediction"] == "Suspicious").sum(),

                "Average Risk Score":
                    prediction_df["risk_score"].mean(),

                "Maximum Risk Score":
                    prediction_df["risk_score"].max(),

                "Minimum Risk Score":
                    prediction_df["risk_score"].min(),

                "Training Time (sec)":
                    self.training_times[model_name]

            })

        self.comparison = pd.DataFrame(comparison)

        print()
        print(self.comparison)
        print()
            # =========================================================================
    # Export Reports
    # =========================================================================

    def export_reports(self):

        logger.info("=" * 80)
        logger.info("EXPORTING REPORTS")
        logger.info("=" * 80)

        comparison_file = REPORT_DIR / "model_comparison.csv"

        training_file = REPORT_DIR / "training_times.csv"

        prediction_file = (
            PREDICTION_DIR /
            "all_model_predictions.parquet"
        )

        self.comparison.to_csv(
            comparison_file,
            index=False
        )

        pd.DataFrame({

            "Model":
                list(self.training_times.keys()),

            "Training Time":
                list(self.training_times.values())

        }).to_csv(

            training_file,

            index=False

        )

        merged = self.df[["user"]].copy()

        for model_name in self.predictions:

            merged[f"{model_name}_Prediction"] = \
                self.predictions[model_name]["prediction"]

            merged[f"{model_name}_Score"] = \
                self.predictions[model_name]["risk_score"]

        merged.to_parquet(
            prediction_file,
            index=False
        )

        logger.info(f"Saved : {comparison_file}")
        logger.info(f"Saved : {training_file}")
        logger.info(f"Saved : {prediction_file}")
            # =========================================================================
    # Summary
    # =========================================================================

    def summary(self):

        logger.info("=" * 80)
        logger.info("FINAL SUMMARY")
        logger.info("=" * 80)

        fastest = min(
            self.training_times,
            key=self.training_times.get
        )

        slowest = max(
            self.training_times,
            key=self.training_times.get
        )

        best = self.comparison.loc[
            self.comparison[
                "Suspicious Employees"
            ].idxmax()
        ]

        logger.info(
            f"Employees : {len(self.df):,}"
        )

        logger.info(
            f"Features : {len(self.feature_columns)}"
        )

        logger.info(
            f"Models Trained : {len(self.models)}"
        )

        logger.info(
            f"Fastest Model : {fastest}"
        )

        logger.info(
            f"Slowest Model : {slowest}"
        )

        logger.info(
            f"Highest Detection : {best['Model']}"
        )

        logger.info("=" * 80)

        logger.info(
            "MULTI-MODEL TRAINING COMPLETED SUCCESSFULLY"
        )

        logger.info("=" * 80)
        # =============================================================================
# Main
# =============================================================================

def main():

    trainer = ModelTrainer()

    trainer.load_dataset()

    trainer.prepare_features()

    trainer.dataset_statistics()

    trainer.train_isolation_forest()

    trainer.train_oneclass_svm()

    trainer.train_lof()

    trainer.train_elliptic_envelope()

    trainer.train_pca()

    trainer.train_dbscan()

    trainer.train_kmeans()

    trainer.compare_models()

    trainer.export_reports()

    trainer.summary()


if __name__ == "__main__":

    main()
