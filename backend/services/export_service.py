from pathlib import Path
import tempfile
import zipfile

from backend.utils.config import REPORTS_DIR


def create_analytics_zip():

    report_files = [
        "model_performance.csv",
        "training_times.csv",
        "feature_statistics.csv",
        "risk_level_statistics.csv",
        "dataset_statistics.csv",
    ]

    zip_path = Path(tempfile.gettempdir()) / "Analytics_Report.zip"

    print("\n========== EXPORT ==========")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:

        for filename in report_files:

            file_path = REPORTS_DIR / filename

            print(file_path)
            print("Exists:", file_path.exists())

            if file_path.exists():
                archive.write(file_path, arcname=filename)
                print("Added")

    print("ZIP:", zip_path)
    print("ZIP Size:", zip_path.stat().st_size)

    return zip_path
