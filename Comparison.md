# Comparison: Pure Python vs. Pandas Descriptive Statistics

## Do the results agree? If not, why not? (Rounding? Missing value handling? Type inference differences?)

For every numeric and categorical column, the two implementations agree to
at least six decimal places:

| Metric | Pure Python | Pandas |
|---|---|---|
| Total rows | 246,745 | 246,745 |
| Missing — `bylines` | 1,009 | 1,009 |
| Missing — `ad_delivery_stop_time` | 2,159 | 2,159 |
| Mean — `illuminating_scam` | 0.071633 | 0.071633 |
| Mean — `illuminating_incivility` | 0.187526 | 0.187526 |
| Mean — `spend_lower_bound` | 921.951813 | 921.951813 |
| Mean — `estimated_audience_size_lower_bound` | 480,610.495401 | 480,610.495401 |
| Unique `page_id` | 4,475 | 4,475 |
| Mode `page_name` | Kamala Harris (n=55,503) | Kamala Harris (n=55,503) |

This agreement was not automatic — it required deliberately matching two
choices Pandas makes as unexamined defaults, and it broke once, for a
reason worth explaining in full.

**Rounding:** not a source of disagreement here. Once the same standard
deviation convention is used (see below), values match well past any
reasonable display precision.

**Missing value handling:** not a source of disagreement, but only because
it was made consistent on purpose. Pandas applies its own internal
NA-token list automatically during `read_csv()`. Rather than rely on
whatever that list happens to be, the pure-Python script's explicit token
set (`""`, `n/a`, `na`, `null`, `none`, `nan`) was used as the standard
against which Pandas' behavior was checked — so the two would not silently
diverge on some edge-case token neither script had been tested against.
Missing counts matched exactly on all 40 columns.

**Type inference / format assumptions — this is where they actually
disagreed.** The three date columns (`ad_creation_time`,
`ad_delivery_start_time`, `ad_delivery_stop_time`) initially produced
completely different results: pure Python reported **zero parsed rows**
for all three, while Pandas reported full date ranges (2021-07-06 through
2024-11-05). This is not a rounding issue — it is a parsing-format
assumption that turned out to be wrong. The pure-Python date parser was
hardcoded to accept only ISO format (`YYYY-MM-DD`). Inspecting the raw
values via Pandas' own `value_counts()` on the un-parsed column showed the
actual stored format is `M/D/YYYY`, unpadded (`10/27/2024`, `11/5/2024`).
Every value failed the strict check and was silently recorded as missing
— not because the data was absent, but because the parser's assumption
about its shape was wrong.

Pandas did not fail the same way, but not because it is inherently smarter
about dates: the Pandas script had been written with a self-verifying
fallback (try the expected ISO format; if more than half the values fail,
retry with Pandas' automatic format inference). Without that fallback,
`pd.to_datetime(col, format="%Y-%m-%d")` would have failed identically.
Once the pure-Python parser was given the same fallback — try a small set
of known formats per value instead of one fixed format — both scripts
produced identical date ranges. The standard deviation convention
(`statistics.stdev`, sample/÷(n−1), matching Pandas' `ddof=1` default) was
also a deliberate match rather than a coincidence; had either side used
population stdev instead, every numeric column would have disagreed
starting in the third decimal place.

## Where did the pure Python approach force decisions that Pandas made silently?

1. **Numeric-vs-categorical classification.** Pandas' `read_csv()` applies
   an implicit all-or-nothing rule: a single unconvertible value in a
   column demotes the whole column to `object` dtype, with no report of
   why. Pure Python required an explicit, documented rule instead — a
   column counts as numeric if more than 50% of its non-missing values
   parse cleanly as numbers, chosen deliberately over all-or-nothing
   because real operational data usually contains a small number of
   non-numeric entries in an otherwise numeric field.

2. **What counts as "missing."** Pandas silently applies its own default
   NA-token list on ingestion. Pure Python required this list to be
   defined and justified explicitly rather than inherited.

3. **Encoded-range and encoded-list parsing.** Neither tool has native
   awareness that `"{'lower_bound': '10001', 'upper_bound': '50000'}"`
   represents a numeric range, or that `"['facebook', 'instagram']"`
   represents a list of categories. This is the one place Pandas offered
   no automatic advantage at all — the same `ast.literal_eval`-based
   unpacking logic had to be hand-written for both scripts. For this
   dataset's three most consequential numeric fields (spend, impressions,
   audience size), "let Pandas handle it" was never actually an option.

4. **Standard deviation formula.** Pandas has a default (`ddof=1`) that
   most users never look at; pure Python has no default at all, only an
   explicit choice between `statistics.stdev` and `statistics.pstdev` —
   which is what prompted checking Pandas' actual behavior instead of
   assuming it matched.

## What did writing the pure Python version reveal that using only Pandas might have missed?

- **The date-format mismatch itself.** Under a Pandas-only workflow,
  `to_datetime()`'s automatic inference likely would have guessed the
  correct format silently and moved on. It was the pure-Python script's
  stricter, single-format parser — which failed loudly, producing zero
  parsed rows — that forced the investigation and surfaced that this
  file's dates are non-ISO, unpadded `M/D/YYYY`. A real inconsistency in
  the data was caught specifically *because* the manual tool was less
  forgiving, not more capable.

- **`estimated_audience_size` has an open-ended top bucket.** 246,166 rows
  carry a `lower_bound`; only 146,020 carry an `upper_bound`. The
  remaining 100,146 rows (the "1,000,001+" audience bucket) are open-ended
  by design. This was only visible because unpacking the range dictionary
  by hand meant explicitly checking for the presence of the `upper_bound`
  key on every row. Pandas' `.describe()` on the raw string column just
  reports `unique=8` and stops — the open-ended structure stays invisible
  unless someone deliberately goes looking for it.

- **Near-duplicate rows in `illuminating_scored_message` differing only by
  case** (`9b2d5b46...`, n=3,046, vs. `9B2D5B46...`, n=2,926) — noticed
  while building the frequency table by hand, where two visibly distinct
  "top values" turned out to be the same hash.

- **A cleaner separation between "missing" and "unparseable."** Pure
  Python reports these as two distinct quantities. Pandas' `.describe()`
  collapses a value that failed silent coercion during ingestion and a
  value that was genuinely blank in the source into the same `NaN`
  representation, with no record of which occurred.
