import csv
import ast
import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime

CSV_PATH = "fb_ads_president_scored_anon.csv"
MISSING_TOKENS = {"", "n/a", "na", "null", "none", "nan"}

DICT_RANGE_COLUMNS = {"estimated_audience_size", "impressions", "spend"}
LIST_COLUMNS = {"publisher_platforms", "illuminating_mentions"}
DATE_COLUMNS = {"ad_creation_time", "ad_delivery_start_time", "ad_delivery_stop_time"}


def is_missing(v):
    return v is None or v.strip().lower() in MISSING_TOKENS


def parse_number(v):
    cleaned = str(v).strip().replace("$", "").replace(",", "")
    try:
        n = float(cleaned)
        return n if math.isfinite(n) else None
    except ValueError:
        return None


def parse_container(v, kind):
    try:
        parsed = ast.literal_eval(v.strip())
    except (ValueError, SyntaxError):
        return None
    return parsed if isinstance(parsed, kind) else None


def parse_date(v):
    try:
        return datetime.strptime(v.strip(), "%Y-%m-%d")
    except ValueError:
        return None


def numeric_stats(values):
    nums = [n for n in (parse_number(v) for v in values) if n is not None]
    if not nums:
        return {"count": 0}
    return {
        "count": len(nums), "mean": sum(nums) / len(nums), "min": min(nums),
        "max": max(nums), "median": statistics.median(nums),
        "std": statistics.stdev(nums) if len(nums) >= 2 else None,
    }


def categorical_stats(values, top_n=5):
    if not values:
        return {"count": 0}
    counts = Counter(values)
    top = counts.most_common(top_n)
    return {"count": len(values), "unique": len(counts),
            "mode": top[0][0], "mode_freq": top[0][1], "top": top}


def date_stats(values):
    dates = [d for d in (parse_date(v) for v in values) if d]
    if not dates:
        return {"count": 0}
    return {"count": len(dates), "min": min(dates).date(), "max": max(dates).date(),
            "unique": len(set(dates))}


def print_block(col, missing, col_type, body_lines):
    print(f"\n{col}  (missing={missing}, type={col_type})")
    for line in body_lines:
        print(f"  {line}")


def main():
    columns = defaultdict(list)
    total_rows = 0
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            total_rows += 1
            for col in fieldnames:
                columns[col].append(row.get(col, ""))

    print(f"Total rows: {total_rows} | Total columns: {len(fieldnames)}")

    for col in fieldnames:
        raw = columns[col]
        missing = sum(1 for v in raw if is_missing(v))
        clean = [v for v in raw if not is_missing(v)]

        if col in DICT_RANGE_COLUMNS:
            lower = [str(parse_container(v, dict).get("lower_bound")) for v in clean
                     if parse_container(v, dict) and "lower_bound" in parse_container(v, dict)]
            upper = [str(parse_container(v, dict).get("upper_bound")) for v in clean
                     if parse_container(v, dict) and "upper_bound" in parse_container(v, dict)]
            ls, us = numeric_stats(lower), numeric_stats(upper)
            lines = [f"lower_bound: n={ls['count']} mean={ls.get('mean',0):.0f} "
                     f"min={ls.get('min')} max={ls.get('max')} median={ls.get('median')} "
                     f"std={ls.get('std',0):.0f}" if ls["count"] else "lower_bound: no data",
                     f"upper_bound: n={us['count']} mean={us.get('mean',0):.0f} "
                     f"min={us.get('min')} max={us.get('max')} median={us.get('median')} "
                     f"std={us.get('std',0):.0f}" if us["count"] else "upper_bound: no data"]
            print_block(col, missing, "dict-range (numeric bounds)", lines)

        elif col in LIST_COLUMNS:
            exploded = []
            for v in clean:
                items = parse_container(v, list)
                exploded.extend(items or [])
            s = categorical_stats(exploded)
            lines = ([f"count={s['count']} unique items={s['unique']}",
                      f"mode={s['mode']!r} (frequency={s['mode_freq']})", "top 5:"] +
                     [f"  {val}: {freq}" for val, freq in s["top"]]) if s["count"] else ["no data"]
            print_block(col, missing, "list-string (exploded per item)", lines)

        elif col in DATE_COLUMNS:
            s = date_stats(clean)
            lines = [f"count={s['count']} min={s['min']} max={s['max']} unique={s['unique']}"] if s["count"] else ["no data"]
            print_block(col, missing, "date", lines)

        else:
            num = numeric_stats(clean)
            is_numeric = num["count"] > len(clean) / 2 if clean else False
            if is_numeric:
                std_str = f"{num['std']:.4f}" if num["std"] is not None else "N/A (n<2)"
                lines = [f"count={num['count']} mean={num['mean']:.4f} min={num['min']} "
                         f"max={num['max']} median={num['median']} std={std_str}"]
                print_block(col, missing, "numeric", lines)
            else:
                s = categorical_stats(clean)
                if s["count"]:
                    lines = [f"count={s['count']} unique={s['unique']}",
                             f"mode={s['mode']!r} (frequency={s['mode_freq']})", "top 5:"] + \
                            [f"  {val}: {freq}" for val, freq in s["top"]]
                else:
                    lines = ["no data (all missing)"]
                print_block(col, missing, "categorical", lines)


if __name__ == "__main__":
    main()