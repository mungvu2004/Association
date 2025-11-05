"""Minimal preprocessing script for optimized_routes_standard.csv

Performs small, safe cleaning steps and writes a cleaned CSV.

Output: algorithms/data/optimized_routes_standard_cleaned.csv
"""
import pandas as pd

# input / output
CSV = 'algorithms/data/optimized_routes_standard.csv'
OUT = 'algorithms/data/optimized_routes_standard_cleaned.csv'


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Apply lightweight preprocessing and return cleaned DataFrame."""
    # normalize column names (strip BOM and whitespace)
    df.columns = [c.strip().lstrip('\ufeff') for c in df.columns]

    # trim whitespace for object (string) columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].where(df[col].isna(), df[col].str.strip())

    # convert numeric columns
    for col in ('latitude', 'longitude', 'weight'):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # combine date + time into a single datetime (if possible)
    if 'delivery_date' in df.columns and 'delivery_time' in df.columns:
        df['delivery_datetime'] = pd.to_datetime(
            df['delivery_date'].astype(str).str.strip() + ' ' + df['delivery_time'].astype(str).str.strip(),
            errors='coerce')
        df['delivery_hour'] = df['delivery_datetime'].dt.hour

    # drop rows missing coords (essential for routing)
    before = len(df)
    if 'latitude' in df.columns and 'longitude' in df.columns:
        df = df.dropna(subset=['latitude', 'longitude'])
    dropped_coords = before - len(df)

    # fill missing weight with median (if weight exists)
    weight_filled = 0
    if 'weight' in df.columns:
        w_median = df['weight'].median()
        weight_filled = int(df['weight'].isna().sum())
        df['weight'] = df['weight'].fillna(w_median)

    # remove exact duplicate rows
    before_dups = len(df)
    df = df.drop_duplicates()
    removed_duplicates = before_dups - len(df)

    # filter obvious outliers in weight: keep 0 < weight <= 50
    if 'weight' in df.columns:
        before_out = len(df)
        df = df[(df['weight'] > 0) & (df['weight'] <= 50)]
        outlier_removed = before_out - len(df)
    else:
        outlier_removed = 0

    # reset index
    df = df.reset_index(drop=True)

    # attach some metadata as attributes (not necessary, but useful)
    df.attrs['preprocess_summary'] = {
        'dropped_missing_coords': int(dropped_coords),
        'filled_weight_with_median_count': int(weight_filled),
        'removed_duplicates': int(removed_duplicates),
        'removed_weight_outliers': int(outlier_removed),
        'final_row_count': len(df)
    }

    return df


def main():
    print('Loading', CSV)
    df = pd.read_csv(CSV, encoding='utf-8')
    original_rows = len(df)

    df_clean = preprocess(df)

    # save cleaned CSV
    df_clean.to_csv(OUT, index=False, encoding='utf-8')

    # print a short summary
    s = df_clean.attrs.get('preprocess_summary', {})
    print('Original rows:', original_rows)
    print('Final rows:', s.get('final_row_count', len(df_clean)))
    print('Dropped rows (missing coords):', s.get('dropped_missing_coords', 0))
    print('Filled weight NaNs with median (count):', s.get('filled_weight_with_median_count', 0))
    print('Removed duplicate rows:', s.get('removed_duplicates', 0))
    print('Removed weight outliers:', s.get('removed_weight_outliers', 0))
    print('Saved cleaned CSV to', OUT)


if __name__ == '__main__':
    main()
