import os
import pandas as pd


def _load(cleaned_path, name):
    return pd.read_csv(os.path.join(cleaned_path, f"{name}_clean.csv"), parse_dates=["date"])


def _logon_features(logon):
    logon["day"] = logon["date"].dt.date
    logon["hour"] = logon["date"].dt.hour
    logon["is_off_hours"] = ((logon["hour"] < 7) | (logon["hour"] >= 19)).astype(int)
    grouped = logon.groupby(["user", "day"]).agg(
        logon_count=("activity", lambda x: (x == "Logon").sum()),
        logoff_count=("activity", lambda x: (x == "Logoff").sum()),
        off_hours_logons=("is_off_hours", "sum"),
        distinct_pcs=("pc", "nunique"),
    ).reset_index()
    return grouped


def _device_features(device):
    device["day"] = device["date"].dt.date
    grouped = device.groupby(["user", "day"]).agg(
        device_connects=("activity", lambda x: (x == "Connect").sum()),
        device_disconnects=("activity", lambda x: (x == "Disconnect").sum()),
    ).reset_index()
    return grouped


def _email_features(email):
    email["day"] = email["date"].dt.date
    agg_dict = {"email_count": ("date", "count")}
    if "size" in email.columns:
        agg_dict["total_email_size"] = ("size", "sum")
        agg_dict["avg_email_size"] = ("size", "mean")
    if "attachments" in email.columns:
        agg_dict["total_attachments"] = ("attachments", "sum")
    grouped = email.groupby(["user", "day"]).agg(**agg_dict).reset_index()
    return grouped


def _file_features(file_df):
    file_df["day"] = file_df["date"].dt.date
    agg_dict = {"file_activity_count": ("date", "count")}
    if "to_removable_media" in file_df.columns:
        agg_dict["files_to_removable"] = ("to_removable_media", lambda x: (x == "True").sum() if x.dtype == object else x.sum())
    if "from_removable_media" in file_df.columns:
        agg_dict["files_from_removable"] = ("from_removable_media", lambda x: (x == "True").sum() if x.dtype == object else x.sum())
    grouped = file_df.groupby(["user", "day"]).agg(**agg_dict).reset_index()
    return grouped


def _http_features(http):
    http["day"] = http["date"].dt.date
    agg_dict = {"http_request_count": ("date", "count")}
    if "url" in http.columns:
        agg_dict["distinct_urls"] = ("url", "nunique")
    grouped = http.groupby(["user", "day"]).agg(**agg_dict).reset_index()
    return grouped


def build_features(cleaned_path, verbose=True):
    if verbose:
        print("Loading cleaned files...")
    logon = _load(cleaned_path, "logon")
    device = _load(cleaned_path, "device")
    email = _load(cleaned_path, "email")
    file_df = _load(cleaned_path, "file")
    http = _load(cleaned_path, "http")

    if verbose:
        print("Building features per source...")
    logon_feat = _logon_features(logon)
    device_feat = _device_features(device)
    email_feat = _email_features(email)
    file_feat = _file_features(file_df)
    http_feat = _http_features(http)

    if verbose:
        print("Merging all features into one table...")
    features = logon_feat
    for feat in [device_feat, email_feat, file_feat, http_feat]:
        features = features.merge(feat, on=["user", "day"], how="outer")

    numeric_cols = features.columns.difference(["user", "day"])
    features[numeric_cols] = features[numeric_cols].fillna(0)
    features = features.sort_values(["user", "day"]).reset_index(drop=True)

    if verbose:
        print(f"\nFinal feature table: {features.shape[0]} user-days, {features.shape[1]} columns")
        print("Columns:", list(features.columns))
    return features


features = build_features(cleaned_path="/kaggle/working/cleaned/")
features.to_csv("/kaggle/working/features.csv", index=False)


# done Loading cleaned files...
# Building features per source...
# Merging all features into one table...

# Final feature table: 330452 user-days, 15 columns
# Columns: ['user', 'day', 'logon_count', 'logoff_count', 'off_hours_logons', 'distinct_pcs', 'device_connects', 'device_disconnects', 'email_count', 'total_email_size', 'avg_email_size', 'total_attachments', 'file_activity_count', 'http_request_count', 'distinct_urls']
