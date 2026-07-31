import pandas as pd
from pathlib import Path


def generate_features(input_file, output_file=None):

    print("=" * 50)
    print("FEATURE ENGINEERING")
    print("=" * 50)

    df = pd.read_csv(input_file)

    features = (
        df.groupby("user")
        .agg(
            login_count=("user", "count"),
            unique_pc_count=("pc", "nunique"),
            weekend_logins=("day", lambda x: x.isin(["Saturday", "Sunday"]).sum()),
            after_hours_logins=("hour", lambda x: ((x >= 22) | (x <= 5)).sum()),
            average_login_hour=("hour", "mean"),
            first_login=("hour", "min"),
            last_login=("hour", "max"),
            latest_login_timestamp=("date", "max"),
        )
        .reset_index()
    )

    features.rename(
        columns={"user": "employee_id"},
        inplace=True
    )

    # Optional CSV output
    if output_file is not None:

        Path(output_file).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        features.to_csv(
            output_file,
            index=False
        )

        print(f"Saved feature dataset to {output_file}")

    return features