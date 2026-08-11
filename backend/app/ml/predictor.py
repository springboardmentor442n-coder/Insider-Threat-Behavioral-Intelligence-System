import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from app.core.config import settings

class MLPredictorService:
    """
    Read-only ML Prediction Service wrapper for gb.pkl, scaler.pkl, feature_columns.pkl.
    Loaded ONCE at application startup.
    Executes real ML predictions using trained Gradient Boosting Classifier and MinMaxScaler.
    """
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_columns = []
        self.is_loaded = False
        self.model_info = {
            "name": "Gradient Boosting Classifier",
            "n_estimators": 100,
            "learning_rate": 0.1,
            "max_depth": 3,
            "random_state": 42
        }
        self.load_artifacts()

    def load_artifacts(self):
        try:
            if os.path.exists(settings.FEATURE_COLUMNS_PATH):
                loaded_cols = joblib.load(settings.FEATURE_COLUMNS_PATH)
                if isinstance(loaded_cols, (list, tuple, np.ndarray)):
                    self.feature_columns = list(loaded_cols)
            
            if os.path.exists(settings.GB_MODEL_PATH):
                self.model = joblib.load(settings.GB_MODEL_PATH)
            
            if os.path.exists(settings.SCALER_PATH):
                self.scaler = joblib.load(settings.SCALER_PATH)

            if self.model is not None and self.scaler is not None and len(self.feature_columns) > 0:
                self.is_loaded = True
                print(f"ML Predictor initialized: Loaded 19 feature schema, Scaler, and GB Model from disk.")
            else:
                print("ML Predictor: Error - Model, Scaler, or Feature Columns file missing.")
                self.is_loaded = False
        except Exception as e:
            print(f"ML Predictor Error loading artifacts: {e}")
            self.is_loaded = False

    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Validate incoming DataFrame against expected 19 feature columns schema.
        Returns (missing_columns, row_errors).
        """
        if not self.is_loaded:
            raise ValueError("ML model artifacts are not loaded. Cannot validate dataset.")

        missing_cols = [col for col in self.feature_columns if col not in df.columns]
        row_errors = []

        if missing_cols:
            return missing_cols, row_errors

        # Check numeric types and validity per row
        for idx, row in df.iterrows():
            row_num = idx + 1
            for col in self.feature_columns:
                val = row[col]
                if pd.isna(val):
                    row_errors.append({"row": row_num, "column": col, "error": "Value is missing/null"})
                else:
                    try:
                        float_val = float(val)
                        if float_val < 0:
                            row_errors.append({"row": row_num, "column": col, "error": f"Negative value ({val}) not allowed"})
                    except (ValueError, TypeError):
                        row_errors.append({"row": row_num, "column": col, "error": f"Invalid numeric format ({val})"})

        return missing_cols, row_errors

    def predict_single(self, feature_dict: dict) -> dict:
        """
        Run inference over 19 behavioral features for a single record.
        """
        if not self.is_loaded or self.model is None or self.scaler is None:
            raise ValueError("ML model artifacts (gb.pkl, scaler.pkl) are not loaded. Real model prediction unavailable.")

        # Extract features strictly in order specified by feature_columns.pkl
        input_vector = []
        for col in self.feature_columns:
            if col not in feature_dict or pd.isna(feature_dict[col]):
                raise ValueError(f"Missing required feature column: {col}")
            try:
                val = float(feature_dict[col])
                input_vector.append(val)
            except Exception:
                raise ValueError(f"Invalid numeric value for feature {col}: {feature_dict[col]}")

        X = np.array([input_vector])
        X_scaled = self.scaler.transform(X)
        pred = int(self.model.predict(X_scaled)[0])
        prob = float(self.model.predict_proba(X_scaled)[0][1])

        ml_risk_score = round(prob * 100.0, 2)

        # Behavioral risk score based on notebook 6-rule formula
        rule_off_hours_logons = 1 if float(feature_dict.get("off_hours_logons", 0)) > 2 else 0
        rule_device_connects = 1 if float(feature_dict.get("device_connects", 0)) > 5 else 0
        rule_sensitive_file_count = 1 if float(feature_dict.get("sensitive_file_count", 0)) > 5 else 0
        rule_attachment_count = 1 if float(feature_dict.get("attachment_count", 0)) > 10 else 0
        rule_external_email_count = 1 if float(feature_dict.get("external_email_count", 0)) > 10 else 0
        rule_off_hours_http = 1 if float(feature_dict.get("off_hours_http", 0)) > 10 else 0

        risk_score = (
            rule_off_hours_logons +
            rule_device_connects +
            rule_sensitive_file_count +
            rule_attachment_count +
            rule_external_email_count +
            rule_off_hours_http
        )
        behavioral_risk_score = round((risk_score / 6.0) * 100.0, 2)

        # Final risk score formula: 0.7 * ml + 0.3 * behavioral
        final_risk_score = round(min(100.0, max(0.0, (0.7 * ml_risk_score) + (0.3 * behavioral_risk_score))), 2)

        if final_risk_score >= 80:
            severity = "Critical"
        elif final_risk_score >= 60:
            severity = "High"
        elif final_risk_score >= 40:
            severity = "Medium"
        else:
            severity = "Low"

        return {
            "prediction": pred,
            "prediction_probability": round(prob, 4),
            "ml_risk_score": ml_risk_score,
            "risk_score": risk_score,
            "behavioral_risk_score": behavioral_risk_score,
            "final_risk_score": final_risk_score,
            "severity": severity,
            "features_used": self.feature_columns
        }

    def predict(self, feature_dict: dict) -> dict:
        return self.predict_single(feature_dict)

predictor_service = MLPredictorService()
