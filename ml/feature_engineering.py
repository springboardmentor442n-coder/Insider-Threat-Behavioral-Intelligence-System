import pandas as pd
from pathlib import Path


def generate_features(input_file, output_file):

    print("=" * 50)
    print("FEATURE ENGINEERING")
    print("=" * 50)

    df = pd.read_csv(input_file)

    # One row per employee
    features = df.groupby("user").agg(

        login_count=("user", "count"),

        unique_pc_count=("pc", "nunique"),

        weekend_logins=("day", lambda x: x.isin(["Saturday", "Sunday"]).sum()),

        after_hours_logins=("hour", lambda x: ((x >= 22) | (x <= 5)).sum()),

        average_login_hour=("hour", "mean"),

        first_login=("hour", "min"),

        last_login=("hour", "max")

    ).reset_index()

    features.rename(
        columns={"user": "employee_id"},
        inplace=True
    )

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    features.to_csv(output_file, index=False)

    print(f"Saved feature dataset to {output_file}")

    return output_file