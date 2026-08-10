"""
=========================================================
Model Training
AI Insider Threat Detection System
---------------------------------------------------------
Leakage-safe training pipeline.

Models:
    1. Random Forest
    2. XGBoost
    3. Isolation Forest

Pipeline:
    Dataset
        ↓
    Train/Test Split
        ↓
    Fit preprocessing ONLY on training data
        ↓
    SMOTE ONLY on training data
        ↓
    Train models
        ↓
    Evaluate on untouched test data
        ↓
    Save models and preprocessing
=========================================================
"""

import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

from sklearn.ensemble import (
    RandomForestClassifier,
    IsolationForest
)

from xgboost import XGBClassifier

from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)


# =========================================================
# CONFIGURATION
# =========================================================

DATASET_PATH = "dataset/processed/employee_features.csv"

MODEL_FOLDER = "ml/models"

TARGET_COLUMN = "threat_label"

TEST_SIZE = 0.20

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
# BASIC DATA CLEANING
# =========================================================

def clean_dataset(df):

    print()
    print("=" * 60)
    print("DATASET CLEANING")
    print("=" * 60)

    df = df.copy()

    # -----------------------------------------------------
    # Remove employee identifier
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

    print()
    print("Dataset cleaning completed.")

    return df


# =========================================================
# SPLIT DATASET
# =========================================================

def split_dataset(df):

    print()
    print("=" * 60)
    print("TRAIN / TEST SPLIT")
    print("=" * 60)

    X = df.drop(
        columns=[TARGET_COLUMN]
    )

    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(

        X,

        y,

        test_size=TEST_SIZE,

        random_state=RANDOM_STATE,

        stratify=y

    )

    print(
        f"Training Samples : {len(X_train)}"
    )

    print(
        f"Testing Samples  : {len(X_test)}"
    )

    print()
    print("Training class distribution:")
    print(y_train.value_counts())

    print()
    print("Testing class distribution:")
    print(y_test.value_counts())

    return (
        X_train,
        X_test,
        y_train,
        y_test
    )


# =========================================================
# CREATE PREPROCESSOR
# =========================================================

def create_preprocessor(X_train):

    print()
    print("=" * 60)
    print("CREATING PREPROCESSOR")
    print("=" * 60)

    categorical_columns = (
        X_train
        .select_dtypes(
            include=["object"]
        )
        .columns
        .tolist()
    )

    numerical_columns = (
        X_train
        .select_dtypes(
            exclude=["object"]
        )
        .columns
        .tolist()
    )

    print(
        f"Categorical columns : {categorical_columns}"
    )

    print(
        f"Numerical columns   : {len(numerical_columns)}"
    )

    # -----------------------------------------------------
    # Categorical pipeline
    # -----------------------------------------------------

    categorical_pipeline = Pipeline(

        steps=[

            (
                "imputer",

                SimpleImputer(
                    strategy="most_frequent"
                )

            ),

            (
                "encoder",

                OrdinalEncoder(

                    handle_unknown="use_encoded_value",

                    unknown_value=-1

                )

            )

        ]

    )

    # -----------------------------------------------------
    # Numerical pipeline
    # -----------------------------------------------------

    numerical_pipeline = Pipeline(

        steps=[

            (
                "imputer",

                SimpleImputer(
                    strategy="median"
                )

            )

        ]

    )

    # -----------------------------------------------------
    # Combined preprocessing
    # -----------------------------------------------------

    preprocessor = ColumnTransformer(

        transformers=[

            (
                "categorical",

                categorical_pipeline,

                categorical_columns

            ),

            (
                "numerical",

                numerical_pipeline,

                numerical_columns

            )

        ],

        remainder="drop"

    )

    return preprocessor


# =========================================================
# TRANSFORM TRAINING DATA
# =========================================================

def prepare_training_data(
    preprocessor,
    X_train,
    y_train
):

    print()
    print("=" * 60)
    print("FITTING PREPROCESSOR ON TRAINING DATA")
    print("=" * 60)

    X_train_processed = preprocessor.fit_transform(
        X_train
    )

    print(
        f"Processed Training Features : "
        f"{X_train_processed.shape[1]}"
    )

    # -----------------------------------------------------
    # SMOTE
    # -----------------------------------------------------

    print()
    print("=" * 60)
    print("APPLYING SMOTE")
    print("=" * 60)

    print("Before SMOTE:")
    print(y_train.value_counts())

    smote = SMOTE(
        random_state=RANDOM_STATE
    )

    X_train_smote, y_train_smote = (
        smote.fit_resample(
            X_train_processed,
            y_train
        )
    )

    print()
    print("After SMOTE:")
    print(y_train_smote.value_counts())

    return (
        X_train_processed,
        y_train_smote,
        X_train_smote
    )


# =========================================================
# TRANSFORM TEST DATA
# =========================================================

def transform_test_data(
    preprocessor,
    X_test
):

    print()
    print("=" * 60)
    print("TRANSFORMING TEST DATA")
    print("=" * 60)

    # IMPORTANT:
    #
    # We use transform(), NOT fit_transform().
    #
    # Therefore test data never influences
    # preprocessing parameters.

    X_test_processed = preprocessor.transform(
        X_test
    )

    print(
        f"Processed Test Features : "
        f"{X_test_processed.shape[1]}"
    )

    return X_test_processed


# =========================================================
# TRAIN RANDOM FOREST
# =========================================================

def train_random_forest(
    X_train,
    y_train
):

    print()
    print("=" * 60)
    print("TRAINING RANDOM FOREST")
    print("=" * 60)

    model = RandomForestClassifier(

        n_estimators=300,

        max_depth=15,

        min_samples_leaf=2,

        class_weight=None,

        random_state=RANDOM_STATE,

        n_jobs=-1

    )

    model.fit(
        X_train,
        y_train
    )

    return model


# =========================================================
# TRAIN XGBOOST
# =========================================================

def train_xgboost(
    X_train,
    y_train
):

    print()
    print("=" * 60)
    print("TRAINING XGBOOST")
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


# =========================================================
# TRAIN ISOLATION FOREST
# =========================================================

def train_isolation_forest(
    X_train_processed,
    y_train
):

    print()
    print("=" * 60)
    print("TRAINING ISOLATION FOREST")
    print("=" * 60)

    # -----------------------------------------------------
    # Isolation Forest should learn NORMAL behaviour.
    #
    # Therefore we train it using only normal employees.
    # -----------------------------------------------------

    normal_data = X_train_processed[
        y_train.values == 0
    ]

    print(
        f"Normal training samples : "
        f"{len(normal_data)}"
    )

    model = IsolationForest(

        n_estimators=300,

        contamination=0.07,

        random_state=RANDOM_STATE,

        n_jobs=-1

    )

    model.fit(
        normal_data
    )

    return model


# =========================================================
# EVALUATE CLASSIFIER
# =========================================================

def evaluate_classifier(
    model,
    X_test,
    y_test
):

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
    print("=" * 60)
    print("MODEL PERFORMANCE")
    print("=" * 60)

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

    print()
    print("Confusion Matrix")

    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )

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

        "Model":
            model.__class__.__name__,

        "Accuracy":
            round(accuracy, 4),

        "Precision":
            round(precision, 4),

        "Recall":
            round(recall, 4),

        "F1 Score":
            round(f1, 4),

        "ROC AUC":
            round(roc_auc, 4)

    }


# =========================================================
# EVALUATE ISOLATION FOREST
# =========================================================

def evaluate_isolation_forest(
    model,
    X_test,
    y_test
):

    raw_predictions = model.predict(
        X_test
    )

    # Isolation Forest:
    #
    # +1 = normal
    # -1 = anomaly
    #
    # Our project:
    #
    # 0 = normal
    # 1 = threat

    predictions = [

        1 if value == -1 else 0

        for value in raw_predictions

    ]

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

    print()
    print("=" * 60)
    print("ISOLATION FOREST PERFORMANCE")
    print("=" * 60)

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

    print()
    print("Confusion Matrix")

    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )

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

        "Model":
            "Isolation Forest",

        "Accuracy":
            round(accuracy, 4),

        "Precision":
            round(precision, 4),

        "Recall":
            round(recall, 4),

        "F1 Score":
            round(f1, 4),

        "ROC AUC":
            "N/A"

    }


# =========================================================
# FEATURE IMPORTANCE
# =========================================================

def save_feature_importance(
    model,
    feature_names
):

    print()
    print("=" * 60)
    print("TOP 15 IMPORTANT FEATURES")
    print("=" * 60)

    importance = pd.DataFrame({

        "Feature":
            feature_names,

        "Importance":
            model.feature_importances_

    })

    importance = importance.sort_values(

        by="Importance",

        ascending=False

    )

    print(
        importance.head(15).to_string(
            index=False
        )
    )

    importance.to_csv(

        os.path.join(
            MODEL_FOLDER,
            "feature_importance.csv"
        ),

        index=False

    )

    joblib.dump(

        importance,

        os.path.join(
            MODEL_FOLDER,
            "feature_importance.pkl"
        )

    )


# =========================================================
# SAVE MODEL
# =========================================================

def save_model(
    model,
    filename
):

    path = os.path.join(

        MODEL_FOLDER,

        filename

    )

    joblib.dump(
        model,
        path
    )

    print(
        f"Model Saved : {path}"
    )


# =========================================================
# COMPARE MODELS
# =========================================================

def compare_models(results):

    print()
    print("=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)

    comparison_df = pd.DataFrame(
        results
    )

    print(
        comparison_df.to_string(
            index=False
        )
    )

    comparison_path = os.path.join(

        MODEL_FOLDER,

        "model_comparison.csv"

    )

    comparison_df.to_csv(

        comparison_path,

        index=False

    )

    print()
    print(
        f"Comparison saved to: "
        f"{comparison_path}"
    )

    # -----------------------------------------------------
    # Select best supervised model
    #
    # We do NOT select Isolation Forest simply because
    # it is an anomaly detector.
    #
    # For our labelled detection problem,
    # F1 Score is the selection criterion.
    # -----------------------------------------------------

    supervised_models = comparison_df[
        comparison_df["Model"].isin(
            [
                "RandomForestClassifier",
                "XGBClassifier"
            ]
        )
    ]

    best_model = supervised_models.loc[
        supervised_models[
            "F1 Score"
        ].idxmax()
    ]

    print()
    print("=" * 60)
    print("BEST SUPERVISED MODEL")
    print("=" * 60)

    print(
        best_model.to_string()
    )

    if (
        best_model["Model"]
        == "RandomForestClassifier"
    ):

        best_model_file = (
            "random_forest.pkl"
        )

    else:

        best_model_file = (
            "xgboost.pkl"
        )

    best_model_path = os.path.join(

        MODEL_FOLDER,

        "best_model.txt"

    )

    with open(
        best_model_path,
        "w"
    ) as file:

        file.write(
            best_model_file
        )

    print()
    print(
        f"Best Model Saved : "
        f"{best_model_file}"
    )

    return comparison_df


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 60)
    print("AI INSIDER THREAT DETECTION SYSTEM")
    print("LEAKAGE-SAFE MODEL TRAINING PIPELINE")
    print("=" * 60)

    # -----------------------------------------------------
    # Create model directory
    # -----------------------------------------------------

    os.makedirs(
        MODEL_FOLDER,
        exist_ok=True
    )

    # -----------------------------------------------------
    # 1. Load
    # -----------------------------------------------------

    df = load_dataset()

    # -----------------------------------------------------
    # 2. Clean
    # -----------------------------------------------------

    df = clean_dataset(df)

    # -----------------------------------------------------
    # 3. Split BEFORE fitting preprocessing
    # -----------------------------------------------------

    (
        X_train,
        X_test,
        y_train,
        y_test
    ) = split_dataset(df)

    # -----------------------------------------------------
    # 4. Create preprocessing definition
    # -----------------------------------------------------

    preprocessor = create_preprocessor(
        X_train
    )

    # -----------------------------------------------------
    # 5. Fit preprocessing ONLY on training data
    # -----------------------------------------------------

    (
        X_train_processed,
        y_train_smote,
        X_train_smote
    ) = prepare_training_data(

        preprocessor,

        X_train,

        y_train

    )

    # -----------------------------------------------------
    # 6. Transform untouched test data
    # -----------------------------------------------------

    X_test_processed = transform_test_data(

        preprocessor,

        X_test

    )

    # -----------------------------------------------------
    # 7. Save preprocessor
    # -----------------------------------------------------

    joblib.dump(

        preprocessor,

        os.path.join(
            MODEL_FOLDER,
            "preprocessor.pkl"
        )

    )

    # -----------------------------------------------------
    # 8. Get transformed feature names
    # -----------------------------------------------------

    feature_names = (
        preprocessor
        .get_feature_names_out()
    )

    joblib.dump(

        list(feature_names),

        os.path.join(
            MODEL_FOLDER,
            "feature_columns.pkl"
        )

    )

    print()
    print(
        f"Final feature count : "
        f"{len(feature_names)}"
    )

    # =====================================================
    # RANDOM FOREST
    # =====================================================

    rf_model = train_random_forest(

        X_train_smote,

        y_train_smote

    )

    print()
    print("RANDOM FOREST RESULTS")

    rf_results = evaluate_classifier(

        rf_model,

        X_test_processed,

        y_test

    )

    save_feature_importance(

        rf_model,

        feature_names

    )

    save_model(

        rf_model,

        "random_forest.pkl"

    )

    # =====================================================
    # XGBOOST
    # =====================================================

    xgb_model = train_xgboost(

        X_train_smote,

        y_train_smote

    )

    print()
    print("XGBOOST RESULTS")

    xgb_results = evaluate_classifier(

        xgb_model,

        X_test_processed,

        y_test

    )

    save_model(

        xgb_model,

        "xgboost.pkl"

    )

    # =====================================================
    # ISOLATION FOREST
    # =====================================================

    iso_model = train_isolation_forest(

        X_train_processed,

        y_train

    )

    print()
    print("ISOLATION FOREST RESULTS")

    iso_results = evaluate_isolation_forest(

        iso_model,

        X_test_processed,

        y_test

    )

    save_model(

        iso_model,

        "isolation_forest.pkl"

    )

    # =====================================================
    # COMPARE MODELS
    # =====================================================

    compare_models(

        [

            rf_results,

            xgb_results,

            iso_results

        ]

    )

    # =====================================================
    # FINISHED
    # =====================================================

    print()
    print("=" * 60)
    print("MODEL TRAINING COMPLETED SUCCESSFULLY")
    print("=" * 60)


# =========================================================
# PROGRAM ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()