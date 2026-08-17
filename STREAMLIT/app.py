
import sys
import streamlit as st
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import utils
import predict

FEATURE_NAMES = predict.FEATURE_NAMES
FLOAT_FEATURES = utils.get_float_features()

FEATURE_CATEGORIES = [
    ("📂 Logon Features", [
        "total_events", "total_logons", "total_logoffs",
        "after_hours_events", "weekend_events", "unique_pcs_x",
        "working_days", "avg_events_per_day", "first_login_hour",
        "last_logout_hour", "work_duration_hours"
    ]),
    ("💻 Device Features", [
        "total_device_events", "total_connects", "total_disconnects",
        "after_hours_device_events", "weekend_device_events"
    ]),
    ("📧 Email Features", [
        "total_email_events", "total_email_sent", "after_hours_email_count",
        "weekend_email_count", "attachment_email_count",
        "average_email_size_kb", "average_recipient_count"
    ]),
    ("📁 File Features", [
        "total_file_events", "file_open_count", "file_copy_count",
        "file_write_count", "file_delete_count", "files_to_removable_media",
        "files_from_removable_media", "unique_files", "unique_pcs_y",
        "after_hours_file_activity", "weekend_file_count"
    ]),
    ("🌐 HTTP Features", [
        "total_http_events", "http_visit_count", "http_download_count",
        "http_upload_count", "after_hours_http_count", "weekend_http_count",
        "unique_urls", "unique_http_pcs"
    ]),
    ("🧠 Psychometric Features", ["O", "C", "E", "A", "N"]),
]

model_info_rows = [
    ("Algorithm", "Random Forest"),
    ("Training Samples", 3200),
    ("Testing Samples", 800),
    ("Number of Features", len(FEATURE_NAMES)),
    ("Dataset", "CERT R6.2"),
]

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Insider Threat Detection System",
    page_icon="🛡️",
    layout="wide"
)

utils.load_css()

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Page",
    [
        "Home",
        "Single Prediction",
        "Batch Prediction",
        "About"
    ]
)

# -----------------------------
# Home Page
# -----------------------------
if page == "Home":

    st.title("🛡 Insider Threat Detection Dashboard")

    st.markdown("---")

    st.write(
        """
Welcome to the Insider Threat Detection System.

This application predicts potential insider threats
using a trained Random Forest Machine Learning model.
"""
    )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Model", "Random Forest")

    with col2:
        st.metric("Features", len(FEATURE_NAMES))

    with col3:
        st.metric("Dataset", "CERT R6.2")

    st.markdown("---")

    st.subheader("Project Overview")

    st.write("""
The application analyzes employee behavioural data including:

- Login Activity
- Device Usage
- Email Behaviour
- File Operations
- HTTP Activity
- Psychometric Features

to identify potential insider threats.
""")

    st.markdown("---")

    st.subheader("Project Workflow")

    workflow = [
        "Dataset Collection",
        "Feature Engineering",
        "Data Preprocessing",
        "Model Training",
        "Model Evaluation",
        "Prediction"
    ]

    workflow_df = pd.DataFrame({
        "Step": range(1, 7),
        "Process": workflow
    })

    st.table(workflow_df)

    st.markdown("---")

    st.subheader("Model Information")

    model_info = pd.DataFrame(
        model_info_rows,
        columns=["Attribute", "Value"]
    ).iloc[:4]

    st.table(model_info)

    st.markdown("---")

    st.subheader("Dataset Distribution")

    distribution = pd.DataFrame({
        "Class": ["Normal", "Insider"],
        "Employees": [3995, 5]
    })

    st.bar_chart(distribution.set_index("Class"))

    st.markdown("---")

    st.subheader("Feature Categories")

    category = pd.DataFrame({
        "Category": ["Logon", "Device", "Email", "File", "HTTP", "Psychometric"],
        "Included": ["Yes", "Yes", "Yes", "Yes", "Yes", "Yes"]
    })

    st.table(category)

    st.markdown("---")

    st.subheader("Technologies Used")

    tech = pd.DataFrame({
        "Technology": ["Python", "Pandas", "NumPy", "Scikit-Learn", "Streamlit", "Joblib"]
    })

    st.table(tech)

    st.markdown("---")

    st.caption(
        "Insider Threat Detection System | B.Tech AI & ML Major Project"
    )

# -----------------------------
# Single Prediction Page
# -----------------------------
elif page == "Single Prediction":

    st.title("👤 Single Employee Prediction")

    st.markdown("---")

    st.write("Enter feature values below")

    input_data = []

    for category, features in FEATURE_CATEGORIES:

        with st.expander(category, expanded=True):

            col1, col2 = st.columns(2)

            for i, feature in enumerate(features):

                with (col1 if i % 2 == 0 else col2):

                    if feature in FLOAT_FEATURES:

                        value = st.number_input(
                            feature,
                            value=0.0,
                            step=0.1,
                            format="%.2f",
                            key=feature
                        )

                    else:

                        value = st.number_input(
                            feature,
                            value=0,
                            step=1,
                            format="%d",
                            key=feature
                        )

                    input_data.append(value)

    if st.button("Predict Insider Threat"):

        prediction, probability = predict.predict_single(input_data)

        st.markdown("---")

        st.header("Prediction Result")

        col1, col2 = st.columns(2)

        with col1:

            if prediction == 1:
                st.error("🔴 Insider Threat Detected")
            else:
                st.success("🟢 Normal Employee")

        with col2:

            risk = probability[1]
            level = predict.risk_level(risk)

            if "High" in level:
                st.error("🔴 HIGH RISK")
            elif "Medium" in level:
                st.warning("🟡 MEDIUM RISK")
            else:
                st.success("🟢 LOW RISK")

        st.markdown("---")

        st.subheader("Prediction Probability")

        st.progress(float(probability[1]))

        metric1, metric2 = st.columns(2)

        metric1.metric(
            "Normal Probability",
            f"{probability[0]*100:.2f}%"
        )

        metric2.metric(
            "Insider Probability",
            f"{probability[1]*100:.2f}%"
        )

        st.markdown("---")

        st.subheader("Employee Summary")

        summary = pd.DataFrame({
            "Feature": FEATURE_NAMES,
            "Value": input_data
        })

        st.dataframe(summary)

        st.markdown("---")

        st.subheader("Recommendation")

        if predict.risk_level(probability[1]) == "🟢 Low":
            st.success("Employee behaviour appears normal.")
        elif predict.risk_level(probability[1]) == "🟡 Medium":
            st.warning("Employee should be monitored.")
        else:
            st.error("Immediate investigation recommended.")

# -----------------------------
# Batch Prediction
# -----------------------------
elif page == "Batch Prediction":

    st.title("📂 Batch Prediction")

    st.markdown("---")

    st.write(
        "Upload a CSV file containing employee features."
    )

    uploaded_file = st.file_uploader(
        "Choose CSV File",
        type=["csv"]
    )

    if uploaded_file is not None:

        data = pd.read_csv(uploaded_file)

        st.subheader("Uploaded Dataset")

        st.dataframe(data.head())

        if st.button("Run Prediction"):

            missing = [
                col
                for col in FEATURE_NAMES
                if col not in data.columns
            ]

            if missing:

                st.error(
                    f"Missing Columns: {missing}"
                )

            else:

                data = predict.predict_batch(data)

                st.success("Prediction Completed Successfully")

                st.subheader("Prediction Results")

                st.dataframe(data)

                st.markdown("---")

                st.subheader("Prediction Summary")

                total = len(data)

                normal = (data["Prediction"] == 0).sum()

                insider = (data["Prediction"] == 1).sum()

                low = (data["Risk Level"] == "🟢 Low").sum()

                medium = (data["Risk Level"] == "🟡 Medium").sum()

                high = (data["Risk Level"] == "🔴 High").sum()

                c1, c2, c3 = st.columns(3)

                c1.metric("Employees", total)
                c2.metric("Normal", normal)
                c3.metric("Insiders", insider)

                c1, c2, c3 = st.columns(3)

                c1.metric("🟢 Low", low)
                c2.metric("🟡 Medium", medium)
                c3.metric("🔴 High", high)

                st.markdown("---")

                risk = pd.DataFrame({
                    "Risk": ["Low", "Medium", "High"],
                    "Employees": [low, medium, high]
                })

                st.bar_chart(risk.set_index("Risk"))

                prediction_chart = pd.DataFrame({
                    "Prediction": ["Normal", "Insider"],
                    "Count": [normal, insider]
                })

                st.bar_chart(prediction_chart.set_index("Prediction"))

                st.markdown("---")

                st.subheader("Highest Risk Employees")

                top = data.sort_values(
                    by="Insider Probability",
                    ascending=False
                )

                st.dataframe(top.head(10))

                csv = data.to_csv(index=False).encode("utf-8")

                st.download_button(
                    "⬇ Download Prediction Results",
                    csv,
                    file_name="prediction_results.csv",
                    mime="text/csv"
                )

# -----------------------------
# About
# -----------------------------
else:

    st.title("ℹ️ About the Project")

    st.markdown("---")

    st.subheader("Project Overview")

    st.write("""
The Insider Threat Detection System is a machine learning application
designed to identify potentially malicious employees based on behavioral data.

The system analyzes employee activities such as:

- Logon Activity
- Device Usage
- Email Behaviour
- File Operations
- HTTP Activity
- Psychometric Features

to predict insider threats.
""")

    st.markdown("---")

    st.subheader("Machine Learning Model")

    model_info = pd.DataFrame(
        model_info_rows,
        columns=["Attribute", "Value"]
    )

    st.table(model_info)

    st.markdown("---")

    st.subheader("Project Workflow")

    workflow = [
        "Dataset Collection",
        "Feature Engineering",
        "Data Preprocessing",
        "Model Training",
        "Model Evaluation",
        "Explainable AI",
        "Deployment"
    ]

    workflow_df = pd.DataFrame({
        "Step": range(1, 8),
        "Process": workflow
    })

    st.table(workflow_df)

    st.markdown("---")

    st.subheader("Technologies Used")

    tech = pd.DataFrame({
        "Technology": [
            "Python",
            "Pandas",
            "NumPy",
            "Scikit-Learn",
            "Streamlit",
            "Matplotlib",
            "Joblib"
        ]
    })

    st.table(tech)

    st.markdown("---")

    st.subheader("Project Highlights")

    st.success("✔ Random Forest Machine Learning Model")
    st.success("✔ 47 Behavioural Features")
    st.success("✔ Batch CSV Prediction")
    st.success("✔ Risk Analysis")
    st.success("✔ Download Prediction Results")
    st.success("✔ Explainable AI")

    st.markdown("---")

    st.caption(
        "Developed as a B.Tech AI & ML Major Project"
    )
