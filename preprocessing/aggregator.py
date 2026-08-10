"""
=========================================================
Feature Aggregator
AI Insider Threat Detection System
---------------------------------------------------------
Maintains one behavioural profile per employee.
Every processor updates this object.

Author : Mohammed Mohsin
=========================================================
"""

from collections import defaultdict
import pandas as pd


class FeatureAggregator:

    def __init__(self):

        self.employees = defaultdict(self._default_profile)

    # -----------------------------------------------------
    # Default Employee Profile
    # -----------------------------------------------------

    @staticmethod
    def _default_profile():

        return {

            # -------------------------------
            # Employee Information
            # -------------------------------

            "department": None,
            "role": None,
            "business_unit": None,

            # -------------------------------
            # Login Features
            # -------------------------------

            "login_count": 0,
            "logoff_count": 0,
            "night_login_count": 0,
            "weekend_login_count": 0,
            "unique_pc_count": 0,

            "night_login_ratio": 0.0,
            "weekend_login_ratio": 0.0,
            "pc_switching_frequency": 0.0,

            # Internal (not saved)
            "_pc_set": set(),

            # -------------------------------
            # Device Features
            # -------------------------------

            "usb_connect_count": 0,
            "usb_disconnect_count": 0,
            "usb_total_activity": 0,
            "usb_connect_ratio": 0.0,

            # -------------------------------
            # File Features
            # -------------------------------

            "file_copy_count": 0,
            "avg_daily_file_copy": 0.0,
            "max_daily_file_copy": 0,

            "_daily_file_copy": defaultdict(int),

            # -------------------------------
            # Email Features
            # -------------------------------

            "email_sent_count": 0,
            "external_email_count": 0,
            "avg_attachment_count": 0.0,
            "avg_email_size": 0.0,
            "external_email_ratio": 0.0,

            "_attachment_sum": 0,
            "_email_size_sum": 0,

            # -------------------------------
            # HTTP Features
            # -------------------------------

            "website_visit_count": 0,
            "unique_domain_count": 0,
            "avg_daily_web_activity": 0.0,

            "_domains": set(),
            "_daily_web": defaultdict(int),

            # -------------------------------
            # Psychometric
            # -------------------------------

            "O": 0,
            "C": 0,
            "E": 0,
            "A": 0,
            "N": 0,

            # -------------------------------
            # Target
            # -------------------------------

            "threat_label": 0

        }

    # -----------------------------------------------------
    # Get Employee
    # -----------------------------------------------------

    def get(self, user):

        return self.employees[user]

    # -----------------------------------------------------
    # Final Calculations
    # -----------------------------------------------------

    def finalize(self):

        for user, emp in self.employees.items():

            # -----------------------------
            # Unique PCs
            # -----------------------------

            emp["unique_pc_count"] = len(emp["_pc_set"])

            # -----------------------------
            # Ratios
            # -----------------------------

            if emp["login_count"] > 0:

                emp["night_login_ratio"] = round(

                    emp["night_login_count"]
                    /
                    emp["login_count"],

                    4

                )

                emp["weekend_login_ratio"] = round(

                    emp["weekend_login_count"]
                    /
                    emp["login_count"],

                    4

                )

                emp["pc_switching_frequency"] = round(

                    emp["unique_pc_count"]
                    /
                    emp["login_count"],

                    4

                )

            # -----------------------------
            # USB
            # -----------------------------

            emp["usb_total_activity"] = (

                emp["usb_connect_count"]

                +

                emp["usb_disconnect_count"]

            )

            if emp["usb_total_activity"] > 0:

                emp["usb_connect_ratio"] = round(

                    emp["usb_connect_count"]

                    /

                    emp["usb_total_activity"],

                    4

                )

            # -----------------------------
            # Email
            # -----------------------------

            if emp["email_sent_count"] > 0:

                emp["avg_attachment_count"] = round(

                    emp["_attachment_sum"]

                    /

                    emp["email_sent_count"],

                    2

                )

                emp["avg_email_size"] = round(

                    emp["_email_size_sum"]

                    /

                    emp["email_sent_count"],

                    2

                )

                emp["external_email_ratio"] = round(

                    emp["external_email_count"]

                    /

                    emp["email_sent_count"],

                    4

                )

            # -----------------------------
            # Daily File Activity
            # -----------------------------

            if len(emp["_daily_file_copy"]) > 0:

                values = list(

                    emp["_daily_file_copy"].values()

                )

                emp["avg_daily_file_copy"] = round(

                    sum(values)

                    /

                    len(values),

                    2

                )

                emp["max_daily_file_copy"] = max(values)

            # -----------------------------
            # Daily Web Activity
            # -----------------------------

            emp["unique_domain_count"] = len(

                emp["_domains"]

            )

            if len(emp["_daily_web"]) > 0:

                values = list(

                    emp["_daily_web"].values()

                )

                emp["avg_daily_web_activity"] = round(

                    sum(values)

                    /

                    len(values),

                    2

                )

            # -----------------------------
            # Remove Internal Fields
            # -----------------------------

            del emp["_pc_set"]
            del emp["_daily_file_copy"]
            del emp["_attachment_sum"]
            del emp["_email_size_sum"]
            del emp["_domains"]
            del emp["_daily_web"]

    # -----------------------------------------------------
    # Convert to DataFrame
    # -----------------------------------------------------

    def to_dataframe(self):

        self.finalize()

        rows = []

        for user, values in self.employees.items():

            row = {"user": user}

            row.update(values)

            rows.append(row)

        return pd.DataFrame(rows)

    # -----------------------------------------------------
    # Save CSV
    # -----------------------------------------------------

    def save(self, path):

        df = self.to_dataframe()

        df.sort_values(

            by="user",

            inplace=True

        )

        df.to_csv(

            path,

            index=False

        )

        print()

        print("=" * 60)
        print("Employee Feature Dataset Generated")
        print("=" * 60)
        print(f"Employees : {len(df)}")
        print(f"Saved To  : {path}")
        print("=" * 60)