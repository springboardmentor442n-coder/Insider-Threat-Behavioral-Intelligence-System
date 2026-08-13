import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Insider Threat Detection", layout="wide")

API_URL = "http://localhost:8000"  # change if backend runs elsewhere

st.title("🛡️ Insider Threat Behavioral Intelligence System")
st.markdown("Upload one or more activity log CSVs (logon, device, email, file, or http format) to detect anomalous behavior.")

uploaded_files = st.file_uploader(
    "Upload CSV file(s)", type="csv", accept_multiple_files=True
)

if uploaded_files:
    if st.button("Analyze"):
        with st.spinner("Analyzing uploaded logs..."):
            files_payload = [
                ("files", (f.name, f.getvalue(), "text/csv")) for f in uploaded_files
            ]
            try:
                response = requests.post(f"{API_URL}/analyze", files=files_payload)
                response.raise_for_status()
                data = response.json()
            except Exception as e:
                st.error(f"Failed to reach backend: {e}")
                st.stop()

        st.success(f"Analyzed {data['total_user_days_scored']} user-days across {len(data['files_processed'])} file(s)")

        st.subheader("Files Processed")
        st.table(pd.DataFrame(data["files_processed"]))

        results_df = pd.DataFrame(data["all_results"])
        results_df["risk_score"] = results_df["risk_score"].astype(float)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Scored", data["total_user_days_scored"])
        col2.metric("Flagged (High/Critical)", data["flagged_count"])
        col3.metric("Highest Risk Score", f"{results_df['risk_score'].max():.1f}")

        st.subheader("Risk Category Distribution")
        st.bar_chart(results_df["risk_category"].value_counts())

        st.subheader("All Results (sorted by risk)")

        def highlight_risk(row):
            colors = {"Critical": "#ff4b4b", "High": "#ffa64b", "Medium": "#ffe14b", "Low": "#4bff88"}
            return [f"background-color: {colors.get(row['risk_category'], '')}"] * len(row)

        st.dataframe(
            results_df.style.apply(highlight_risk, axis=1),
            use_container_width=True,
            height=500,
        )

        st.download_button(
            "Download Full Report (CSV)",
            results_df.to_csv(index=False),
            file_name="insider_threat_report.csv",
            mime="text/csv",
        )
else:
    st.info("Upload a CSV to get started. You can upload multiple files (e.g., logon.csv + device.csv) for a more complete analysis.")