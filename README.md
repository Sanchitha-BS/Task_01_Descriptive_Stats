# 2024 Presidential Facebook Ads — Descriptive Statistics

Analysis of `fb_ads_president_scored_anon.csv` (246,745 rows, 40 columns),
Facebook's public ad-library export of 2024 U.S. presidential campaign ads,
scored with additional "illuminating_*" content-classification flags.

## Dataset overview

| | |
|---|---|
| Total records | 246,745 |
| Total columns | 40 |
| Numeric columns (`illuminating_*` flags) | 26 |
| Categorical / text columns | 14 |
| Dict-range columns (spend, impressions, audience size) | 3 |
| List-string columns (platforms, mentions) | 2 |
| Date columns | 3 |

## Getting the dataset

The CSV is not included in this repository. Download it separately and
place it in the same folder as the scripts before running either one:

Dataset source: 2024 Facebook Political Ads Dataset — download from
the course-provided Google Drive link.

1. Download fb_ads_president_scored_anon.csv from the drive link.
2. Place the file in the repo root, alongside the scripts:

```text
Task_01_Descriptive_Stats/
├── fb_ads_president_scored_anon.csv   <- add this (not tracked in git)
├── pure_python_stats.py
├── pandas_stats.py
├── README.md
├── Comparison.md
└── Findings.md
```

If you'd rather keep the CSV somewhere else, update the `CSV_PATH`
constant near the top of both `pure_python_stats.py` and
`pandas_stats.py` — both currently default to
`fb_ads_president_scored_anon.csv` in the working directory.

## What's in this repo

| File | What it is |
|---|---|
| `pure_python_stats.py` | Descriptive statistics using only the Python standard library — no Pandas, no NumPy |
| `pandas_stats.py` | The same analysis using Pandas |
| `Comparison.md` | Where the two implementations agreed/disagreed, and what writing the manual version revealed |
| `Findings.md` | Narrative write-up of what the data actually shows (spend concentration, timing patterns, mentions, geography, surprises) |
| `README.md` | This file |

## Setup

Only dependency is Pandas, needed for `pandas_stats.py`
(`pure_python_stats.py` has none):

```bash
pip install pandas
```

## Running the scripts

```bash
python3 pure_python_stats.py
python3 pandas_stats.py
```

Each prints a full report to stdout — dataset shape, missing-value counts,
per-column type inference, and full descriptive statistics (count, mean,
min, max, median, std for numeric fields; count, unique, mode+frequency,
top 5 for categorical fields). `pandas_stats.py` additionally imports and
calls functions from `pure_python_stats.py` directly to cross-check its
own numbers against the manual implementation, so run
`pure_python_stats.py` at least once first (or just keep both files in the
same folder — the import happens automatically).

## A few things about the data worth knowing before you read the output

- **`spend`, `impressions`, and `estimated_audience_size`** are not stored
  as plain numbers — Facebook discloses these as ranges, stringified as
  Python dict literals (e.g. `"{'lower_bound': '10001', 'upper_bound':
  '50000'}"`). Both scripts parse these into separate `*_lower_bound` /
  `*_upper_bound` numeric fields rather than leaving them as opaque
  strings, since that's the only way to get real numeric stats on
  spend/reach — the three most important numbers in the dataset.
- **`publisher_platforms` and `illuminating_mentions`** are stringified
  lists (e.g. `"['facebook', 'instagram']"`). Both scripts explode these
  into per-item frequency counts (e.g. "how many ads mention Facebook" vs.
  "how many ads mention this exact platform combination").
- **Date columns** (`ad_creation_time`, `ad_delivery_start_time`,
  `ad_delivery_stop_time`) are parsed with a small fallback list of
  formats rather than one fixed format, because the same nominal dataset
  has been observed with dates stored as both `YYYY-MM-DD` and unpadded
  `M/D/YYYY` depending on how/where the CSV was exported. See
  `Comparison.md` for the full story — this was an actual bug caught
  mid-project, not a hypothetical.
- **"Missing"** is defined consistently across both scripts as empty
  string plus a small set of null tokens (`n/a`, `na`, `null`, `none`,
  `nan`) — not just blank cells.

