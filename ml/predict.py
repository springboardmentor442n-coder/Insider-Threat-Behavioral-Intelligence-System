"""
=========================================================
Prediction + Risk Engine
AI Insider Threat Detection System
---------------------------------------------------------
ML Prediction:
    Random Forest

Additional analysis:
    Behavioural Risk Score
    Risk Indicators
    SOC Recommendation

IMPORTANT:
    ML probability and behavioural risk score are kept
    separate. The behavioural score does NOT alter the
    Random Forest prediction.
=========================================================
"""

import os
import joblib
import pandas as pd


# =========================================================
# CONFIGURATION
# =========================================================

MODEL_FOLDER = "ml/models"

MODEL_PATH = os.path.join(
    MODEL_FOLDER,
    "random_forest.pkl"
)

PREPROCESSOR_PATH = os.path.join(
    MODEL_FOLDER,
    "preprocessor.pkl"
)


# =========================================================
# LOAD MODEL
# =========================================================

def load_model():

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "random_forest.pkl not found. "
            "Run ml/train_model.py first."
        )

    if not os.path.exists(PREPROCESSOR_PATH):
        raise FileNotFoundError(
            "preprocessor.pkl not found. "
            "Run ml/train_model.py first."
        )

    model = joblib.load(MODEL_PATH)

    preprocessor = joblib.load(
        PREPROCESSOR_PATH
    )

    return model, preprocessor


# =========================================================
# ML RISK LEVEL
# =========================================================

def get_ml_risk_level(probability):

    if probability < 0.30:
        return "LOW"

    elif probability < 0.60:
        return "MEDIUM"

    elif probability < 0.80:
        return "HIGH"

    else:
        return "CRITICAL"


# =========================================================
# BEHAVIOURAL RISK SCORE
# =========================================================

def calculate_behavioral_risk(employee):

    score = 0
    indicators = []

    # -----------------------------------------------------
    # USB ACTIVITY
    # -----------------------------------------------------

    usb = float(
        employee.get(
            "usb_total_activity",
            0
        )
    )

    if usb >= 20:

        points = 20
        score += points

        indicators.append({
            "feature": "USB Activity",
            "value": usb,
            "points": points,
            "severity": "HIGH",
            "reason":
                "Very high removable-device activity."
        })

    elif usb >= 10:

        points = 12
        score += points

        indicators.append({
            "feature": "USB Activity",
            "value": usb,
            "points": points,
            "severity": "MEDIUM",
            "reason":
                "Elevated removable-device activity."
        })

    # -----------------------------------------------------
    # FILE COPYING
    # -----------------------------------------------------

    file_copy = float(
        employee.get(
            "file_copy_count",
            0
        )
    )

    if file_copy >= 30:

        points = 20
        score += points

        indicators.append({
            "feature": "File Copy Activity",
            "value": file_copy,
            "points": points,
            "severity": "HIGH",
            "reason":
                "Very high file-copy activity."
        })

    elif file_copy >= 20:

        points = 12
        score += points

        indicators.append({
            "feature": "File Copy Activity",
            "value": file_copy,
            "points": points,
            "severity": "MEDIUM",
            "reason":
                "Elevated file-copy activity."
        })

    # -----------------------------------------------------
    # MAXIMUM DAILY FILE COPY
    # -----------------------------------------------------

    max_daily = float(
        employee.get(
            "max_daily_file_copy",
            0
        )
    )

    if max_daily >= 40:

        points = 15
        score += points

        indicators.append({
            "feature":
                "Maximum Daily File Copy",
            "value": max_daily,
            "points": points,
            "severity": "HIGH",
            "reason":
                "Very high single-day file-copy activity."
        })

    elif max_daily >= 30:

        points = 8
        score += points

        indicators.append({
            "feature":
                "Maximum Daily File Copy",
            "value": max_daily,
            "points": points,
            "severity": "MEDIUM",
            "reason":
                "Elevated single-day file-copy activity."
        })

    # -----------------------------------------------------
    # NIGHT LOGIN
    # -----------------------------------------------------

    night_ratio = float(
        employee.get(
            "night_login_ratio",
            0
        )
    )

    if night_ratio >= 0.50:

        points = 15
        score += points

        indicators.append({
            "feature":
                "Night Login Activity",
            "value":
                round(
                    night_ratio * 100,
                    2
                ),
            "points": points,
            "severity": "HIGH",
            "reason":
                "A large proportion of logins occur at night."
        })

    elif night_ratio >= 0.30:

        points = 8
        score += points

        indicators.append({
            "feature":
                "Night Login Activity",
            "value":
                round(
                    night_ratio * 100,
                    2
                ),
            "points": points,
            "severity": "MEDIUM",
            "reason":
                "Elevated after-hours login activity."
        })

    # -----------------------------------------------------
    # WEEKEND LOGIN
    # -----------------------------------------------------

    weekend_ratio = float(
        employee.get(
            "weekend_login_ratio",
            0
        )
    )

    if weekend_ratio >= 0.50:

        points = 10
        score += points

        indicators.append({
            "feature":
                "Weekend Login Activity",
            "value":
                round(
                    weekend_ratio * 100,
                    2
                ),
            "points": points,
            "severity": "HIGH",
            "reason":
                "Large proportion of logins occur during weekends."
        })

    elif weekend_ratio >= 0.30:

        points = 6
        score += points

        indicators.append({
            "feature":
                "Weekend Login Activity",
            "value":
                round(
                    weekend_ratio * 100,
                    2
                ),
            "points": points,
            "severity": "MEDIUM",
            "reason":
                "Elevated weekend login activity."
        })

    # -----------------------------------------------------
    # PC SWITCHING
    # -----------------------------------------------------

    pc_switching = float(
        employee.get(
            "pc_switching_frequency",
            0
        )
    )

    if pc_switching >= 0.50:

        points = 10
        score += points

        indicators.append({
            "feature": "PC Switching",
            "value":
                round(
                    pc_switching,
                    4
                ),
            "points": points,
            "severity": "HIGH",
            "reason":
                "Frequent switching between computers."
        })

    elif pc_switching >= 0.30:

        points = 5
        score += points

        indicators.append({
            "feature": "PC Switching",
            "value":
                round(
                    pc_switching,
                    4
                ),
            "points": points,
            "severity": "MEDIUM",
            "reason":
                "Elevated computer switching behaviour."
        })

    # -----------------------------------------------------
    # EXTERNAL EMAIL
    # -----------------------------------------------------

    external_ratio = float(
        employee.get(
            "external_email_ratio",
            0
        )
    )

    if external_ratio >= 0.50:

        points = 10
        score += points

        indicators.append({
            "feature":
                "External Email Activity",
            "value":
                round(
                    external_ratio * 100,
                    2
                ),
            "points": points,
            "severity": "HIGH",
            "reason":
                "Large proportion of emails are external."
        })

    elif external_ratio >= 0.30:

        points = 5
        score += points

        indicators.append({
            "feature":
                "External Email Activity",
            "value":
                round(
                    external_ratio * 100,
                    2
                ),
            "points": points,
            "severity": "MEDIUM",
            "reason":
                "Elevated external email activity."
        })

    # -----------------------------------------------------
    # LIMIT SCORE
    # -----------------------------------------------------

    score = min(score, 100)

    # -----------------------------------------------------
    # SORT INDICATORS
    # -----------------------------------------------------

    indicators.sort(
        key=lambda x: x["points"],
        reverse=True
    )

    return score, indicators


# =========================================================
# OVERALL RISK LEVEL
# =========================================================

def get_overall_risk_level(
    ml_probability,
    behavioral_score
):

    if (
        ml_probability >= 0.80
        or behavioral_score >= 70
    ):
        return "CRITICAL"

    if (
        ml_probability >= 0.60
        or behavioral_score >= 50
    ):
        return "HIGH"

    if (
        ml_probability >= 0.30
        or behavioral_score >= 25
    ):
        return "MEDIUM"

    return "LOW"


# =========================================================
# SOC RECOMMENDATION
# =========================================================

def get_recommendation(
    status,
    risk_level,
    indicators
):

    if risk_level == "CRITICAL":

        return (
            "Immediately escalate this employee "
            "for SOC investigation. Review recent "
            "USB, file, login and communication activity."
        )

    if risk_level == "HIGH":

        return (
            "Perform a detailed review of the "
            "employee's recent behavioural activity "
            "and investigate the highest-risk indicators."
        )

    if risk_level == "MEDIUM":

        return (
            "Continue monitoring the employee and "
            "review the identified behavioural indicators."
        )

    return (
        "No immediate escalation is recommended. "
        "Continue normal monitoring."
    )


# =========================================================
# PREDICT EMPLOYEE
# =========================================================

def predict_employee(employee_data):

    model, preprocessor = load_model()

    # -----------------------------------------------------
    # Convert input to DataFrame
    # -----------------------------------------------------

    employee_df = pd.DataFrame(
        [employee_data]
    )

    # -----------------------------------------------------
    # Remove non-model fields
    # -----------------------------------------------------

    employee_df.drop(
        columns=[
            "user",
            "threat_label"
        ],
        errors="ignore",
        inplace=True
    )

    # -----------------------------------------------------
    # Get exact training columns
    # -----------------------------------------------------

    expected_columns = list(
        preprocessor.feature_names_in_
    )

    # -----------------------------------------------------
    # Add missing fields
    # -----------------------------------------------------

    for column in expected_columns:

        if column not in employee_df.columns:

            employee_df[column] = 0

    # -----------------------------------------------------
    # Remove unexpected fields
    # -----------------------------------------------------

    employee_df = employee_df[
        expected_columns
    ]

    # -----------------------------------------------------
    # SAME preprocessing as training
    # -----------------------------------------------------

    X = preprocessor.transform(
        employee_df
    )

    # =====================================================
    # ML PREDICTION
    # =====================================================

    prediction = model.predict(X)[0]

    probabilities = model.predict_proba(X)[0]

    # -----------------------------------------------------
    # IMPORTANT FIX
    #
    # Do NOT assume probabilities[1] is THREAT.
    #
    # Find the probability corresponding to class 1.
    # -----------------------------------------------------

    classes = list(model.classes_)

    if 1 in classes:

        threat_index = classes.index(1)

        threat_probability = float(
            probabilities[threat_index]
        )

    else:

        raise ValueError(
            "The trained model does not contain "
            "class label 1 for THREAT."
        )

    normal_probability = 1.0 - threat_probability

    # -----------------------------------------------------
    # Convert prediction to Python integer
    # -----------------------------------------------------

    prediction = int(prediction)

    # -----------------------------------------------------
    # ML classification
    # -----------------------------------------------------

    if prediction == 1:

        ml_status = "THREAT"

    else:

        ml_status = "NORMAL"

    # -----------------------------------------------------
    # ML risk level
    # -----------------------------------------------------

    ml_risk_level = get_ml_risk_level(
        threat_probability
    )

    # -----------------------------------------------------
    # Behavioural analysis
    # -----------------------------------------------------

    behavioral_score, indicators = (
        calculate_behavioral_risk(
            employee_data
        )
    )

    # -----------------------------------------------------
    # Overall risk
    # -----------------------------------------------------

    overall_risk_level = (
        get_overall_risk_level(
            threat_probability,
            behavioral_score
        )
    )
    # ---------------------------------------------------------
# FINAL SECURITY STATUS
# ---------------------------------------------------------
# A high/critical behavioral risk should also be treated
# as a final security threat.

    if (
            ml_status == "THREAT"
            or overall_risk_level in ["HIGH", "CRITICAL"]
        ):
            status = "THREAT"
    else:
            status = "NORMAL"

    # -----------------------------------------------------
    # Recommendation
    # -----------------------------------------------------

    recommendation = get_recommendation(
        status,
        overall_risk_level,
        indicators
    )

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    return {

        "status":
            status,

        "prediction":
            prediction,

        "threat_probability":
            round(
                threat_probability * 100,
                2
            ),

        "normal_probability":
            round(
                normal_probability * 100,
                2
            ),

        "ml_risk_level":
            ml_risk_level,

        "behavioral_risk_score":
            behavioral_score,

        "overall_risk_level":
            overall_risk_level,

        "risk_indicators":
            indicators,

        "recommendation":
            recommendation,

        "model":
            "Random Forest"
    }


# =========================================================
# TEST EMPLOYEE
# =========================================================

def get_test_employee():

    return {

        "department": "Finance",

        "role": "Financial Analyst",

        "business_unit": 1,

        "login_count": 20,

        "logoff_count": 18,

        "night_login_count": 8,

        "weekend_login_count": 3,

        "unique_pc_count": 4,

        "night_login_ratio": 0.40,

        "weekend_login_ratio": 0.15,

        "pc_switching_frequency": 0.20,

        "usb_connect_count": 12,

        "usb_disconnect_count": 10,

        "usb_total_activity": 22,

        "usb_connect_ratio": 0.55,

        "file_copy_count": 35,

        "avg_daily_file_copy": 17.5,

        "max_daily_file_copy": 40,

        "email_sent_count": 30,

        "external_email_count": 8,

        "avg_attachment_count": 2.5,

        "avg_email_size": 150.0,

        "external_email_ratio": 0.27,

        "website_visit_count": 300,

        "unique_domain_count": 80,

        "avg_daily_web_activity": 150.0,

        "O": 0.5,

        "C": 0.4,

        "E": 0.5,

        "A": 0.6,

        "N": 0.7
    }


# =========================================================
# PRINT RESULT
# =========================================================

def print_result(result):

    print()
    print("=" * 60)
    print("INSIDER THREAT ANALYSIS")
    print("=" * 60)

    print()

    print(
        f"ML Classification       : "
        f"{result['status']}"
    )

    print(
        f"Threat Probability      : "
        f"{result['threat_probability']}%"
    )

    print(
        f"Normal Probability      : "
        f"{result['normal_probability']}%"
    )

    print(
        f"ML Risk Level           : "
        f"{result['ml_risk_level']}"
    )

    print(
        f"Behavioural Risk Score  : "
        f"{result['behavioral_risk_score']}/100"
    )

    print(
        f"Overall Risk Level      : "
        f"{result['overall_risk_level']}"
    )

    print(
        f"Model                   : "
        f"{result['model']}"
    )

    print()
    print("=" * 60)
    print("RISK INDICATORS")
    print("=" * 60)

    if result["risk_indicators"]:

        for indicator in result["risk_indicators"]:

            print()

            print(
                f"[{indicator['severity']}] "
                f"{indicator['feature']}"
            )

            print(
                f"Value  : {indicator['value']}"
            )

            print(
                f"Points : +{indicator['points']}"
            )

            print(
                f"Reason : {indicator['reason']}"
            )

    else:

        print(
            "No major behavioural risk indicators detected."
        )

    print()
    print("=" * 60)
    print("SOC RECOMMENDATION")
    print("=" * 60)

    print()
    print(
        result["recommendation"]
    )

    print()
    print("=" * 60)


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 60)
    print("AI INSIDER THREAT DETECTION SYSTEM")
    print("FINAL PREDICTION ENGINE")
    print("=" * 60)

    employee = get_test_employee()

    result = predict_employee(
        employee
    )

    print_result(
        result
    )


# =========================================================
# PROGRAM ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()