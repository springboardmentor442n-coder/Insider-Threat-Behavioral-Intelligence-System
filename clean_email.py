import polars as pl

def clean_dataset(df: pl.DataFrame) -> pl.DataFrame:
    df = df.unique()
    columns = df.collect_schema().names()
    subset = []
    if "user" in columns:
        subset.append("user")
    if "user_id" in columns:
        subset.append("user_id")
    if subset:
        df = df.drop_nulls(subset=subset)
    return df

print("Loading email.csv...")
df = pl.read_csv("datasets/raw/email.csv")
print("Cleaning email.csv...")
cleaned = clean_dataset(df)
print("Saving email_cleaned.csv...")
cleaned.write_csv("datasets/processed/email_cleaned.csv")
print("Done!")
