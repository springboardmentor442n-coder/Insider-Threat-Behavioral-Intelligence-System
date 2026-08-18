import polars as pl
import glob
import json
import joblib
from pathlib import Path

def count_unique_users():
    results = {}
    
    # Raw Datasets
    raw_files = glob.glob('datasets/raw/*.csv')
    for f in raw_files:
        try:
            # We assume the column is either 'user' or 'user_id' based on typical names
            df = pl.scan_csv(f)
            cols = df.collect_schema().names()
            user_col = 'user' if 'user' in cols else 'user_id' if 'user_id' in cols else None
            
            if user_col:
                count = df.select(user_col).unique().collect().shape[0]
                results[f'RAW {Path(f).name}'] = (count, user_col)
            else:
                results[f'RAW {Path(f).name}'] = ('No user col', 'None')
        except Exception as e:
            results[f'RAW {Path(f).name}'] = (f"Error: {e}", "None")
            
    # Processed Datasets
    processed_files = glob.glob('datasets/processed/*.csv')
    for f in processed_files:
        try:
            df = pl.scan_csv(f)
            cols = df.collect_schema().names()
            user_col = 'user' if 'user' in cols else 'user_id' if 'user_id' in cols else None
            
            if user_col:
                count = df.select(user_col).unique().collect().shape[0]
                results[f'PROCESSED {Path(f).name}'] = (count, user_col)
            else:
                results[f'PROCESSED {Path(f).name}'] = ('No user col', 'None')
        except Exception as e:
            results[f'PROCESSED {Path(f).name}'] = (f"Error: {e}", "None")
            
    # Employees JSON
    try:
        with open('frontend/src/employees.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        results['employees.json'] = (len(data), 'N/A')
    except Exception as e:
        results['employees.json'] = (f"Error: {e}", "N/A")
        
    # Model
    try:
        model = joblib.load('ml/models/isolation_forest.pkl')
        if hasattr(model, 'n_samples_fit_'):
            results['isolation_forest.pkl'] = (model.n_samples_fit_, 'N/A')
        else:
            results['isolation_forest.pkl'] = ('Unknown', 'N/A')
    except Exception as e:
        results['isolation_forest.pkl'] = (f"Error: {e}", "N/A")

    for k, (v, col) in sorted(results.items()):
        print(f"{k} | {v} | {col}")

if __name__ == '__main__':
    count_unique_users()
