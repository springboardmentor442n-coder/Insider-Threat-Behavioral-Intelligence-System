import pandas as pd
import os

DATASET = "dataset/raw"

FILES = [
    "logon.csv",
    "device.csv",
    "file.csv",
    "email.csv",
    "http.csv",
    "psychometric.csv"
]

for file in FILES:

    print("=" * 80)
    print(file)

    df = pd.read_csv(
        os.path.join(DATASET, file),
        nrows=5
    )

    print()

    print("Columns")

    print(df.columns.tolist())

    print()

    print(df.head())

print("=" * 80)

print("LDAP")

ldap = os.path.join(DATASET, "LDAP")

for f in sorted(os.listdir(ldap)):

    if f.endswith(".csv"):

        print()

        print(f)

        df = pd.read_csv(

            os.path.join(ldap, f),

            nrows=5

        )

        print(df.columns.tolist())

        print(df.head())

        break

print("=" * 80)

print("ANSWERS")

answers = os.path.join(DATASET, "answers")

for f in sorted(os.listdir(answers)):

    if f.endswith(".csv"):

        print()

        print(f)

        df = pd.read_csv(

            os.path.join(answers, f),

            nrows=5

        )

        print(df.columns.tolist())

        print(df.head())