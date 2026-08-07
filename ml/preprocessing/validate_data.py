"""
validate_data.py

Validates all datasets before preprocessing.
"""

from load_data import load_all_data


def validate():

    datasets = load_all_data()

    print("\n========== DATA VALIDATION ==========\n")

    for name, df in datasets.items():

        print(f"\nDataset : {name}")

        print("-" * 40)

        print(f"Rows      : {df.height}")
        print(f"Columns   : {df.width}")

        print("\nColumn Names:")

        print(df.columns)

        print("\nMissing Values:")

        print(df.null_count())

        print("\nFirst Five Rows:")

        print(df.head())

        print("=" * 50)


if __name__ == "__main__":

    validate()