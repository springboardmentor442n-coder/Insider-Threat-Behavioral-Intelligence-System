"""
=========================================================
Preprocessing Pipeline
AI Insider Threat Detection System
=========================================================
"""

from aggregator import FeatureAggregator

from login_processor import LoginProcessor
from device_processor import DeviceProcessor
from file_processor import FileProcessor
from email_processor import EmailProcessor
from http_processor import HttpProcessor
from psychometric_processor import PsychometricProcessor
from ldap_processor import LDAPProcessor

from dataset_config import EMPLOYEE_FEATURES
import pandas as pd
from dataset_config import EMPLOYEE_FEATURES

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ANSWERS_FILE = os.path.join(
    BASE_DIR,
    "dataset",
    "raw",
    "answers",
    "insiders.csv"
)


def assign_labels(aggregator):

    print()
    print("=" * 60)
    print("Assigning Threat Labels")
    print("=" * 60)
    print(ANSWERS_FILE)

    answers = pd.read_csv(ANSWERS_FILE)

    insider_users = set(

        answers["user"]

        .astype(str)

        .str.upper()

        .str.strip()

    )

    count = 0

    for user, employee in aggregator.employees.items():

        if user.upper() in insider_users:

            employee["threat_label"] = 1
            count += 1

        else:

            employee["threat_label"] = 0

    print(f"Insider Users : {count}")

def main():

    print()

    print("=" * 70)
    print("AI INSIDER THREAT DETECTION SYSTEM")
    print("PREPROCESSING PIPELINE")
    print("=" * 70)

    aggregator = FeatureAggregator()

    LoginProcessor(

        aggregator

    ).run()

    DeviceProcessor(

        aggregator

    ).run()

    FileProcessor(

        aggregator

    ).run()

    EmailProcessor(

        aggregator

    ).run()

    HttpProcessor(

        aggregator

    ).run()

    PsychometricProcessor(

        aggregator

    ).run()

    LDAPProcessor(

        aggregator

    ).run()
    assign_labels(aggregator)

    aggregator.save(

        EMPLOYEE_FEATURES

    )

    print()

    print("=" * 70)
    print("PREPROCESSING FINISHED")
    print("=" * 70)


if __name__ == "__main__":

    main()