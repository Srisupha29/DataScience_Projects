# Data Dictionary — Upworthy Headline Experiment Analysis

## Dataset overview

- **Source:** Upworthy Research Archive
- **File:** `upworthy-archive-exploratory-packages-03.12.2020.csv`
- **Rows:** 22,666
- **Columns:** 17
- **Distinct experiments:** 4,873
- **Unit of observation:** Package (headline-and-image combination)
- **Outcome:** Clicks out of impressions
- **Scope:** Exploratory analysis only; confirmatory data will not be examined until hypotheses and analysis decisions are documented.

## Column reference

| Column | Meaning / intended use | Notes and limitations |
|---|---|---|
| `column00` | Source row identifier | Unique across all 22,666 rows in the inspected file. |
| `created_at` | Package creation timestamp | Timezone is undocumented. |
| `updated_at` | Last update timestamp | May reflect later edits in the source system. |
| `clickability_test_id` | Experiment identifier | Packages sharing this ID belong to the same experiment. |
| `excerpt` | Article excerpt | Missing in 10.66% of rows. Not assumed to be shown during the test. |
| `headline` | Tested headline text | Primary text feature source. Repeated text occurs within experiments. |
| `lede` | Opening sentence or paragraph of the article | Missing in 0.05% of rows; not assumed to be shown during the test. |
| `slug` | Internal name used in the web address | May distinguish packages whose headline text is identical. |
| `eyecatcher_id` | Image identifier | Missing in 0.10% of rows; image files are not included. |
| `impressions` | Number of viewers assigned to the package | Denominator for package click-through rate (CTR). |
| `clicks` | Number of viewers who clicked the package | Numerator for package CTR. |
| `significance` | Historical internal editorial metric | Not a reliable statistical-significance estimate; do not use as a p-value or model feature. |
| `first_place` | Historical field used to guide editorial decisions | Exact operational meaning should not be assumed beyond the archive documentation. |
| `winner` | Whether editors selected the package for publication after testing | Editorial choice, not necessarily the package with the highest observed CTR. |
| `share_text` | Text used in social-sharing previews | Missing in 85.85% of rows; archive documentation says it was not shown during the headline tests. |
| `square` | Part of the social-sharing suggestion when used | Missing in 67.15% of rows; not assumed to be a tested stimulus. |
| `test_week` | Archive-created week variable | Intended for stratified random sampling; investigate before using as a time variable. |

## Initial data-quality findings

- All 22,666 source row identifiers are unique.
- No missing, zero, or negative impressions were found.
- No missing or negative click counts were found.
- No rows had more clicks than impressions.
- Each experiment contains between 2 and 14 rows; the median is 4.
- Some experiments contain repeated headline text with distinct slugs. These records require further investigation before defining the analytical unit.

## Initial metric

Package-level click-through rate:

`CTR = clicks / impressions`

Pooled descriptive CTR:

`SUM(clicks) / SUM(impressions) = 1.5196%`

The pooled figure is descriptive and does not measure the effect of a particular headline feature.

## Analytical cautions

1. Compare packages within the same experiment when estimating experimental contrasts.
2. Do not remove repeated headline text without investigating package identity.
3. Do not interpret `significance` as a p-value.
4. Do not use `winner`, `first_place`, or `significance` as predictors of clicks.
5. Do not automatically replace missing text with empty strings or remove rows without a documented rationale.
6. Associations between headline features and CTR across unrelated experiments are not automatically causal.
7. Keep confirmatory and holdout data untouched until the analysis plan is preregistered.

## Documentation source

Upworthy Research Archive, “Data in the Upworthy Research Archive”:
https://upworthy.natematias.com/about-the-archive.html