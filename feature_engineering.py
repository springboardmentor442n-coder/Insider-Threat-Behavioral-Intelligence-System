import pandas as pd

def _logon_features(logon):
    logon["day"] = logon["date"].dt.date
    logon["hour"] = logon["date"].dt.hour
    logon["is_off_hours"] = ((logon["hour"] < 7) | (logon["hour"] >= 18)).astype(int)
    return logon.groupby(["user", "day"]).agg(
        logon_count=("activity", lambda x: (x == "Logon").sum()),
        off_hours_logons=("is_off_hours", "sum"),
        distinct_pcs=("pc", "nunique")
    ).reset_index()

def _device_features(device):
    device["day"] = device["date"].dt.date
    device["hour"] = device["date"].dt.hour
    connects = device[device["activity"] == "Connect"].copy()
    connects["is_off_hours"] = ((connects["hour"] < 7) | (connects["hour"] >= 18)).astype(int)
    return connects.groupby(["user", "day"]).agg(
        usb_connects=("activity", "count"),
        off_hours_usb=("is_off_hours", "sum")
    ).reset_index()

def _file_features(file_df):
    file_df["day"] = file_df["date"].dt.date
    file_df["is_sensitive"] = file_df["filename"].str.contains(
        r'\.doc|\.pdf|\.zip', case=False, na=False
    ).astype(int)
    return file_df.groupby(["user", "day"]).agg(
        files_copied_to_usb=("filename", "count"),
        sensitive_files_to_usb=("is_sensitive", "sum")
    ).reset_index()

def _email_features(email):
    email["day"] = email["date"].dt.date
    email["is_external"] = (~email["to"].str.contains("dtaa.com", case=False, na=False)).astype(int)
    email["attachment_count"] = pd.to_numeric(email.get("attachments", 0), errors="coerce").fillna(0)
    return email.groupby(["user", "day"]).agg(
        total_emails_sent=("date", "count"),
        external_emails_sent=("is_external", "sum"),
        total_attachments=("attachment_count", "sum"),
        total_email_size=("size", "sum")
    ).reset_index()

def _http_features(http):
    http["day"] = http["date"].dt.date
    http["is_cloud_or_job"] = http["url"].str.contains(
        "dropbox|drive|monster|linkedin", case=False, na=False
    ).astype(int)
    return http.groupby(["user", "day"]).agg(
        http_requests=("date", "count"),
        cloud_job_visits=("is_cloud_or_job", "sum")
    ).reset_index()

def engineer_features(logon, device, file_df, email, http):
    for df in [logon, device, file_df, email, http]:
        df["date"] = pd.to_datetime(df["date"])
    combined = _logon_features(logon)
    for feat_func, df in [(_device_features, device), (_file_features, file_df), (_email_features, email)]:
        combined = combined.merge(feat_func(df), on=["user", "day"], how="outer")
    combined = combined.merge(_http_features(http), on=["user", "day"], how="outer")
    numeric_cols = combined.columns.difference(["user", "day"])
    combined[numeric_cols] = combined[numeric_cols].fillna(0)
    return combined

def attach_ldap_context(combined, ldap_df, le_dict):
    ldap_df = ldap_df.rename(columns={'user_id': 'user'})
    combined['day'] = pd.to_datetime(combined['day'])
    combined['month_year'] = combined['day'].dt.strftime('%Y-%m')
    combined = pd.merge(combined, ldap_df, on=['user', 'month_year'], how='left')
    for col in ['role', 'department', 'team', 'supervisor']:
        combined[col] = combined[col].fillna('Unknown').astype(str)
        le = le_dict[col]
        combined[col] = combined[col].apply(lambda x: x if x in le.classes_ else 'Unknown')
        combined[f"{col}_encoded"] = le.transform(combined[col])
    combined.drop(columns=['role', 'department', 'team', 'supervisor', 'month_year'], inplace=True)
    return combined





#output
