# Findings: 2024 Presidential Facebook Ad Spending

## Which organizations spent the most? Is spending concentrated or distributed?

Across 246,745 ads and 4,546 distinct page names, total estimated spend
is roughly $262 million. The top five spenders are Kamala Harris ($82.8M),
Joe Biden ($26.4M), Donald J. Trump ($19.6M), Kamala HQ ($8.1M), and Tim
Walz ($7.6M) — together 55% of all spend. The top ten (adding The Daily
Scroll, Future Forward, Barack Obama, America PAC, and Robert F. Kennedy
Jr.) account for 63%.

Spending is concentrated but not narrowly so. The top 20 pages together
still only reach 72% of total spend, meaning more than a quarter of all
money flows through the remaining 4,500+ pages — a long tail of state
party committees, PACs (Future Forward, America PAC, AFP Action, Senate
Democrats, Working America), and smaller advocacy or media-style pages.
It's a "concentrated core, long tail" pattern rather than a two-player
story.

One structural caveat: the two candidates' totals aren't directly
comparable at face value. Harris-aligned spending is also split across
separately-named pages — "Kamala HQ" ($8.1M) and "Biden-Harris HQ"
($2.5M) — while Trump's spend is more consolidated under his own page
plus "America PAC." Any "candidate A spent $X vs. candidate B spent $Y"
comparison needs to specify whether it's aggregating by candidate or by
individual page, since the two give different pictures.

## Is there a pattern in when ads were purchased? Spikes around events?

Daily ad-creation volume is highly uneven — a mean of 451 ads/day against
a standard deviation of 876. Several spikes line up with known campaign
events:

- **July 21, 2024 (Biden's withdrawal from the race):** ad creation
  jumped from 172 the day before to 1,610 that day, with estimated spend
  spiking to $9.4M — the largest single-day spend spike found anywhere
  outside the final election week.
- **September 10, 2024 (Harris–Trump debate):** 3,853 ads were created
  that day, roughly 6x the daily average, with spend around $5.4M.
- **The single busiest stretch of the entire campaign was not a debate at
  all — it was the final two weeks before the election.** October 27
  (8,619 ads) and October 28 (7,356 ads) are the two highest-volume single
  days in the whole dataset, part of a sustained run of 4,000+ ads/day
  through late October, consistent with a final get-out-the-vote push
  rather than a reaction to any single news event.
- **Ad creation essentially stops at Election Day itself** — only a
  handful of ads are dated November 2–5. This is very likely a Meta
  policy effect (political ads are restricted in the final days before a
  U.S. election) rather than a spending decision by advertisers, and is
  worth treating as a data-collection artifact rather than a campaign
  choice.

## Which candidates were mentioned most? Does spend relate to mentions?

Donald Trump is the single most-mentioned name in ad text (78,324
mentions, associated with an estimated $81.6M in spend), ahead of Kamala
Harris (53,239 mentions, $60.0M), Joe Biden (24,247 mentions, $22.0M),
"President Trump" (22,153 — counted separately from "Donald Trump" as a
distinct string), and "President Biden" (16,517).

Across the top 15 most-mentioned political figures, the correlation
between mention count and total spend behind ads mentioning that name is
**0.996** — almost perfectly linear. This makes intuitive sense (more
money buys more ad volume, and more ad volume creates more chances to
mention a name), but it means mention frequency in this dataset is
essentially a proxy for spend, not an independent signal about media
attention or messaging strategy.

## Are there geographic patterns in the data?

Very little. 99.94% of ads are billed in USD. The remaining 146 ads span
17 other currencies (INR, GBP, EUR, PKR, EGP, and others), but together
represent only 0.04% of total estimated spend — likely a mix of
international advertisers, currency-conversion artifacts, or a handful of
foreign-based pages running small U.S.-facing political ads. There isn't
enough volume to support a real geographic breakdown; the honest finding
is that this is an overwhelmingly domestic, USD-denominated dataset, with
foreign currency amounting to a rounding error rather than a pattern.

## What surprised you?

Cross-referencing the `illuminating_scam` flag against page names turned
up the clearest surprise: **several pages flagged as scam content 100% of
the time have generically "patriotic" names** — "A Patriotic American,"
"American Patriot United," "Proud To Be Patriots," "Patriot Sanctuary,"
and others, each with well over 100 ads and a 100% scam-flag rate. This
points to a cluster of ad-farm or clickbait pages deliberately adopting
patriotic branding to piggyback on real political ad traffic — distinct
from the legitimate campaign and PAC infrastructure the rest of this
report describes. A dataset of "political ads" is not the same thing as
a dataset of "campaign ads," and the two overlap far less than expected.

A second, smaller surprise: `illuminating_scored_message` contains
near-duplicate rows differing only by hex-string case (the same message
hash appears in both lowercase and uppercase form — one pair appears
3,046 and 2,926 times respectively). It's a data-processing quirk worth
correcting before this field is used for message-level deduplication in
any downstream analysis.
