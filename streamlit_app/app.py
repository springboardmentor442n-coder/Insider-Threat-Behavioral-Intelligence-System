import warnings
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

warnings.filterwarnings("ignore", category=UserWarning)

# -----------------------------
# App configuration
# -----------------------------
st.set_page_config(
    page_title="Insider Threat Behavioral Intelligence System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Constants and metadata
# -----------------------------
FEATURE_COLUMNS = [
    "http_count",
    "unique_url",
    "after_hours_activity",
    "weekend_activity",
    "logon_count",
    "unique_pc",
    "device_count",
    "file_count",
    "unique_files",
    "email_count",
    "unique_receivers",
    "total_attachment",
]

CLASS_LABELS = {0: "Normal User", 1: "Insider Threat"}
APP_TITLE = "Insider Threat Behavioral Intelligence System"
APP_SUBTITLE = "Behavioral intelligence for proactive insider-threat monitoring"

CUSTOM_CSS = """
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
        color: #0f172a;
    }
    .stSidebar {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
        border-right: 1px solid rgba(15, 23, 42, 0.08);
    }
    .stSidebar .block-container {
        padding-top: 0.8rem;
    }
    .stButton > button {
        border-radius: 10px;
        background: linear-gradient(90deg, #2563eb, #3b82f6);
        color: white;
        border: none;
        font-weight: 600;
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.18);
    }
    .hero-card {
        padding: 1.3rem 1.4rem;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(15, 23, 42, 0.08);
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
        margin-bottom: 1rem;
    }
    .info-pill {
        display: inline-block;
        padding: 0.38rem 0.7rem;
        border-radius: 999px;
        background: rgba(37, 99, 235, 0.1);
        color: #1d4ed8;
        font-size: 0.92rem;
        margin-right: 0.4rem;
        margin-bottom: 0.45rem;
    }
    .section-card {
        padding: 1rem 1.1rem;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid rgba(15, 23, 42, 0.08);
        margin-bottom: 0.9rem;
    }
    .prediction-card {
        padding: 1.15rem 1.2rem;
        border-radius: 14px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .footer-note {
        text-align: center;
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 1.2rem;
        padding-top: 0.7rem;
        border-top: 1px solid rgba(15, 23, 42, 0.08);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading the trained model...")
def load_model():
    """Load the pre-trained Random Forest model from disk."""
    base_dir = Path(__file__).resolve().parent.parent
    model_path = base_dir / "models" / "insider_threat_model.pkl"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model file not found at {model_path}. Please ensure the trained model exists."
        )

    try:
        return joblib.load(model_path)
    except Exception as exc:
        raise RuntimeError(f"Unable to load model: {exc}") from exc


def validate_inputs(values):
    """Validate all numeric inputs and ensure they are non-negative."""
    for key, value in values.items():
        if value is None:
            raise ValueError(f"{key} is required.")
        if value < 0:
            raise ValueError(f"{key} must be a non-negative number.")
    return values


def build_prediction_frame(values):
    """Create a DataFrame in the exact feature order expected by the model."""
    return pd.DataFrame([values], columns=FEATURE_COLUMNS)


def render_sidebar():
    """Render a tidy and informative sidebar navigation."""
    with st.sidebar:
        st.title("🛡️ Security Command Center")
        st.caption(APP_SUBTITLE)
        st.markdown("---")

        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "home"
        if st.button("🧠 Make Prediction", use_container_width=True):
            st.session_state.page = "prediction"

        st.markdown("---")
        st.subheader("📌 Project Overview")
        st.write("- **Algorithm:** Random Forest Classifier")
        st.write("- **Model Source:** Existing joblib artifact in the models folder")
        st.write("- **Features:** HTTP, logon, device, file, and email behavior")
        st.write("- **Developer:** Poornima Devi Kallempudi")
        st.markdown("---")
        st.caption("The model is loaded directly from the trained joblib artifact and is not retrained during runtime.")


def render_home_page():
    """Render the landing page with a clearer product-style overview."""
    st.markdown(
        f"<div class='hero-card'><h1 style='margin-bottom:0.25rem;'>{APP_TITLE}</h1>"
        f"<p style='color:#475569; margin-top:0.2rem;'>{APP_SUBTITLE}</p></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='hero-card'>"
        "<span class='info-pill'>⚡ Real-time risk scoring</span>"
        "<span class='info-pill'>📊 Feature-driven analysis</span>"
        "<span class='info-pill'>🧠 Pre-trained Random Forest model</span>"
        "<span class='info-pill'>🔍 SHAP insights</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns(2)
    with left_col:
        st.markdown(
            "<div class='section-card'><h4>🎯 Objective</h4><p>This dashboard helps security teams evaluate employee behavior patterns and flag potentially risky activity using a trusted model.</p></div>",
            unsafe_allow_html=True,
        )
    with right_col:
        st.markdown(
            "<div class='section-card'><h4>🛠️ What you can do</h4><p>Review predictions, inspect confidence scores, examine feature importance, and interpret outputs with SHAP support.</p></div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div class='section-card'><h4>📋 How it works</h4><ol><li>Open the prediction page.</li><li>Enter employee activity metrics.</li><li>Click predict to review the outcome and supporting insights.</li></ol></div>",
        unsafe_allow_html=True,
    )

    st.info("Use the sidebar to move into the prediction workflow when you are ready.")


def render_prediction_result(model, sample_df):
    """Render prediction result cards and supporting model insights."""
    try:
        prediction = int(model.predict(sample_df)[0])
        probabilities = model.predict_proba(sample_df)[0]
        class_to_index = {int(class_label): idx for idx, class_label in enumerate(model.classes_)}
        confidence = float(max(probabilities) * 100)
        predicted_label = CLASS_LABELS.get(prediction, "Unknown")
        predicted_probability = float(probabilities[class_to_index.get(prediction, 0)] * 100)

        normal_user_probability = 0.0
        insider_threat_probability = 0.0

        if 0 in class_to_index:
            normal_user_probability = float(probabilities[class_to_index[0]] * 100)
        if 1 in class_to_index:
            insider_threat_probability = float(probabilities[class_to_index[1]] * 100)

        st.subheader("📈 Prediction Outcome")

        if prediction == 1:
            st.markdown(
                "<div class='prediction-card' style='background:linear-gradient(135deg,#dc2626,#ef4444);'>"
                "<h3>🚨 Insider Threat</h3>"
                "<p>High-risk behavior pattern detected for this employee.</p></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div class='prediction-card' style='background:linear-gradient(135deg,#059669,#10b981);'>"
                "<h3>✅ Normal User</h3>"
                "<p>No suspicious insider threat pattern identified.</p></div>",
                unsafe_allow_html=True,
            )

        metric_col_1, metric_col_2 = st.columns(2)
        metric_col_1.metric("Prediction", predicted_label, help="Model classification outcome")
        metric_col_2.metric("Confidence", f"{confidence:.2f}%", help="Highest class probability")

        prob_col_1, prob_col_2 = st.columns(2)
        prob_col_1.metric("Normal User Probability", f"{normal_user_probability:.2f}%", help="Probability assigned to the Normal User class")
        prob_col_2.metric("Insider Threat Probability", f"{insider_threat_probability:.2f}%", help="Probability assigned to the Insider Threat class")

        st.write("")
        st.progress(confidence / 100)
        st.caption("Prediction confidence score")

        st.subheader("📊 Feature Importance")
        importances = pd.DataFrame(
            {"Feature": FEATURE_COLUMNS, "Importance": model.feature_importances_}
        ).sort_values("Importance", ascending=False)
        st.dataframe(importances, use_container_width=True, hide_index=True)
        st.bar_chart(importances.set_index("Feature")["Importance"])

        st.subheader("🔍 SHAP Explanation")
        try:
            import shap
            import matplotlib.pyplot as plt

            explainer = shap.TreeExplainer(model)
            try:
                shap_values = explainer(sample_df)
            except TypeError:
                shap_values = explainer.shap_values(sample_df)

            fig, ax = plt.subplots(figsize=(10, 5))
            shap.summary_plot(shap_values, sample_df, plot_type="bar", ax=ax)
            st.pyplot(fig)
        except Exception as exc:
            st.info(f"SHAP explanation could not be generated: {exc}")

    except Exception as exc:
        st.error(f"Prediction failed: {exc}")


def render_prediction_page():
    """Render the prediction workflow with a cleaner form layout."""
    st.markdown(
        "<div class='hero-card'><h2 style='margin-bottom:0.2rem;'>🧠 Employee Behaviour Prediction</h2>"
        "<p style='color:#475569; margin-top:0.2rem;'>Enter behavioral telemetry to classify the employee as either a normal user or a potential insider threat.</p></div>",
        unsafe_allow_html=True,
    )

    try:
        model = load_model()
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    st.subheader("📝 Behavioral Input Features")

    left_col, right_col = st.columns(2)
    with left_col:
        http_count = st.number_input("HTTP Count", min_value=0, value=0, step=1)
        unique_url = st.number_input("Unique URLs", min_value=0, value=0, step=1)
        after_hours_activity = st.number_input("After Hours Activity", min_value=0, value=0, step=1)
        weekend_activity = st.number_input("Weekend Activity", min_value=0, value=0, step=1)
        logon_count = st.number_input("Logon Count", min_value=0, value=0, step=1)
        unique_pc = st.number_input("Unique PCs", min_value=0, value=0, step=1)

    with right_col:
        device_count = st.number_input("Device Count", min_value=0, value=0, step=1)
        file_count = st.number_input("File Count", min_value=0, value=0, step=1)
        unique_files = st.number_input("Unique Files", min_value=0, value=0, step=1)
        email_count = st.number_input("Email Count", min_value=0, value=0, step=1)
        unique_receivers = st.number_input("Unique Receivers", min_value=0, value=0, step=1)
        total_attachment = st.number_input("Total Attachment", min_value=0, value=0, step=1)

    if st.button("Predict Employee Risk", type="primary", use_container_width=True):
        raw_values = {
            "http_count": http_count,
            "unique_url": unique_url,
            "after_hours_activity": after_hours_activity,
            "weekend_activity": weekend_activity,
            "logon_count": logon_count,
            "unique_pc": unique_pc,
            "device_count": device_count,
            "file_count": file_count,
            "unique_files": unique_files,
            "email_count": email_count,
            "unique_receivers": unique_receivers,
            "total_attachment": total_attachment,
        }

        try:
            values = validate_inputs(raw_values)
            sample_df = build_prediction_frame(values)
            with st.spinner("Generating prediction insights..."):
                render_prediction_result(model, sample_df)
        except ValueError as exc:
            st.error(f"Invalid input detected: {exc}")
        except Exception as exc:
            st.error(f"An unexpected error occurred: {exc}")


def render_footer():
    """Render a small footer for a more complete app experience."""
    st.markdown("---")
    st.markdown(
        "<div class='footer-note'>Built with Streamlit • Pre-trained Random Forest model • No retraining performed at runtime</div>",
        unsafe_allow_html=True,
    )


# -----------------------------
# App entry point
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"

render_sidebar()

if st.session_state.page == "home":
    render_home_page()
else:
    render_prediction_page()

render_footer()