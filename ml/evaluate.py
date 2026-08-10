"""
=========================================================
Model Evaluation
AI Insider Threat Detection System
---------------------------------------------------------
Uses the SAME preprocessing saved during training.

Evaluates:
    Random Forest
    XGBoost
    Isolation Forest

Generates:
    - Test metrics
    - Confusion matrices
    - ROC curves
    - Precision-Recall curves
    - Cross-validation
    - Overfitting check
    - Feature importance
=========================================================
"""

import os
import joblib
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    roc_curve,
    precision_recall_curve,
    average_precision_score
)

from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier


# =========================================================
# CONFIGURATION
# =========================================================

DATASET_PATH = "dataset/processed/employee_features.csv"

MODEL_FOLDER = "ml/models"

EVALUATION_FOLDER = os.path.join(
    MODEL_FOLDER,
    "evaluation"
)

TARGET_COLUMN = "threat_label"

RANDOM_STATE = 42


# =========================================================
# LOAD DATASET
# =========================================================

def load_dataset():

    print()
    print("=" * 60)
    print("LOADING DATASET")
    print("=" * 60)

    df = pd.read_csv(DATASET_PATH)

    print(f"Rows    : {len(df)}")
    print(f"Columns : {len(df.columns)}")

    return df


# =========================================================
# PREPARE RAW DATA
# =========================================================

def prepare_raw_data(df):

    print()
    print("=" * 60)
    print("PREPARING DATASET")
    print("=" * 60)

    df = df.copy()

    # -----------------------------------------------------
    # Remove identifier
    # -----------------------------------------------------

    if "user" in df.columns:

        df.drop(
            columns=["user"],
            inplace=True
        )

        print("Removed identifier column: user")

    # -----------------------------------------------------
    # Remove constant columns
    # -----------------------------------------------------

    constant_columns = [

        column

        for column in df.columns

        if column != TARGET_COLUMN
        and df[column].nunique(dropna=False) <= 1

    ]

    if constant_columns:

        print()
        print("Dropped Constant Columns:")

        for column in constant_columns:

            print(f"  - {column}")

        df.drop(
            columns=constant_columns,
            inplace=True
        )

    X = df.drop(
        columns=[TARGET_COLUMN]
    )

    y = df[TARGET_COLUMN]

    print()
    print(
        f"Features before preprocessing : "
        f"{X.shape[1]}"
    )

    print(
        f"Target distribution:"
    )

    print(
        y.value_counts()
    )

    return X, y


# =========================================================
# LOAD PREPROCESSOR
# =========================================================

def load_preprocessor():

    path = os.path.join(
        MODEL_FOLDER,
        "preprocessor.pkl"
    )

    if not os.path.exists(path):

        raise FileNotFoundError(
            "preprocessor.pkl not found. "
            "Run ml/train_model.py first."
        )

    preprocessor = joblib.load(
        path
    )

    print()
    print(
        f"Preprocessor loaded : {path}"
    )

    return preprocessor


# =========================================================
# TRANSFORM DATA
# =========================================================

def transform_data(
    preprocessor,
    X
):

    print()
    print("=" * 60)
    print("APPLYING SAVED PREPROCESSOR")
    print("=" * 60)

    # IMPORTANT:
    #
    # We DO NOT fit here.
    #
    # The preprocessor was already fitted during training.
    #
    # This guarantees that evaluation uses exactly the same
    # transformation as the trained model.

    X_processed = preprocessor.transform(
        X
    )

    feature_names = (
        preprocessor
        .get_feature_names_out()
    )

    print(
        f"Features after preprocessing : "
        f"{X_processed.shape[1]}"
    )

    return (
        X_processed,
        feature_names
    )


# =========================================================
# LOAD TRAINED MODELS
# =========================================================

def load_models():

    print()
    print("=" * 60)
    print("LOADING TRAINED MODELS")
    print("=" * 60)

    rf_path = os.path.join(
        MODEL_FOLDER,
        "random_forest.pkl"
    )

    xgb_path = os.path.join(
        MODEL_FOLDER,
        "xgboost.pkl"
    )

    iso_path = os.path.join(
        MODEL_FOLDER,
        "isolation_forest.pkl"
    )

    random_forest = joblib.load(
        rf_path
    )

    xgboost_model = joblib.load(
        xgb_path
    )

    isolation_forest = joblib.load(
        iso_path
    )

    print(
        "Random Forest loaded"
    )

    print(
        "XGBoost loaded"
    )

    print(
        "Isolation Forest loaded"
    )

    return (
        random_forest,
        xgboost_model,
        isolation_forest
    )


# =========================================================
# TEST SET EVALUATION
# =========================================================

def evaluate_test_set(
    model,
    X_test,
    y_test,
    model_name
):

    print()
    print("=" * 60)
    print(f"TEST SET EVALUATION: {model_name}")
    print("=" * 60)

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        y_test,
        probabilities
    )

    print()
    print(
        f"Accuracy  : {accuracy:.4f}"
    )

    print(
        f"Precision : {precision:.4f}"
    )

    print(
        f"Recall    : {recall:.4f}"
    )

    print(
        f"F1 Score  : {f1:.4f}"
    )

    print(
        f"ROC AUC   : {roc_auc:.4f}"
    )

    cm = confusion_matrix(
        y_test,
        predictions
    )

    print()
    print("Confusion Matrix")

    print(cm)

    print()
    print("Classification Report")

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    return {

        "Model": model_name,

        "Accuracy": accuracy,

        "Precision": precision,

        "Recall": recall,

        "F1 Score": f1,

        "ROC AUC": roc_auc,

        "Predictions": predictions,

        "Probabilities": probabilities,

        "Confusion Matrix": cm

    }


# =========================================================
# CROSS VALIDATION
# =========================================================

def cross_validate_model(
    model,
    X,
    y,
    model_name
):

    print()
    print("=" * 60)
    print(f"5-FOLD CROSS VALIDATION: {model_name}")
    print("=" * 60)

    cv = StratifiedKFold(

        n_splits=5,

        shuffle=True,

        random_state=RANDOM_STATE

    )

    scoring = {

        "accuracy": "accuracy",

        "precision": "precision",

        "recall": "recall",

        "f1": "f1",

        "roc_auc": "roc_auc"

    }

    scores = cross_validate(

        model,

        X,

        y,

        cv=cv,

        scoring=scoring,

        n_jobs=-1

    )

    results = {

        "Accuracy Mean":
            scores["test_accuracy"].mean(),

        "Accuracy Std":
            scores["test_accuracy"].std(),

        "Precision Mean":
            scores["test_precision"].mean(),

        "Precision Std":
            scores["test_precision"].std(),

        "Recall Mean":
            scores["test_recall"].mean(),

        "Recall Std":
            scores["test_recall"].std(),

        "F1 Mean":
            scores["test_f1"].mean(),

        "F1 Std":
            scores["test_f1"].std(),

        "ROC AUC Mean":
            scores["test_roc_auc"].mean(),

        "ROC AUC Std":
            scores["test_roc_auc"].std()

    }

    print()

    print(
        f"Accuracy   : "
        f"{results['Accuracy Mean']:.4f} "
        f"+/- "
        f"{results['Accuracy Std']:.4f}"
    )

    print(
        f"Precision  : "
        f"{results['Precision Mean']:.4f} "
        f"+/- "
        f"{results['Precision Std']:.4f}"
    )

    print(
        f"Recall     : "
        f"{results['Recall Mean']:.4f} "
        f"+/- "
        f"{results['Recall Std']:.4f}"
    )

    print(
        f"F1         : "
        f"{results['F1 Mean']:.4f} "
        f"+/- "
        f"{results['F1 Std']:.4f}"
    )

    print(
        f"ROC AUC    : "
        f"{results['ROC AUC Mean']:.4f} "
        f"+/- "
        f"{results['ROC AUC Std']:.4f}"
    )

    return results


# =========================================================
# OVERFITTING CHECK
# =========================================================

def overfitting_check(
    model,
    X_train,
    y_train,
    X_test,
    y_test
):

    print()
    print("=" * 60)
    print("OVERFITTING CHECK")
    print("=" * 60)

    train_predictions = model.predict(
        X_train
    )

    test_predictions = model.predict(
        X_test
    )

    train_accuracy = accuracy_score(
        y_train,
        train_predictions
    )

    test_accuracy = accuracy_score(
        y_test,
        test_predictions
    )

    gap = (
        train_accuracy
        -
        test_accuracy
    )

    print(
        f"Training Accuracy : "
        f"{train_accuracy:.4f}"
    )

    print(
        f"Testing Accuracy  : "
        f"{test_accuracy:.4f}"
    )

    print(
        f"Accuracy Gap      : "
        f"{gap:.4f}"
    )

    if gap <= 0.05:

        print(
            "Result             : "
            "No substantial train-test "
            "accuracy gap observed"
        )

    elif gap <= 0.10:

        print(
            "Result             : "
            "Moderate possible overfitting"
        )

    else:

        print(
            "Result             : "
            "Strong evidence of overfitting"
        )

    return {

        "Training Accuracy":
            train_accuracy,

        "Testing Accuracy":
            test_accuracy,

        "Accuracy Gap":
            gap

    }


# =========================================================
# CONFUSION MATRIX PLOT
# =========================================================

def generate_confusion_matrix(
    cm,
    model_name
):

    print()
    print(
        "Generating Confusion Matrix..."
    )

    plt.figure(
        figsize=(6, 5)
    )

    plt.imshow(
        cm,
        interpolation="nearest"
    )

    plt.title(
        f"{model_name} Confusion Matrix"
    )

    plt.colorbar()

    plt.xticks(
        [0, 1],
        ["Normal", "Threat"]
    )

    plt.yticks(
        [0, 1],
        ["Normal", "Threat"]
    )

    plt.xlabel(
        "Predicted"
    )

    plt.ylabel(
        "Actual"
    )

    for i in range(2):

        for j in range(2):

            plt.text(
                j,
                i,
                str(cm[i, j]),
                ha="center",
                va="center"
            )

    plt.tight_layout()

    path = os.path.join(
        EVALUATION_FOLDER,
        "confusion_matrix.png"
    )

    plt.savefig(
        path,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Saved : {path}"
    )


# =========================================================
# ROC CURVE
# =========================================================

def generate_roc_curve(
    y_test,
    probabilities
):

    print()
    print(
        "Generating ROC Curve..."
    )

    fpr, tpr, _ = roc_curve(
        y_test,
        probabilities
    )

    auc = roc_auc_score(
        y_test,
        probabilities
    )

    plt.figure(
        figsize=(7, 6)
    )

    plt.plot(
        fpr,
        tpr,
        label=f"AUC = {auc:.4f}"
    )

    plt.plot(
        [0, 1],
        [0, 1],
        linestyle="--"
    )

    plt.xlabel(
        "False Positive Rate"
    )

    plt.ylabel(
        "True Positive Rate"
    )

    plt.title(
        "ROC Curve - Random Forest"
    )

    plt.legend(
        loc="lower right"
    )

    plt.tight_layout()

    path = os.path.join(
        EVALUATION_FOLDER,
        "roc_curve.png"
    )

    plt.savefig(
        path,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Saved : {path}"
    )


# =========================================================
# PRECISION-RECALL CURVE
# =========================================================

def generate_precision_recall_curve(
    y_test,
    probabilities
):

    print()
    print(
        "Generating Precision-Recall Curve..."
    )

    precision, recall, _ = (
        precision_recall_curve(
            y_test,
            probabilities
        )
    )

    average_precision = (
        average_precision_score(
            y_test,
            probabilities
        )
    )

    plt.figure(
        figsize=(7, 6)
    )

    plt.plot(
        recall,
        precision,
        label=(
            f"Average Precision = "
            f"{average_precision:.4f}"
        )
    )

    plt.xlabel(
        "Recall"
    )

    plt.ylabel(
        "Precision"
    )

    plt.title(
        "Precision-Recall Curve - Random Forest"
    )

    plt.legend(
        loc="lower left"
    )

    plt.tight_layout()

    path = os.path.join(
        EVALUATION_FOLDER,
        "precision_recall_curve.png"
    )

    plt.savefig(
        path,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Saved : {path}"
    )


# =========================================================
# FEATURE IMPORTANCE
# =========================================================

def generate_feature_importance(
    model,
    feature_names
):

    print()
    print(
        "Generating Feature Importance..."
    )

    importance_df = pd.DataFrame({

        "Feature":
            feature_names,

        "Importance":
            model.feature_importances_

    })

    importance_df.sort_values(

        by="Importance",

        ascending=False,

        inplace=True

    )

    print()
    print(
        importance_df.head(15).to_string(
            index=False
        )
    )

    path = os.path.join(
        EVALUATION_FOLDER,
        "feature_importance.csv"
    )

    importance_df.to_csv(
        path,
        index=False
    )

    # -----------------------------------------------------
    # Plot top 15
    # -----------------------------------------------------

    top_features = (
        importance_df
        .head(15)
        .sort_values(
            "Importance"
        )
    )

    plt.figure(
        figsize=(9, 7)
    )

    plt.barh(

        top_features["Feature"],

        top_features["Importance"]

    )

    plt.xlabel(
        "Importance"
    )

    plt.ylabel(
        "Feature"
    )

    plt.title(
        "Top 15 Random Forest Features"
    )

    plt.tight_layout()

    plot_path = os.path.join(
        EVALUATION_FOLDER,
        "feature_importance.png"
    )

    plt.savefig(
        plot_path,
        dpi=200,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Saved : {path}"
    )

    print(
        f"Saved : {plot_path}"
    )


# =========================================================
# SAVE EVALUATION REPORT
# =========================================================

def save_evaluation_report(
    test_results,
    cv_results,
    overfit_results
):

    report = {

        "Test Accuracy":
            test_results["Accuracy"],

        "Test Precision":
            test_results["Precision"],

        "Test Recall":
            test_results["Recall"],

        "Test F1":
            test_results["F1 Score"],

        "Test ROC AUC":
            test_results["ROC AUC"],

        "CV Accuracy Mean":
            cv_results["Accuracy Mean"],

        "CV Accuracy Std":
            cv_results["Accuracy Std"],

        "CV Precision Mean":
            cv_results["Precision Mean"],

        "CV Precision Std":
            cv_results["Precision Std"],

        "CV Recall Mean":
            cv_results["Recall Mean"],

        "CV Recall Std":
            cv_results["Recall Std"],

        "CV F1 Mean":
            cv_results["F1 Mean"],

        "CV F1 Std":
            cv_results["F1 Std"],

        "CV ROC AUC Mean":
            cv_results["ROC AUC Mean"],

        "CV ROC AUC Std":
            cv_results["ROC AUC Std"],

        "Training Accuracy":
            overfit_results["Training Accuracy"],

        "Testing Accuracy":
            overfit_results["Testing Accuracy"],

        "Accuracy Gap":
            overfit_results["Accuracy Gap"]

    }

    report_df = pd.DataFrame(
        [report]
    )

    path = os.path.join(
        EVALUATION_FOLDER,
        "evaluation_report.csv"
    )

    report_df.to_csv(
        path,
        index=False
    )

    print()
    print(
        f"Evaluation report saved : {path}"
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 60)
    print("AI INSIDER THREAT DETECTION SYSTEM")
    print("MODEL EVALUATION PIPELINE")
    print("=" * 60)

    # -----------------------------------------------------
    # Create evaluation directory
    # -----------------------------------------------------

    os.makedirs(
        EVALUATION_FOLDER,
        exist_ok=True
    )

    # -----------------------------------------------------
    # 1. Load dataset
    # -----------------------------------------------------

    df = load_dataset()

    # -----------------------------------------------------
    # 2. Prepare raw features
    # -----------------------------------------------------

    X, y = prepare_raw_data(
        df
    )

    # -----------------------------------------------------
    # 3. Load saved preprocessor
    # -----------------------------------------------------

    preprocessor = load_preprocessor()

    # -----------------------------------------------------
    # 4. Transform complete dataset
    #
    # IMPORTANT:
    # This uses an already-fitted preprocessor.
    # No fitting occurs here.
    # -----------------------------------------------------

    X_processed, feature_names = (
        transform_data(
            preprocessor,
            X
        )
    )

    print()
    print(
        f"Final feature count : "
        f"{len(feature_names)}"
    )

    # -----------------------------------------------------
    # 5. Reproduce SAME train/test split
    # -----------------------------------------------------

    from sklearn.model_selection import train_test_split

    (
        X_train,
        X_test,
        y_train,
        y_test
    ) = train_test_split(

        X_processed,

        y,

        test_size=0.20,

        random_state=RANDOM_STATE,

        stratify=y

    )

    print()
    print(
        f"Training Samples : {len(X_train)}"
    )

    print(
        f"Testing Samples  : {len(X_test)}"
    )

    # -----------------------------------------------------
    # 6. Load models
    # -----------------------------------------------------

    (
        random_forest,
        xgboost_model,
        isolation_forest
    ) = load_models()

    # =====================================================
    # RANDOM FOREST
    # =====================================================

    print()
    print(
        "Model : RandomForestClassifier"
    )

    rf_results = evaluate_test_set(

        random_forest,

        X_test,

        y_test,

        "RandomForestClassifier"

    )

    # -----------------------------------------------------
    # Cross validation
    # -----------------------------------------------------

    rf_cv = cross_validate_model(

        random_forest,

        X_processed,

        y,

        "RandomForestClassifier"

    )

    # -----------------------------------------------------
    # Overfitting
    # -----------------------------------------------------

    rf_overfit = overfitting_check(

        random_forest,

        X_train,

        y_train,

        X_test,

        y_test

    )

    # -----------------------------------------------------
    # Plots
    # -----------------------------------------------------

    generate_confusion_matrix(

        rf_results["Confusion Matrix"],

        "Random Forest"

    )

    generate_roc_curve(

        y_test,

        rf_results["Probabilities"]

    )

    generate_precision_recall_curve(

        y_test,

        rf_results["Probabilities"]

    )

    generate_feature_importance(

        random_forest,

        feature_names

    )

    # =====================================================
    # XGBOOST
    # =====================================================

    print()
    print(
        "Model : XGBClassifier"
    )

    xgb_results = evaluate_test_set(

        xgboost_model,

        X_test,

        y_test,

        "XGBClassifier"

    )

    xgb_cv = cross_validate_model(

        xgboost_model,

        X_processed,

        y,

        "XGBClassifier"

    )

    # =====================================================
    # ISOLATION FOREST
    # =====================================================

    print()
    print(
        "Model : Isolation Forest"
    )

    iso_raw = isolation_forest.predict(
        X_test
    )

    iso_predictions = np.where(
        iso_raw == -1,
        1,
        0
    )

    iso_accuracy = accuracy_score(
        y_test,
        iso_predictions
    )

    iso_precision = precision_score(
        y_test,
        iso_predictions,
        zero_division=0
    )

    iso_recall = recall_score(
        y_test,
        iso_predictions,
        zero_division=0
    )

    iso_f1 = f1_score(
        y_test,
        iso_predictions,
        zero_division=0
    )

    print()
    print("=" * 60)
    print("ISOLATION FOREST PERFORMANCE")
    print("=" * 60)

    print(
        f"Accuracy  : {iso_accuracy:.4f}"
    )

    print(
        f"Precision : {iso_precision:.4f}"
    )

    print(
        f"Recall    : {iso_recall:.4f}"
    )

    print(
        f"F1 Score  : {iso_f1:.4f}"
    )

    print()
    print("Confusion Matrix")

    print(
        confusion_matrix(
            y_test,
            iso_predictions
        )
    )

    print()
    print("Classification Report")

    print(
        classification_report(
            y_test,
            iso_predictions,
            zero_division=0
        )
    )

    # =====================================================
    # SAVE SUMMARY
    # =====================================================

    comparison = pd.DataFrame({

        "Model": [

            "RandomForestClassifier",

            "XGBClassifier",

            "Isolation Forest"

        ],

        "Accuracy": [

            rf_results["Accuracy"],

            xgb_results["Accuracy"],

            iso_accuracy

        ],

        "Precision": [

            rf_results["Precision"],

            xgb_results["Precision"],

            iso_precision

        ],

        "Recall": [

            rf_results["Recall"],

            xgb_results["Recall"],

            iso_recall

        ],

        "F1 Score": [

            rf_results["F1 Score"],

            xgb_results["F1 Score"],

            iso_f1

        ],

        "ROC AUC": [

            rf_results["ROC AUC"],

            xgb_results["ROC AUC"],

            "N/A"

        ]

    })

    comparison_path = os.path.join(

        EVALUATION_FOLDER,

        "final_model_comparison.csv"

    )

    comparison.to_csv(

        comparison_path,

        index=False

    )

    print()
    print("=" * 60)
    print("FINAL MODEL COMPARISON")
    print("=" * 60)

    print(
        comparison.to_string(
            index=False
        )
    )

    print()
    print(
        f"Saved : {comparison_path}"
    )

    # -----------------------------------------------------
    # Save detailed RF evaluation report
    # -----------------------------------------------------

    save_evaluation_report(

        rf_results,

        rf_cv,

        rf_overfit

    )

    # =====================================================
    # FINAL MESSAGE
    # =====================================================

    print()
    print("=" * 60)
    print("MODEL EVALUATION COMPLETED")
    print("=" * 60)

    print()
    print(
        "IMPORTANT:"
    )

    print(
        "The reported metrics are evaluation results "
        "on the current CERT-derived employee dataset."
    )

    print(
        "They should not be interpreted as guaranteed "
        "real-world detection accuracy."
    )

    print()
    print("=" * 60)


# =========================================================
# PROGRAM ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()