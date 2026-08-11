import pandas as pd
import numpy as np
from typing import Dict, Optional

class CERTRawAggregatorService:
    """
    Application-side CERT r4.2 raw log aggregator.
    Converts raw logon.csv, device.csv, file.csv, email.csv, http.csv into 
    the exact 19 daily behavioral feature schema used by Notebook 01/02.
    """

    @staticmethod
    def process_raw_logs(
        logon_df: Optional[pd.DataFrame] = None,
        device_df: Optional[pd.DataFrame] = None,
        file_df: Optional[pd.DataFrame] = None,
        email_df: Optional[pd.DataFrame] = None,
        http_df: Optional[pd.DataFrame] = None,
        company_domain: str = "@doolittle.com"
    ) -> pd.DataFrame:
        user_days = set()

        # Helper to extract date string YYYY-MM-DD
        def prep_df(df, date_col='date'):
            if df is not None and not df.empty and date_col in df.columns:
                df['dt'] = pd.to_datetime(df[date_col], errors='coerce')
                df['day'] = df['dt'].dt.strftime('%Y-%m-%d')
                df['hour'] = df['dt'].dt.hour
                return df
            return None

        logon_df = prep_df(logon_df)
        device_df = prep_df(device_df)
        file_df = prep_df(file_df)
        email_df = prep_df(email_df)
        http_df = prep_df(http_df)

        for df in [logon_df, device_df, file_df, email_df, http_df]:
            if df is not None and 'user' in df.columns and 'day' in df.columns:
                user_days.update(zip(df['user'], df['day']))

        if not user_days:
            return pd.DataFrame()

        base_df = pd.DataFrame(list(user_days), columns=['user', 'day'])

        # 1. Logon Features
        if logon_df is not None:
            logon_grp = logon_df.groupby(['user', 'day'])
            logon_feats = logon_grp.agg(
                logon_count=('activity', lambda x: (x == 'Logon').sum()),
                logoff_count=('activity', lambda x: (x == 'Logoff').sum()),
                off_hours_logons=('hour', lambda x: ((x < 8) | (x > 18)).sum()),
                unique_pcs=('pc', 'nunique')
            ).reset_index()
            base_df = base_df.merge(logon_feats, on=['user', 'day'], how='left')
        else:
            for col in ['logon_count', 'logoff_count', 'off_hours_logons', 'unique_pcs']:
                base_df[col] = 0

        # 2. Device Features
        if device_df is not None:
            dev_grp = device_df.groupby(['user', 'day'])
            dev_feats = dev_grp.agg(
                device_connects=('activity', lambda x: (x == 'Connect').sum()),
                device_disconnects=('activity', lambda x: (x == 'Disconnect').sum()),
                unique_device_pcs=('pc', 'nunique')
            ).reset_index()
            base_df = base_df.merge(dev_feats, on=['user', 'day'], how='left')
        else:
            for col in ['device_connects', 'device_disconnects', 'unique_device_pcs']:
                base_df[col] = 0

        # 3. File Features
        if file_df is not None:
            file_grp = file_df.groupby(['user', 'day'])
            file_feats = file_grp.agg(
                file_activity_count=('filename', 'count'),
                unique_file_pcs=('pc', 'nunique'),
                unique_files=('filename', 'nunique'),
                sensitive_file_count=('filename', lambda x: x.astype(str).str.contains(r'\.(doc|pdf|xls|zip|exe|key)$', case=False, na=False).sum())
            ).reset_index()
            base_df = base_df.merge(file_feats, on=['user', 'day'], how='left')
        else:
            for col in ['file_activity_count', 'unique_file_pcs', 'unique_files', 'sensitive_file_count']:
                base_df[col] = 0

        # 4. Email Features
        if email_df is not None:
            email_grp = email_df.groupby(['user', 'day'])
            email_feats = email_grp.agg(
                email_count=('user', 'count'),
                attachment_count=('attachment_count', 'sum') if 'attachment_count' in email_df.columns else ('user', lambda x: 0),
                total_email_size=('size', 'sum') if 'size' in email_df.columns else ('user', lambda x: 0),
                unique_email_pcs=('pc', 'nunique'),
                external_email_count=('to', lambda x: (~x.astype(str).str.contains(company_domain, case=False, na=False)).sum()) if 'to' in email_df.columns else ('user', lambda x: 0)
            ).reset_index()
            base_df = base_df.merge(email_feats, on=['user', 'day'], how='left')
        else:
            for col in ['email_count', 'attachment_count', 'total_email_size', 'unique_email_pcs', 'external_email_count']:
                base_df[col] = 0

        # 5. HTTP Features
        if http_df is not None:
            http_grp = http_df.groupby(['user', 'day'])
            http_feats = http_grp.agg(
                http_request_count=('url', 'count'),
                unique_http_urls=('url', 'nunique'),
                off_hours_http=('hour', lambda x: ((x < 8) | (x > 18)).sum())
            ).reset_index()
            base_df = base_df.merge(http_feats, on=['user', 'day'], how='left')
        else:
            for col in ['http_request_count', 'unique_http_urls', 'off_hours_http']:
                base_df[col] = 0

        feature_cols = [
            "logon_count", "logoff_count", "off_hours_logons", "unique_pcs",
            "device_connects", "device_disconnects", "unique_device_pcs",
            "file_activity_count", "unique_file_pcs", "unique_files", "sensitive_file_count",
            "email_count", "attachment_count", "total_email_size", "unique_email_pcs", "external_email_count",
            "http_request_count", "unique_http_urls", "off_hours_http"
        ]

        base_df[feature_cols] = base_df[feature_cols].fillna(0)
        return base_df

cert_aggregator = CERTRawAggregatorService()
