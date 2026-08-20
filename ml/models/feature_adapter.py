import pandas as pd


FEATURE_MAP = {
    "logon_count": "logon_count",
    "off_hours_logons": "off_hours_logons",
    "unique_pcs": "distinct_pcs",
    "device_connects": "usb_connects",
    "off_hours_usb": "off_hours_usb",
    "file_activity_count": "files_copied_to_usb",
    "sensitive_file_count": "sensitive_files_to_usb",
    "email_count": "total_emails_sent",
    "external_email_count": "external_emails_sent",
    "attachment_count": "total_attachments",
    "total_email_size": "total_email_size",
    "http_request_count": "http_requests",
    "off_hours_http": "cloud_job_visits",
}


def prepare_model_features(df):
    result = pd.DataFrame(index=df.index)

    for source_column, model_column in FEATURE_MAP.items():
        if source_column in df.columns:
            result[model_column] = pd.to_numeric(
                df[source_column],
                errors="coerce"
            ).fillna(0)
        else:
            result[model_column] = 0.0

    return result[
        [
            "logon_count",
            "off_hours_logons",
            "distinct_pcs",
            "usb_connects",
            "off_hours_usb",
            "files_copied_to_usb",
            "sensitive_files_to_usb",
            "total_emails_sent",
            "external_emails_sent",
            "total_attachments",
            "total_email_size",
            "http_requests",
            "cloud_job_visits",
        ]
    ]