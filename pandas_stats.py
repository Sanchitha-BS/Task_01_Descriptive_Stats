import ast
import pandas as pd
from pure_python_stats import numeric_stats, parse_container  # reuse for the verification step

CSV_PATH = "fb_ads_president_scored_anon.csv"

DICT_RANGE_COLUMNS = ["estimated_audience_size", "impressions", "spend"]
LIST_COLUMNS = ["publisher_platforms", "illuminating_mentions"]
DATE_COLUMNS = ["ad_creation_time", "ad_delivery_start_time", "ad_delivery_stop_time"]


def load_data():
    return pd.read_csv(CSV_PATH)


def show_structure(df):
    print("=" * 70)
    print("BASIC STRUCTURE")
    print("=" * 70)
    print(f"shape: {df.shape}  (rows, columns)\n")
    print("dtypes:")
    print(df.dtypes)
    print("\ninfo():")
    df.info()


def show_missing(df):
    print("\n" + "=" * 70)
    print("MISSING VALUES PER COLUMN")
    print("=" * 70)
    missing = df.isna().sum()
    pct = (missing / len(df) * 100).round(2)
    report = pd.DataFrame({"missing": missing, "pct": pct})
    print(report[report["missing"] >= 0])  # show every column, including zero-missing


def show_describe(df):
    print("\n" + "=" * 70)
    print("DataFrame.describe() -- NUMERIC COLUMNS")
    print("=" * 70)
    print(df.describe())

    print("\n" + "=" * 70)
    print("DataFrame.describe() -- NON-NUMERIC (STRING) COLUMNS")
    print("=" * 70)
    string_dtype = "str" if "str" in df.dtypes.astype(str).values else "object"
    print(df.describe(include=[string_dtype]))


def unpack_dict_range_columns(df):
    """spend/impressions/estimated_audience_size -> *_lower_bound / *_upper_bound numeric cols."""
    for col in DICT_RANGE_COLUMNS:
        def get_bound(value, key):
            if pd.isna(value):
                return None
            try:
                parsed = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                return None
            return pd.to_numeric(parsed.get(key), errors="coerce") if isinstance(parsed, dict) else None

        df[f"{col}_lower_bound"] = df[col].apply(lambda v: get_bound(v, "lower_bound"))
        df[f"{col}_upper_bound"] = df[col].apply(lambda v: get_bound(v, "upper_bound"))
    return df


def explode_list_columns(df):
    """publisher_platforms/illuminating_mentions -> exploded value_counts (not added to df)."""
    exploded_counts = {}
    for col in LIST_COLUMNS:
        parsed = df[col].apply(lambda v: ast.literal_eval(v) if pd.notna(v) else [])
        exploded = parsed.explode()
        exploded_counts[col] = exploded.value_counts()
    return exploded_counts


def parse_date_columns(df):
    
    for col in DATE_COLUMNS:
        parsed = pd.to_datetime(df[col], format="%Y-%m-%d", errors="coerce")
        failure_rate = parsed.isna().mean()
        if failure_rate > 0.5:  # strict format assumption was wrong for this file
            parsed = pd.to_datetime(df[col], errors="coerce")
            failure_rate = parsed.isna().mean()
        df[col] = parsed
        newly_failed = parsed.isna().sum()
        if failure_rate > 0:
            print(f"  note: {col} -- {newly_failed} value(s) could not be parsed as dates "
                  f"({failure_rate*100:.1f}%)")
    return df


def show_numeric_bound_stats(df):
    print("\n" + "=" * 70)
    print("DICT-RANGE COLUMNS (unpacked lower/upper bound numeric stats)")
    print("=" * 70)
    bound_cols = [f"{c}_{b}" for c in DICT_RANGE_COLUMNS for b in ("lower_bound", "upper_bound")]
    print(df[bound_cols].describe())


def show_list_value_counts(exploded_counts):
    print("\n" + "=" * 70)
    print("LIST COLUMNS (exploded item value_counts)")
    print("=" * 70)
    for col, counts in exploded_counts.items():
        print(f"\n{col} -- nunique={counts.shape[0]}")
        print(counts.head(5))


def show_date_stats(df):
    print("\n" + "=" * 70)
    print("DATE COLUMNS")
    print("=" * 70)
    print(df[DATE_COLUMNS].describe())


def show_categorical_value_counts(df):
    print("\n" + "=" * 70)
    print("CATEGORICAL COLUMNS -- value_counts() / nunique()")
    print("=" * 70)
    string_dtype = "str" if "str" in df.dtypes.astype(str).values else "object"
    categorical_cols = df.select_dtypes(include=[string_dtype]).columns
    for col in categorical_cols:
        print(f"\n{col}  (nunique={df[col].nunique()})")
        print(df[col].value_counts().head(5))


def verify_against_pure_python(df):
    
    print("\n" + "=" * 70)
    print("VERIFICATION: PANDAS vs PURE PYTHON")
    print("=" * 70)

    check_cols = ["illuminating_incivility", "illuminating_scam",
                  "spend_lower_bound", "impressions_upper_bound",
                  "estimated_audience_size_lower_bound"]

    for col in check_cols:
        series = df[col].dropna()
        pandas_mean = series.mean()
        pandas_std = series.std()  # ddof=1 (sample), matches statistics.stdev

        pure_values = [str(v) for v in series]
        pure = numeric_stats(pure_values)

        match = (
            abs(pandas_mean - pure["mean"]) < 1e-6
            and abs(pandas_std - (pure["std"] or 0)) < 1e-6
        )
        print(f"\n{col}")
        print(f"  pandas : mean={pandas_mean:.6f}  std={pandas_std:.6f}")
        print(f"  pure py: mean={pure['mean']:.6f}  std={(pure['std'] or 0):.6f}")
        print(f"  match  : {match}")


def main():
    df = load_data()
    show_structure(df)
    show_missing(df)
    show_describe(df)

    df = unpack_dict_range_columns(df)
    show_numeric_bound_stats(df)

    exploded_counts = explode_list_columns(df)
    show_list_value_counts(exploded_counts)

    df = parse_date_columns(df)
    show_date_stats(df)

    show_categorical_value_counts(df)
    verify_against_pure_python(df)


if __name__ == "__main__":
    main()