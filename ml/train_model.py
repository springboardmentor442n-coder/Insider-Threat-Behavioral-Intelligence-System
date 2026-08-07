"""
=========================================================
Model Training
AI Insider Threat Detection System
---------------------------------------------------------
Loads engineered employee features
Preprocesses the data
Splits into train/test sets
=========================================================
"""
from sklearn.ensemble import IsolationForest
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)
import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer

# -----------------------------------------------------
# Configuration
# -----------------------------------------------------

DATASET_PATH = "dataset/processed/employee_features.csv"

MODEL_FOLDER = "ml/models"

TARGET_COLUMN = "threat_label"

TEST_SIZE = 0.20

RANDOM_STATE = 42


# -----------------------------------------------------
# Load Dataset
# -----------------------------------------------------

def load_dataset():

    print("=" * 60)
    print("Loading Dataset")
    print("=" * 60)

    df = pd.read_csv(DATASET_PATH)

    print(f"Rows    : {len(df)}")
    print(f"Columns : {len(df.columns)}")

    return df


# -----------------------------------------------------
# Preprocess Dataset
# -----------------------------------------------------

def preprocess_dataset(df):

    print()
    print("=" * 60)
    print("Preprocessing Dataset")
    print("=" * 60)

    # Remove user ID (identifier only)
    if "user" in df.columns:
        df.drop(columns=["user"], inplace=True)

    # Remove constant columns
    constant_columns = [
        col for col in df.columns
        if df[col].nunique() <= 1
    ]

    if constant_columns:
        print("Dropped Constant Columns:")
        for col in constant_columns:
            print(f"  - {col}")

        df.drop(columns=constant_columns, inplace=True)

    # Separate X and y
    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN]

    label_encoders = {}

    # Encode categorical columns
    categorical_columns = X.select_dtypes(
        include=["object"]
    ).columns

    for column in categorical_columns:

        X[column] = X[column].fillna("Unknown")

        encoder = LabelEncoder()

        X[column] = encoder.fit_transform(X[column])

        label_encoders[column] = encoder

    # Fill numeric missing values
    numeric_columns = X.select_dtypes(
        exclude=["object"]
    ).columns

    imputer = SimpleImputer(strategy="median")

    X[numeric_columns] = imputer.fit_transform(
        X[numeric_columns]
    )

    print("Dataset preprocessing completed.")

    return X, y, label_encoders, imputer


# -----------------------------------------------------
# Train-Test Split
# -----------------------------------------------------

def split_dataset(X, y):

    print()
    print("=" * 60)
    print("Splitting Dataset")
    print("=" * 60)

    X_train, X_test, y_train, y_test = train_test_split(

        X,
        y,

        test_size=TEST_SIZE,

        random_state=RANDOM_STATE,

        stratify=y

    )

    print(f"Training Samples : {len(X_train)}")
    print(f"Testing Samples  : {len(X_test)}")

    return X_train, X_test, y_train, y_test

# -----------------------------------------------------
# Apply SMOTE
# -----------------------------------------------------

def apply_smote(X_train, y_train):

    print()
    print("=" * 60)
    print("Applying SMOTE")
    print("=" * 60)

    print("Before SMOTE")
    print(y_train.value_counts())

    smote = SMOTE(
        random_state=RANDOM_STATE
    )

    X_train_smote, y_train_smote = smote.fit_resample(
        X_train,
        y_train
    )

    print()
    print("After SMOTE")
    print(y_train_smote.value_counts())

    return X_train_smote, y_train_smote
# -----------------------------------------------------
# Main
# -----------------------------------------------------
# -----------------------------------------------------
# Train Random Forest
# -----------------------------------------------------

def train_random_forest(X_train, y_train):

    print()
    print("=" * 60)
    print("Training Random Forest")
    print("=" * 60)

    model = RandomForestClassifier(

        n_estimators=300,

        max_depth=15,

        random_state=RANDOM_STATE,

        n_jobs=-1

    )

    model.fit(X_train, y_train)

    return model

# -----------------------------------------------------
# Train XGBoost
# -----------------------------------------------------

def train_xgboost(X_train, y_train):

    print()
    print("=" * 60)
    print("Training XGBoost")
    print("=" * 60)

    model = XGBClassifier(

        n_estimators=300,

        max_depth=6,

        learning_rate=0.1,

        subsample=0.8,

        colsample_bytree=0.8,

        random_state=RANDOM_STATE,

        eval_metric="logloss"

    )

    model.fit(

        X_train,

        y_train

    )

    return model

# -----------------------------------------------------
# Train Isolation Forest
# -----------------------------------------------------

def train_isolation_forest(X_train):

    print()
    print("=" * 60)
    print("Training Isolation Forest")
    print("=" * 60)

    model = IsolationForest(

        n_estimators=300,

        contamination=0.07,

        random_state=RANDOM_STATE,

        n_jobs=-1

    )

    model.fit(X_train)

    return model
# -----------------------------------------------------
# Evaluate Isolation Forest
# -----------------------------------------------------

def evaluate_isolation_forest(model, X_test, y_test):

    predictions = model.predict(X_test)

    # Convert predictions
    predictions = [1 if x == -1 else 0 for x in predictions]

    print()
    print("=" * 60)
    print("ISOLATION FOREST PERFORMANCE")
    print("=" * 60)

    print(f"Accuracy  : {accuracy_score(y_test, predictions):.4f}")
    print(f"Precision : {precision_score(y_test, predictions):.4f}")
    print(f"Recall    : {recall_score(y_test, predictions):.4f}")
    print(f"F1 Score  : {f1_score(y_test, predictions):.4f}")

    print()

    print(confusion_matrix(y_test, predictions))

    print()

    print(classification_report(y_test, predictions))

    return {

        "Model": "Isolation Forest",

        "Accuracy": accuracy_score(y_test, predictions),

        "Precision": precision_score(y_test, predictions),

        "Recall": recall_score(y_test, predictions),

        "F1": f1_score(y_test, predictions),

        "ROC_AUC": None

    }
# -----------------------------------------------------
# Evaluate Model
# -----------------------------------------------------
# -----------------------------------------------------
# Evaluate Model
# -----------------------------------------------------

def evaluate_model(model, X_test, y_test):

    # Predictions
    predictions = model.predict(X_test)

    # Prediction Probabilities
    probabilities = model.predict_proba(X_test)[:, 1]

    # Metrics
    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions)
    recall = recall_score(y_test, predictions)
    f1 = f1_score(y_test, predictions)
    roc_auc = roc_auc_score(y_test, probabilities)

    # Display Results
    print()
    print("=" * 60)
    print("MODEL PERFORMANCE")
    print("=" * 60)

    print(f"Accuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1 Score  : {f1:.4f}")
    print(f"ROC AUC   : {roc_auc:.4f}")

    print("\nConfusion Matrix")
    print(confusion_matrix(y_test, predictions))

    print("\nClassification Report")
    print(classification_report(y_test, predictions))

    # Return Results
    return {
        "Model": model.__class__.__name__,
        "Accuracy": round(accuracy, 4),
        "Precision": round(precision, 4),
        "Recall": round(recall, 4),
        "F1 Score": round(f1, 4),
        "ROC AUC": round(roc_auc, 4)
    }
# -----------------------------------------------------
# Feature Importance
# -----------------------------------------------------

def feature_importance(model, feature_names):

    print()
    print("=" * 60)
    print("TOP 15 IMPORTANT FEATURES")
    print("=" * 60)

    importance = pd.DataFrame({

        "Feature": feature_names,
        "Importance": model.feature_importances_

    })

    importance = importance.sort_values(
        by="Importance",
        ascending=False
    )

    print(importance.head(15))

    joblib.dump(
        importance,
        os.path.join(
            MODEL_FOLDER,
            "feature_importance.pkl"
        )
    )

    importance.to_csv(
        os.path.join(
            MODEL_FOLDER,
            "feature_importance.csv"
        ),
        index=False
    )
# -----------------------------------------------------
# Save Model
# -----------------------------------------------------

# -----------------------------------------------------
# Save Model
# -----------------------------------------------------

def save_model(model, filename):

    path = os.path.join(

        MODEL_FOLDER,

        filename

    )

    joblib.dump(

        model,

        path

    )

    print(f"\nModel Saved : {path}")
# -----------------------------------------------------
# -----------------------------------------------------
# Evaluate Isolation Forest
# -----------------------------------------------------

def evaluate_isolation_forest(model, X_test, y_test):

    # Predict Anomalies
    predictions = model.predict(X_test)

    # Convert Predictions
    #  1  -> Normal (0)
    # -1 -> Insider (1)

    predictions = [1 if x == -1 else 0 for x in predictions]

    # Calculate Metrics
    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions, zero_division=0)
    recall = recall_score(y_test, predictions, zero_division=0)
    f1 = f1_score(y_test, predictions, zero_division=0)

    # Print Results
    print()
    print("=" * 60)
    print("ISOLATION FOREST PERFORMANCE")
    print("=" * 60)

    print(f"Accuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1 Score  : {f1:.4f}")

    print("\nConfusion Matrix")
    print(confusion_matrix(y_test, predictions))

    print("\nClassification Report")
    print(classification_report(y_test, predictions, zero_division=0))

    # Return Results
    return {
        "Model": "Isolation Forest",
        "Accuracy": round(accuracy, 4),
        "Precision": round(precision, 4),
        "Recall": round(recall, 4),
        "F1 Score": round(f1, 4),
        "ROC AUC": "N/A"
    }
# -----------------------------------------------------
# Compare Models
# -----------------------------------------------------
# -----------------------------------------------------
# Compare Models
# -----------------------------------------------------
# -----------------------------------------------------
# Compare Models
# -----------------------------------------------------

def compare_models(results):

    # Create DataFrame
    comparison_df = pd.DataFrame(results)

    # Display Comparison
    print()
    print("=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)
    print(comparison_df)

    # Save Comparison CSV
    comparison_path = os.path.join(
        MODEL_FOLDER,
        "model_comparison.csv"
    )

    comparison_df.to_csv(
        comparison_path,
        index=False
    )

    print(f"\nComparison saved to: {comparison_path}")

    # Select Best Model (Highest F1 Score)
    best_model = comparison_df.loc[
        comparison_df["F1 Score"].idxmax()
    ]

    print()
    print("=" * 60)
    print("BEST MODEL")
    print("=" * 60)
    print(best_model)

    # Determine Best Model File
    if best_model["Model"] == "RandomForestClassifier":
        best_model_file = "random_forest.pkl"

    elif best_model["Model"] == "XGBClassifier":
        best_model_file = "xgboost.pkl"

    else:
        best_model_file = "isolation_forest.pkl"

    # Save Best Model Name
    best_model_path = os.path.join(
        MODEL_FOLDER,
        "best_model.txt"
    )

    with open(best_model_path, "w") as file:
        file.write(best_model_file)

    print(f"\nBest Model Saved : {best_model_file}")

    return comparison_df
# -----------------------------------------------------
# Main
# -----------------------------------------------------

def main():

    print("\n" + "=" * 60)
    print("AI INSIDER THREAT DETECTION SYSTEM")
    print("MODEL TRAINING PIPELINE")
    print("=" * 60)

    # -------------------------------------------------
    # Create Models Directory
    # -------------------------------------------------

    os.makedirs(MODEL_FOLDER, exist_ok=True)

    # -------------------------------------------------
    # Load Dataset
    # -------------------------------------------------

    df = load_dataset()

    # -------------------------------------------------
    # Preprocess Dataset
    # -------------------------------------------------

    X, y, label_encoders, imputer = preprocess_dataset(df)

    # -------------------------------------------------
    # Train/Test Split
    # -------------------------------------------------

    X_train, X_test, y_train, y_test = split_dataset(
        X,
        y
    )

    # -------------------------------------------------
    # Apply SMOTE (Only for Supervised Models)
    # -------------------------------------------------

    X_train_smote, y_train_smote = apply_smote(
        X_train,
        y_train
    )

    # =================================================
    # RANDOM FOREST
    # =================================================

    rf_model = train_random_forest(
        X_train_smote,
        y_train_smote
    )

    print("\nRANDOM FOREST RESULTS")

    rf_results = evaluate_model(
        rf_model,
        X_test,
        y_test
    )

    feature_importance(
        rf_model,
        X.columns
    )

    save_model(
        rf_model,
        "random_forest.pkl"
    )

    # =================================================
    # XGBOOST
    # =================================================

    xgb_model = train_xgboost(
        X_train_smote,
        y_train_smote
    )

    print("\nXGBOOST RESULTS")

    xgb_results = evaluate_model(
        xgb_model,
        X_test,
        y_test
    )

    save_model(
        xgb_model,
        "xgboost.pkl"
    )

    # =================================================
    # ISOLATION FOREST
    # =================================================

    iso_model = train_isolation_forest(
        X_train
    )

    print("\nISOLATION FOREST RESULTS")

    iso_results = evaluate_isolation_forest(
        iso_model,
        X_test,
        y_test
    )

    save_model(
        iso_model,
        "isolation_forest.pkl"
    )

    # =================================================
    # MODEL COMPARISON
    # =================================================

    compare_models([
        rf_results,
        xgb_results,
        iso_results
    ])

    # -------------------------------------------------
    # Save Preprocessing Objects
    # -------------------------------------------------

    joblib.dump(
        label_encoders,
        os.path.join(
            MODEL_FOLDER,
            "label_encoders.pkl"
        )
    )

    joblib.dump(
        imputer,
        os.path.join(
            MODEL_FOLDER,
            "imputer.pkl"
        )
    )

    joblib.dump(
        list(X.columns),
        os.path.join(
            MODEL_FOLDER,
            "feature_columns.pkl"
        )
    )

    print("\n" + "=" * 60)
    print("MODEL TRAINING COMPLETED SUCCESSFULLY")
    print("=" * 60)


# -----------------------------------------------------
# Entry Point
# -----------------------------------------------------

if __name__ == "__main__":
    main()
