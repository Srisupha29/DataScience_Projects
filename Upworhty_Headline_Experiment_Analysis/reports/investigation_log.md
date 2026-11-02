# Upworthy Headline Experiment Analysis
## Data Investigation Log

**Project phase:** Phase 1: Data Understanding and Profiling  
**Status: Phase 2.4: ML Modeling has been completed.**
**Tools:** Python, DuckDB, pandas, SQL  
**Source dataset:** `upworthy-archive-exploratory-packages-03.12.2020.csv`
---

## Purpose

The objective of this investigation is to understand the structure, completeness, and limitations of the Upworthy Research Archive before conducting statistical analysis.

The initial investigation focuses on:
- Understanding the dataset schema and unit of observation.
- Measuring missingness and validating engagement counts.
- Understanding how packages, headlines, images, and experiments relate to one another.
- Identifying fields that should not be interpreted as independent statistical evidence.
- Establishing defensible rules for subsequent data cleaning and analysis.

## Step 1 — Inspect the dataset

**Script:** `src/inspect_data.py`

### Findings

- Total rows: 22,666
- Total columns: 17
- Distinct experiments (`clickability_test_id`): 4,873
- Unique row identifiers (`column00`): 22,666

The dataset contains identifiers, timestamps, headline text, image identifiers, impressions, clicks, and several archive-specific metadata fields.

### Interpretation

The dataset contains multiple observations within each experiment. Therefore, the analysis must preserve the relationship between packages belonging to the same experiment.

A unique row identifier does not imply a unique headline or a unique experiment.

### Decision

Retain `clickability_test_id` as the experiment grouping identifier and `column00` as the row-level identifier, subject to further documentation checks.

---

## Step 2 — Profile the dataset

**Script:** `src/profile_data.py`

### Findings

- Total packages: 22,666
- Total experiments: 4,873
- Total impressions: 81,024,151
- Total clicks: 1,231,208
- Pooled CTR: approximately 1.52%
- Packages per experiment: median 4, mean approximately 4.65, maximum 14
- Impressions per package: median 3,122, mean approximately 3,574.7, maximum 25,314

### Interpretation

The number of packages varies across experiments. An assumption that every experiment contains exactly two alternatives would be incorrect.

The pooled CTR is a descriptive aggregate. It is not an estimate of the causal effect of a headline change because it combines observations across experiments and weights packages by their impressions.

### Decision

Use within-experiment comparisons for subsequent analyses rather than treating all packages as independent alternatives in one pooled comparison.

---

## Step 3 — Assess data quality

**Script:** `src/check_data_quality.py`

### Missing-value findings

| Column | Missing values | Percentage |
|---|---:|---:|
| `excerpt` | 2,417 | 10.66% |
| `lede` | 12 | 0.05% |
| `eyecatcher_id` | 22 | 0.10% |
| `share_text` | 19,458 | 85.85% |
| `square` | 15,220 | 67.15% |

### Engagement-count validation

The checks found:

- Zero rows with zero impressions.
- Zero rows with missing impressions or clicks.
- Zero rows with clicks greater than impressions.
- Zero rows with negative impressions or clicks.

The row identifier `column00` is unique across all 22,666 rows.

### Interpretation

The impression and click counts pass the basic logical validation checks performed so far.

Several descriptive or metadata fields have substantial missingness. Missingness alone does not establish that a row is invalid, so these observations should not automatically be deleted.

### Decision

Preserve the original data. Investigate the analytical relevance of each field before deciding whether to exclude observations or handle missing values.

---

## Step 4 — Investigate repeated headlines

**Script:** `src/investigate_variants.py`

### Example A

Experiment: `53480581be4154443a000008`

- Package rows: 14
- Distinct headlines: 1
- Distinct slugs: 14
- Distinct image IDs: 14

All 14 rows contain the same headline, but their image identifiers, impressions, and clicks differ.

### Example B

Experiment: `52930ef6d40ad9e426003b53`

- Package rows: 11
- Distinct headlines: 1
- Distinct slugs: 11
- Distinct image IDs: 11

Again, all rows share the same headline text, while image identifiers and observed CTRs vary.

### Interpretation

Repeated headline text does not necessarily indicate duplicate records. A headline can occur in multiple packages with different image identifiers.

The observed CTR differences are descriptive. This inspection alone cannot establish that the images caused the differences.

### Decision

Do not deduplicate observations based solely on headline text. Preserve package-level records for further investigation.

---

## Step 5 — Measure headline and image variation

**Script:** `src/summarize_experiment_structure.py`

### Findings

- Total experiments: 4,873
- Total packages: 22,666
- Experiments with multiple distinct headlines: 2,601 (53.5%)
- Experiments with multiple distinct image IDs: 1,726 (35.4%)
- Experiments with one distinct headline and one distinct image ID: 838

### Headline distribution

| Distinct headlines | Experiments |
|---:|---:|
| 1 | 2,266 |
| 2 | 316 |
| 3 | 150 |
| 4 | 1,291 |
| 5 | 386 |
| 6 | 371 |
| 7 | 46 |
| 8 | 34 |
| 9 | 9 |
| 10 | 2 |
| 11 | 1 |
| 12 | 1 |

### Interpretation

Headline variation differs substantially between experiments. Some experiments contain one distinct headline, while others contain many.

Headline variation and image variation are overlapping properties: an experiment may vary both.

The number of distinct image IDs is not necessarily the same as the number of visually distinct images, and an image identifier does not establish which experimental treatment was intended.

### Decision

Do not assume that every experiment tests multiple headline texts. Before headline-focused statistical analysis, investigate which experiments vary headlines, images, or both.

---

## Current analytical decisions

1. Preserve package-level observations.
2. Group related packages using `clickability_test_id`.
3. Do not deduplicate solely on headline text.
4. Treat the pooled CTR as descriptive, not causal.
5. Do not treat `significance`, `winner`, or `first_place` as independent evidence of statistical significance or causal superiority.
6. Investigate missing image identifiers before classifying image variation.
7. Avoid automatic row deletion or missing-value imputation before the analytical purpose of each field is established.
8. Document the unit of analysis and limitations before selecting statistical methods.

## Limitations and open questions

- What proportion of experiments vary headline text, image IDs, or both?
- How many image identifiers are missing, and how are they distributed across experiments?
- Which fields are documented as experimental stimuli versus archive metadata?
- What cleaning and inclusion rules are appropriate for the eventual research questions?
- What assumptions are required for valid within-experiment comparisons?

## Step 6 — Classify Headline and Image ID Variation

### Objective

Classify experiments according to the number of distinct headlines and image IDs. Check whether missing image IDs are concentrated in particular experiments.

### Method

Ran `src/classify_experiments.py` to group packages by `clickability_test_id` and classify experiments based on their distinct headline and image ID counts. The script also checked image ID completeness.

### Observed Results

#### Headline and Image ID Variation

| Headline Pattern | Image ID Pattern | Experiment Count |
|---|---|---:|
| Multiple headlines | All image IDs missing | 3 |
| Multiple headlines | Multiple distinct image IDs | 300 |
| Multiple headlines | One distinct image ID | 2,304 |
| One headline | All image IDs missing | 2 |
| One headline | Multiple distinct image IDs | 1,426 |
| One headline | One distinct image ID | 838 |
| **Total** | | **4,873** |

#### Image ID Completeness

| Metric | Result |
|---|---:|
| Total experiments | 4,873 |
| Experiments with no missing image IDs | 4,868 |
| Experiments with some missing image IDs | 0 |
| Experiments with all image IDs missing | 5 |
| Total rows missing an image ID | 22 |

### Interpretation

1. **Headline variation:** 2,601 experiments have multiple distinct headlines, representing approximately 53.5% of all experiments.
2. **Image ID variation:** 1,726 experiments have multiple distinct image IDs, representing approximately 35.4% of all experiments.
3. **One headline, multiple image IDs:** 1,426 experiments fall into this category. These may be useful for investigating image variation separately from headline variation.
4. **One headline, one image ID:** 838 experiments fall into this category. This does not mean that each experiment contains only one package; multiple package rows can share the same headline and image ID.
5. **Missing image IDs:** All 22 rows with missing image IDs occur in

## Step 7 — Open Questions and Analytical Decisions

### Objective

Identify unresolved questions about the dataset's structure and measurement before beginning performance analysis.

### Open Questions

| Question | Why It Matters | Current Status |
|---|---|---|
| What does one row represent? | Determines the correct unit of analysis. | Documentation describes each row as a package, representing a headline-and-image combination. |
| Can multiple rows share the same headline? | Repeated text must not automatically be treated as duplicate data. | Yes. Investigations found experiments with repeated headline text and different slugs and image IDs. |
| Do different image IDs always represent different visual content? | Image IDs alone cannot establish visual differences. | Unresolved; distinct IDs do not guarantee visually distinct images. |
| What do `winner`, `first_place`, and `significance` represent? | These fields could be misleading if interpreted as independent statistical evidence. | Treat as editorial metadata unless documentation supports a more specific interpretation. |
| Are all experiments suitable for headline-performance comparisons? | Some experiments have only one distinct headline, so not all support a direct headline-variant comparison. | No. Eligibility must be determined from the experiment structure. |
| How should differences in impressions be handled? | Raw click counts are not directly comparable when exposure differs. | Use click-through rate (CTR) for descriptive comparisons and account for statistical uncertainty in subsequent analysis. |
| What experimental-design details are needed for valid inference? | Assignment procedures and dependence between observations affect statistical conclusions. | Requires further investigation before selecting the inferential method. |

### Analytical Decisions

1. Preserve the original raw CSV and perform transformations on derived data.
2. Use `clickability_test_id` to group packages into experiments.
3. Do not remove repeated headline text solely because it appears more than once.
4. Do not interpret `winner`, `first_place`, or `significance` as independent proof of statistical significance or causal superiority.
5. Distinguish experiments with multiple headlines from experiments with multiple image IDs.
6. Treat overall CTR as descriptive, not as evidence that a particular headline caused better performance.
7. Record assumptions and limitations before using the dataset for statistical comparisons.


## Identifier and Repeated-Record Investigation

### Identifier definitions
- `row_id`: Original source identifier from `column00`; unique per source row.
- `package_id`: Deterministic SHA-256 identifier based on experiment ID,
  normalized headline text, and recorded image ID.
- `clickability_test_id`: Identifier grouping packages within an experiment.

### Findings
- Source rows: 22,666.
- Distinct stimulus identities: 19,171.
- Repeated stimulus identities: 1,148.
- Every repeated identity has multiple distinct timestamps.
- No repeated identity has a missing timestamp.
- Repeated identities have differing impression counts, click counts, or both.

### Decisions and limitations
- Preserve every source row; do not deduplicate based on headline and image ID.
- Keep `row_id` as the source-record identifier and `package_id` as the
  stimulus-identity identifier.
- Retain `created_at` for temporal investigation.
- Do not aggregate repeated impression and click counts until the source
  recording process and row semantics are established.
- A recorded image ID does not prove visual identity, and a repeated
  stimulus identity does not prove independent experimental assignment.

## Identifier Uniqueness Audit

### Objective

Determine whether source row IDs, slugs, and constructed stimulus identifiers uniquely identify records.

### Findings

| Candidate identifier | Distinct keys | Excess rows beyond distinct keys | Result |
|---|---:|---:|---|
| `row_id` | 22,666 | 0 | Unique in the source extract |
| `clickability_test_id` + `slug` | 22,587 | 79 | Not unique |
| `clickability_test_id` + normalized headline + `eyecatcher_id` | 19,171 | 3,495 | Not unique; used as a stimulus-identity proxy |
| `clickability_test_id` + `slug` + `eyecatcher_id` | 22,636 | 30 | Not unique |

### Interpretation

The source row ID is the only tested identifier that uniquely identifies every row in the extract. Slugs and composite identifiers produce repeated keys.

Repeated keys do not, by themselves, prove that records are erroneous duplicates. Records sharing the same experiment, headline, slug, and image ID can have different impression and click counts. The source-record generation process and the independence of these observations remain unresolved.

### Analytical decisions

1. Preserve all source rows.
2. Retain `row_id` as the source-record identifier.
3. Retain `clickability_test_id` as the experiment grouping identifier.
4. Treat `package_id` as a constructed stimulus-identity proxy, not a unique source-record identifier.
5. Do not deduplicate or aggregate repeated records until their semantics are established.
6. Do not treat source-row uniqueness as evidence of statistical independence.

### Remaining investigation

Inspect records sharing the same experiment, slug, and image ID. Determine whether their counts and timestamps differ, and document any remaining uncertainty before selecting the unit of analysis.

### Follow-up: Repeated Key and Headline Normalization

A targeted audit examined records sharing the same experiment, slug, and image ID.

One apparent exception had two distinct raw headline strings according to exact string comparison. Inspection confirmed that the difference was a leading whitespace character: one headline had length 55 and the other length 54. After trimming whitespace, both normalized to the same 54-character headline.

The records nevertheless had different measurements:

- Row 46751: 6,906 impressions and 91 clicks.
- Row 46752: 6,863 impressions and 84 clicks.

**Interpretation:** Exact headline comparison can overstate headline variation when whitespace differs. Normalized headline text is more appropriate for classifying textual variants, while the original headline must remain available for traceability.

**Decision:** Preserve both source records. Do not deduplicate records solely because their normalized headline, experiment ID, slug, or image ID matches. The source does not establish why the measurements differ or whether the records represent independent observations.

**Remaining limitation:** The process that generated repeated records and their changing counts remains unresolved. Statistical inference must account for this uncertainty rather than treating all source rows as independent observations by default.

### Follow-up: Impression-Imbalance Review

#### Method

Reviewed the five experiments flagged by the project-defined maximum-to-minimum impression ratio threshold of 1.5. Examined the number of source rows, distinct package fingerprints, impression range, coefficient of variation, and whether each experiment falls within the project's defined randomization-risk screening window.

#### Observed Results

| Experiment ID | Source Rows | Distinct Package IDs | Minimum Impressions | Maximum Impressions | Max/Min Ratio | Risk-Window Screen |
|---|---:|---:|---:|---:|---:|---|
| `51d1e3934a5d3ff28b0001b0` | 4 | 4 | 2,763 | 4,490 | 1.625 | Within window |
| `51ddbd415d8e6fa6d2006471` | 2 | 2 | 948 | 1,571 | 1.657 | Within window |
| `526d4c1c94d1f182f600574f` | 5 | 5 | 17 | 54 | 3.176 | Within window |
| `52a5cf335de7b1f7a3000e04` | 5 | 4 | 280 | 522 | 1.864 | Within window |
| `5348bd88fe9c5a1bf500001b` | 9 | 9 | 1,902 | 25,314 | 13.309 | Outside window |

All five experiments exceed the project-defined review threshold. The experiment `5348bd88fe9c5a1bf500001b` has the largest observed imbalance, with a maximum-to-minimum impression ratio of approximately 13.31.

#### Interpretation and Limitations

- These flags identify experiments requiring further review; they do not establish that random assignment failed.
- The impression-ratio threshold of 1.5 is a project-defined screening rule, not a statistical significance threshold.
- The randomization-risk window is a separate screening dimension. Its dates and rationale should be verified against the source documentation before being interpreted as an established historical risk period.
- Unequal impressions may affect the precision and comparability of CTR estimates. The available fields alone do not establish why the differences occurred.
- The flagged experiments should remain identified for subsequent eligibility decisions. Do not silently delete them or interpret the flags as proof of bias.

#### Decision

Retain all five flags in the analytical dataset. Before inferential analysis, document the inclusion and exclusion rules and investigate the experimental design and the origin of the impression counts. Treat the screening results as diagnostic evidence rather than proof of randomization failure.

### Missing-Image Audit and Eligibility Decision

**Findings**

Five experiments have zero distinct recorded image IDs, covering 22 packages. All packages in these experiments have missing image IDs.

- Three experiments have multiple normalized headlines: `530527c3fe1bdf6bd0000003`, `5310bcc6dc7ca705b7000048`, and `53270be28d6f209195000022`.
- Two experiments have one normalized headline: `52faa100aab77d1c21000005` and `52fb18b70a9b91080a000019`.

**Decision**

Retain all five experiments in the audit. Do not classify them as confirmed headline-only or image-only comparisons because image consistency cannot be established from the recorded image IDs. Distinguish missing metadata from an observed absence of variation.

**Status:** Missing-image audit complete; final eligibility rules and experiment-level eligibility output pending.

### Unit of Analysis and Repeated Package Rows

**Source-row unit:** Each of the 22,666 rows is a distinct source record identified by the unique `row_id` derived from `column00`.

**Package/stimulus unit:** `package_id` is a constructed identity based on experiment ID, normalized headline, and image ID. The dataset contains 19,171 distinct stimulus identities, with 1,148 repeated identity groups.

**Experiment unit:** `clickability_test_id` identifies the experiment containing the packages.

**Finding:** Every repeated stimulus identity has multiple distinct timestamps. Repeated identities have differing impression counts, click counts, or both. The source-recording semantics have not been established.

**Decision:** Preserve all source rows. Do not deduplicate repeated package identities or aggregate their metrics until it is established whether repeated rows represent cumulative snapshots, incremental observations, or another recording structure. Retain `created_at` for subsequent investigation.

**Limitation:** A repeated stimulus identity does not establish independent experimental assignment, and the current evidence does not establish whether summing repeated metrics would double-count exposure or engagement.

**Status:** Unit identifiers documented; aggregation decision deferred pending clarification of repeated-row semantics.

### Repeated Metric Progression Audit — Final Decision

**Diagnostic findings**

The repeated-metric progression audit examined 198 repeated stimulus identities. All 198 have multiple creation timestamps, multiple update timestamps, and changing impression counts. Click counts change in 197 of the 198 identities.

The example records include non-monotonic impression and click counts. Metrics therefore do not consistently increase with the recorded timestamps.

**Unit-of-analysis decision**

- Preserve each source row as a distinct observation in the raw and prepared source-level data.
- Use `row_id` to identify source records, `package_id` to identify constructed stimulus identities, and `clickability_test_id` to identify experiments.
- Do not deduplicate repeated stimulus identities.
- Do not sum repeated impression or click counts or select a single row as representative without establishing the source-recording semantics.

**Limitation**

The available diagnostic does not establish whether repeated rows represent snapshots, corrections, or another recording process. The dataset evidence alone is insufficient to justify aggregation to one row per experiment and package. This remains an explicit limitation for subsequent analysis.

**Status:** Unit of analysis documented. Aggregation is deferred because the recording semantics remain unresolved. Any later metric analysis must preserve this limitation and avoid treating repeated rows as independent observations without justification.

### Primary Question and Analysis Plan

**Primary question**

Among experiments with multiple distinct normalized headlines and exactly one consistently recorded, non-missing image ID, how do headline variants' click-through rates compare?

**Primary metric**

Click-through rate (CTR), defined as clicks divided by impressions. CTR is the intended primary performance metric because raw click counts are affected by differences in exposure.

**Secondary questions**

- How do descriptive results differ across headline-only, image-only, and mixed headline/image variation?
- How sensitive are results to impression imbalance and minimum-data thresholds?
- Do conclusions change when headline text is normalized by lowercasing and trimming surrounding whitespace?

**Planned analysis sequence**

1. Describe the structure and data quality of eligible experiments.
2. Resolve, or explicitly retain as a limitation, the interpretation of repeated stimulus records and their click/impression metrics.
3. Calculate variant-level CTR only after establishing a defensible metric aggregation rule.
4. Confirm the experimental assignment procedure and dependence structure before selecting an inferential test.
5. Report descriptive comparisons separately from inferential conclusions.

**Constraints and limitations**

- Do not deduplicate repeated source records solely because headline text or image IDs match.
- Do not sum repeated click/impression counts or select representative records without evidence that the operation is valid.
- Do not interpret `winner`, `first_place`, or `significance` as independent proof of statistical significance or causal superiority.
- Do not claim that a headline caused better performance based on descriptive CTR differences alone.
- The valid aggregation rule and inferential method remain unresolved pending further investigation.

**Status:** Analysis plan proposed; metric interpretation and inferential method require validation before performance testing.

### Comparison Category and Image-ID Missingness Validation

**Validation performed**

Reviewed the classification rules in `src/classify_comparison_candidates.py` and checked the generated `comparison_candidates.parquet` dataset.

**Results**

- Total experiments: 4,873.
- Experiments with one or more missing image IDs: 5.
- Experiments with partially missing image IDs: 0.
- Headline variation candidates with missing image IDs: 0.

**Decision**

Retain the existing five-category classification for the current audit. The missing-image-ID rule correctly separates the five experiments without recorded image IDs, and no partially missing image-ID experiments were found.

**Limitation**

Recorded image IDs are identifiers, not independent verification of visual content. The classifications identify potential comparisons and do not establish that the intended experimental variable was the only variable changed.

**Status:** Classification logic reviewed and image-ID missingness validated. No code changes required based on these checks.

### Zero-Click and Impression-Imbalance Audit

**Audit performed**

Reviewed zero-click observations, missing and negative click/impression metrics, and the five experiments flagged by the impression-balance diagnostic.

**Zero-click findings**

- Prepared dataset: 22,666 rows.
- Zero-click rows: 12, spanning 7 experiments.
- All 12 zero-click rows have positive impressions.
- No rows have both zero clicks and zero impressions.
- No missing click or impression values were found.
- No negative click or impression values were found.

**Decision:** Retain zero-click observations. Zero clicks with positive impressions are valid outcomes and should not be excluded solely because they have no clicks.

**Impression-imbalance findings**

- `51d1e3934a5d3ff28b0001b0`: 4 normalized headlines, 1 recorded image ID, 0 zero-click rows.
- `51ddbd415d8e6fa6d2006471`: 2 normalized headlines, 1 recorded image ID, 0 zero-click rows.
- `526d4c1c94d1f182f600574f`: 5 normalized headlines, 1 recorded image ID, 2 zero-click rows.
- `52a5cf335de7b1f7a3000e04`: 4 normalized headlines, 1 recorded image ID, 0 zero-click rows.
- `5348bd88fe9c5a1bf500001b`: 1 normalized headline, 9 recorded image IDs, 0 zero-click rows.

**Eligibility implications**

The first four experiments remain headline-comparison candidates under the current structural classification. Their exposure imbalance should be documented and considered in subsequent sensitivity analysis; it is not, by itself, proof of failed randomization or grounds for automatic exclusion.

The fifth experiment is classified as an image-variation candidate rather than a headline-variation candidate and is therefore not eligible for the primary headline-variant comparison.

**Limitations**

The audit does not establish the experiment assignment mechanism, independence of observations, or the recording semantics of repeated metric rows. These issues must be addressed before inferential testing. Impression-balance flags are diagnostic indicators, not proof of experimental failure.

**Status:** Zero-click and impression-imbalance audit complete. No observations were removed and no raw data was modified.

### Eligibility Rules by Analytical Question — Finalized

#### 1. Primary question: Headline-variant CTR comparison

**Structural inclusion criteria**

- At least two distinct normalized headlines within an experiment.
- Exactly one distinct, non-missing recorded image ID.
- No missing image IDs among the experiment's records.

These criteria define the structural candidate cohort. They do not establish that the experiment is eligible for a valid performance comparison.

**Performance eligibility**

Before comparing CTR, establish how repeated records with changing impression and click counts should be interpreted and select a defensible aggregation method. Do not sum repeated metrics, select a representative row, or treat repeated records as independent observations without supporting evidence.

Confirm the experiment's assignment procedure and relevant dependence structure before selecting an inferential test.

#### 2. Secondary analytical questions

| Analytical question | Structural eligibility | Limitation |
|---|---|---|
| Image variation | One normalized headline and multiple distinct recorded image IDs | Image IDs do not independently establish that visual content differs. |
| Mixed variation | Multiple normalized headlines and multiple recorded image IDs | Headline and image effects cannot be isolated from the recorded structure alone. |
| No recorded variation | One normalized headline and one recorded image ID | Not eligible for a variant comparison; retain for descriptive profiling. |
| Missing image ID | Experiments with no recorded image ID | Keep separate from the primary cohort because a consistent recorded image cannot be verified. |
| Zero-click outcomes | Rows with zero clicks and positive impressions | Retain; zero clicks alone are not an exclusion criterion. |
| Impression imbalance | Experiments flagged by the existing diagnostic | Review as a potential sensitivity-analysis concern, not automatic grounds for exclusion. |
| Editorial metadata | Experiments with `winner`, `first_place`, or `significance` fields | Treat as descriptive metadata, not independent proof of statistical significance or causal superiority. |
| Overall CTR | Records with interpretable metrics after aggregation is established | Defer the final calculation until repeated-record semantics and aggregation are resolved. |

#### 3. Exclusion and retention principles

- Exclude image-only, mixed-variation, no-variation, and missing-image-ID experiments from the primary fixed-image headline-comparison cohort.
- Retain those experiments in their separate analytical cohorts or descriptive audits where relevant.
- Retain valid zero-click observations.
- Do not exclude experiments solely because their impressions are imbalanced.
- Do not infer causal superiority from descriptive CTR differences alone.
- Do not use editorial flags as substitutes for independent statistical evidence.

#### 4. Deferred decisions

The following remain unresolved and must be addressed before inferential headline-performance analysis:

1. The recording semantics of repeated stimulus rows with changing metrics.
2. The defensible unit of analysis and metric-aggregation method.
3. The experiment assignment procedure and dependence structure.
4. Minimum-data thresholds for the relevant analytical questions, to be specified in the next audit step.

**Status:** Structural eligibility rules finalized. Performance-level eligibility remains pending resolution of metric interpretation and experimental-design limitations.

### Minimum-Data Rules for Variant Comparisons

**Purpose**

Specify minimum-data criteria before comparing headline performance. These rules address data sufficiency and do not establish statistical power or experimental validity.

**Primary operational threshold**

- Use **100 impressions per variant** as a provisional minimum for the primary descriptive CTR comparison.
- Do not impose a minimum-click requirement. A variant with zero clicks and positive impressions remains a valid observation.
- CTR is undefined when impressions equal zero. The current prepared dataset contains no zero-impression rows.
- Retain below-threshold observations in the prepared data and flag them rather than deleting them.
- Consider sensitivity checks at 500 and 1,000 impressions to assess whether descriptive conclusions depend on the chosen threshold.

**Evidence from the recorded-row audit**

- Total recorded rows: 22,666.
- Rows below 100 impressions: 17.
- Rows below 500 impressions: 21.
- Rows below 1,000 impressions: 41.
- Median recorded-row impressions: 3,122.
- Interquartile range: 2,740–4,091.
- Zero-impression rows: 0.

**Interpretation and limitations**

The 100-impression threshold is an operational data-sufficiency rule, not a universal statistical standard. It does not guarantee adequate power, precise estimates, valid inference, or causal identification. Sensitivity checks at 500 and 1,000 impressions are diagnostic comparisons, not substitutes for a power analysis.

**Status:** Minimum-data policy documented provisionally. Final application to variants is pending resolution of repeated-record metric semantics.

## Phase 2.1 — Item 9: Inclusion and Exclusion Rules

### Primary headline-comparison cohort

**Structural inclusion rules**

An experiment is structurally eligible for the primary headline-variant cohort when all of the following conditions hold:

- It contains more than one distinct normalized headline.
- It contains exactly one distinct recorded image ID.
- It has no packages with missing image IDs.

These rules produce 2,301 structurally eligible experiments out of 4,873 total experiments.

The `primary_headline_structural_eligible` Boolean column records this classification in `comparison_candidates.parquet`.

**Exclusion rules and reasons**

| Condition | Decision | Reason |
|---|---|---|
| One distinct normalized headline | Exclude from headline-variant comparisons | No distinct headline variants are recorded. |
| Multiple recorded image IDs | Exclude from the primary headline-only cohort | Image variation may confound headline comparisons. |
| No recorded image ID or any missing image ID | Exclude from the primary cohort | Consistent image assignment cannot be established from the recorded IDs. |
| Zero clicks with positive impressions | Retain | Zero observed clicks are valid outcomes, not automatically invalid records. |
| Low impressions | Retain in the dataset and flag against the provisional minimum-data rule | Avoid unnecessary data deletion; assess sensitivity separately. |
| High impression imbalance | Flag for review; do not automatically exclude | Imbalance alone does not establish invalidity, but may affect comparability and uncertainty. |
| Repeated stimulus identities with changing metrics | Defer performance analysis until recording semantics are resolved | Do not deduplicate, sum, or select a representative record without a defensible rule. |
| Mixed headline and image variation | Exclude from the primary headline-only cohort; retain for separate analysis | The independent contribution of headline variation cannot be isolated from the recorded structure alone. |
| `winner`, `first_place`, or `significance` metadata | Do not use as independent proof of statistical significance | Their precise meaning and derivation have not been established. |

### Eligibility limitations

Structural eligibility is not equivalent to metric-level or inferential eligibility. The 2,301 experiments are candidates for further review, not a confirmed sample for statistical hypothesis testing.

Before comparing headline performance, the analysis must resolve repeated-record metric semantics, establish a defensible aggregation method, and investigate the experiment assignment and dependence structure. The provisional minimum of 100 impressions per variant, with sensitivity checks at 500 and 1,000 impressions, must be applied only after the analytical variant and its metrics are properly defined. Zero-click variants with positive impressions remain eligible for descriptive analysis.

Image IDs identify recorded values, not verified visual differences. Headline normalization may also leave some edge-whitespace differences unresolved.

### Validation

- Total experiments: 4,873
- Structurally eligible: 2,301
- Not structurally eligible: 2,572
- Eligibility flags are non-null and reconcile to the total experiment count.

The raw CSV remains unchanged. Eligibility decisions are stored in derived analytical data, with unresolved limitations documented rather than silently assumed away.

**Next planned step:** Phase 2.2 — investigate repeated-record semantics and metric construction. Review available documentation and record histories to determine whether repeated stimulus records represent snapshots, corrections, or another recording structure. Do not calculate comparative headline CTRs until a defensible metric-aggregation rule has been established. Experimental assignment and dependence structure must also be investigated before inferential testing.

### Phase 2.2 — Descriptive Headline Feature Patterns

The pooled CTR summaries below describe associations between headline characteristics and click-through rate (CTR) among structurally eligible source records. They are not causal estimates and should not be interpreted as evidence that changing a headline feature would produce the observed difference.

| Headline characteristic | Group | Pooled CTR |
|---|---|---:|
| Question mark | Absent | 1.391% |
| Question mark | Present | 1.097% |
| Exclamation mark | Absent | 1.350% |
| Exclamation mark | Present | 0.941% |
| First-person pronoun | Absent | 1.359% |
| First-person pronoun | Present | 1.279% |
| Third-person pronoun | Absent | 1.268% |
| Third-person pronoun | Present | 1.477% |
| You-family pronoun | Absent | 1.371% |
| You-family pronoun | Present | 1.246% |
| Number | Absent | 1.338% |
| Number | Present | 1.354% |

Headline length also showed descriptive differences:

- Headlines with 85–94 characters had the highest pooled CTR among the four character-length groups (1.422%).
- Headlines with 70 or fewer characters had the lowest pooled CTR (1.269%).
- Headlines with 15–17 words had the highest pooled CTR among the word-count groups (1.370%).
- Headlines with 10 or fewer words had the lowest pooled CTR among the word-count groups (1.277%).

#### Interpretation and limitations

In these pooled summaries, headlines containing question marks or exclamation marks had lower CTR, while headlines containing third-person pronouns had higher CTR. The presence of numbers showed little difference in pooled CTR. These are exploratory patterns, not recommendations to use or avoid particular features.

The summaries pool records across experiments. Differences may reflect experiment composition, audience allocation, exposure levels, repeated-record semantics, or other headline characteristics. The analysis does not establish statistical significance or causal effects. Multiple features may also occur together, so these comparisons do not isolate the independent contribution of any single feature.

The results should be used to identify questions for further investigation, not to claim that a particular punctuation mark, pronoun, number, or headline length causes better performance.

### Phase 2.2 — Descriptive Headline Feature Patterns

The pooled CTR summaries describe associations between headline characteristics and click-through rate (CTR) among structurally eligible source records. They are exploratory, descriptive comparisons—not causal estimates.

| Headline characteristic | Group | Pooled CTR |
|---|---|---:|
| Question mark | Absent | 1.391% |
| Question mark | Present | 1.097% |
| Exclamation mark | Absent | 1.350% |
| Exclamation mark | Present | 0.941% |
| First-person pronoun | Absent | 1.359% |
| First-person pronoun | Present | 1.279% |
| Third-person pronoun | Absent | 1.268% |
| Third-person pronoun | Present | 1.477% |
| You-family pronoun | Absent | 1.371% |
| You-family pronoun | Present | 1.246% |
| Number | Absent | 1.338% |
| Number | Present | 1.354% |

Headline length also showed descriptive differences:

- Headlines with 85–94 characters had the highest pooled CTR among the character-length groups (1.422%); headlines with 70 or fewer characters had the lowest (1.269%).
- Headlines with 15–17 words had the highest pooled CTR among the word-count groups (1.370%); headlines with 10 or fewer words had the lowest (1.277%).

#### Interpretation and limitations

In the pooled summaries, headlines containing question marks or exclamation marks had lower CTR, while headlines containing third-person pronouns had higher CTR. The presence of numbers showed little difference in pooled CTR. These patterns are exploratory and do not establish that changing a headline feature would change performance.

The summaries pool records across experiments. Differences may reflect experiment composition, exposure levels, audience allocation, other headline characteristics, or unresolved repeated-record semantics. Multiple features may occur together, so these comparisons do not isolate the independent contribution of any feature. Statistical significance and causal effects have not been established.

#### Within-experiment headline comparisons

The initial comparison output contains 9,778 headline-variant rows from 2,136 retained experiments. A further 165 structurally eligible experiments were excluded because they contained repeated package identities whose changing impression and click counts have unresolved semantics. The analysis did not deduplicate those records, sum their metrics, or select a latest record without supporting evidence.

The output compares each retained package's CTR with the CTR of the other retained package records in its experiment. The differences are descriptive. Valid causal interpretation would require documented assignment procedures and justified assumptions about the observations.

The results identify questions for further investigation; they do not establish that a particular punctuation mark, pronoun, number, or headline length causes better performance.

### Phase 2.3 — Assignment Procedure and Dependence Investigation

#### Assignment procedure

The official Upworthy Research Archive documentation states that viewers were randomly assigned to packages within each experiment. A package represents an experimental arm, and the recorded impressions and clicks are aggregate counts of assigned viewers and viewers who clicked, respectively. The dataset does not contain individual-level viewer records.

The archive also documents potential randomization problems for tests conducted between June 25, 2013, and January 10, 2014. This concern is distinct from exposure-imbalance flags calculated during this project.

#### Dependence and repeated-record limitations

The local exploratory dataset contains 22,666 source records across 4,873 experiments and 19,171 constructed package identities. Repeated identities have differing impression counts, click counts, or both. The source-record generation process and the statistical meaning of these repeated records remain unresolved.

Consequently, the intended randomized assignment procedure is documented, but the independence and aggregation assumptions required for inference on the retained comparison dataset are not fully established. Repeated records must not be deduplicated, summed, or treated as independent observations without further evidence.

#### Decision

Carry the documented random-assignment design forward as supporting evidence, not as proof that every row in the current analysis is an independent experimental arm. Preserve the exclusion of the 165 experiments with repeated package identities from the current comparison output. Proceed to define the comparison unit and inferential method before running statistical tests.

Sources: Upworthy Research Archive documentation and Matias et al. (2021), *The Upworthy Research Archive, a time series of 32,487 experiments in U.S. media*.

## Phase 2.2 — Descriptive Performance Analysis

### Objective

Describe headline click-through-rate (CTR) performance, compare headline variants within eligible experiments, quantify exposure differences, and explore associations between headline text features and CTR. These analyses are descriptive and exploratory; they do not establish that individual headline features cause higher or lower CTR.

### 1. Overall CTR distribution

The exploratory dataset contains 22,666 source records across 4,873 experiments.

| Metric | Result |
|---|---:|
| Pooled CTR (total clicks / total impressions) | 1.5196% |
| Mean source-row CTR | 1.5754% |
| Median source-row CTR | 1.2537% |
| Standard deviation | 1.229 percentage points |
| 25th percentile | 0.746% |
| 75th percentile | 2.028% |
| 95th percentile | 4.003% |
| 99th percentile | 6.076% |
| Maximum source-row CTR | 13.606% |
| Source rows with zero clicks | 12 |
| Source rows with CTR above 5% | 502 |

The pooled CTR differs from the unweighted mean and median because the calculations weight observations differently. The pooled CTR gives greater influence to packages with more impressions, while the unweighted statistics summarize the distribution of source-row CTRs.

### 2. Eligible headline comparisons

The structural eligibility audit identified 2,301 experiments with multiple distinct headlines, one shared image ID, and no missing image IDs. Repeated package identities created an additional comparability concern.

The comparison output excludes the 165 eligible experiments containing repeated package identities. The resulting dataset contains:

- 2,136 retained experiments.
- 9,778 retained package-level headline comparisons.
- No missing required columns in the validation check.
- Passing checks for package CTR, other-headlines CTR, CTR difference, relative CTR difference, and multiple distinct raw headlines per experiment.

For each retained package, performance was compared with the other retained package records in the same experiment. The output contains `package_ctr`, `other_headlines_ctr`, `ctr_difference_percentage_points`, and `relative_ctr_difference_pct`.

The absolute CTR difference has a standard deviation of approximately 0.528 percentage points, a median

### Phase 2.3 — Sensitivity Check: Excluding Exposure-Imbalance-Flagged Experiments

The primary inference analysis included 2,136 experiments. The exposure-balance audit identified five experiments flagged for exposure imbalance; three of these were present in the primary comparison dataset and were excluded for this sensitivity check.

The sensitivity analysis reran the six within-experiment headline-feature comparisons after excluding those three experiments. The same two-proportion testing approach, Benjamini–Hochberg correction across the sensitivity test family, and experiment-level bootstrap procedure with 10,000 replicates were used.

| Headline feature | Primary mean CTR difference (pp) | Sensitivity mean CTR difference (pp) | Sensitivity bootstrap 95% CI (pp) |
|---|---:|---:|---:|
| Question mark | -0.1329 | -0.1333 | [-0.1632, -0.1032] |
| Exclamation mark | -0.1558 | -0.1566 | [-0.2212, -0.0932] |
| Number | 0.0629 | 0.0633 | [0.0265, 0.1006] |
| You-family pronoun | 0.0164 | 0.0161 | [-0.0143, 0.0470] |
| First-person pronoun | 0.0063 | 0.0091 | [-0.0209, 0.0392] |
| Third-person pronoun | 0.1064 | 0.1059 | [0.0728, 0.1392] |

The mean effects changed only slightly after exclusion. The bootstrap confidence intervals remained entirely below zero for question marks and exclamation marks, entirely above zero for numbers and third-person pronouns, and included zero for you-family and first-person pronouns. The counts of BH-significant experiment-feature tests also remained unchanged from the primary analysis.

These results indicate that the aggregate patterns are robust to excluding the three exposure-imbalance-flagged experiments present in the comparison dataset. This check does not establish that the remaining experiments were randomly assigned or that observations are independent. It does not establish causal effects.

Outputs:
- `data/processed/phase23_sensitivity_tests.csv`
- `data/processed/phase23_sensitivity_summary.csv`

### Phase 2.3 — Assignment Procedure and Dependence

#### What the documentation establishes

The Upworthy Research Archive documentation and its 2021 research paper describe a randomized online experiment design. Readers were randomly assigned to headline-and-image packages within an experiment. The dataset records aggregate impressions and clicks for each package rather than individual-level viewer data.

The documentation also identifies a period from June 25, 2013, to January 10, 2014, in which experiments were flagged for possible randomization problems. Editors monitored experiment results and exercised judgment over when to stop experiments.

Sources:
- Matias et al. (2021), *The Upworthy Research Archive, a time series of 32,487 experiments in U.S. media*, Scientific Data.
- Upworthy Research Archive, “Data in the Upworthy Research Archive.”

#### Implications for this analysis

The original experiment randomized readers to packages, not to individual linguistic features such as question marks, numbers, or pronouns. Our feature comparisons group packages by whether a feature is present or absent. Consequently, differences in CTR are observational associations between headline characteristics and outcomes within experiments; they do not isolate the causal effect of a single feature.

The aggregate dataset does not provide viewer identifiers. We therefore cannot verify whether the same viewers participated in multiple experiments or directly test independence across experiments. We also cannot verify the randomization procedure for each retained experiment using individual assignment records.

The two-proportion tests treat clicks as binomial outcomes and rely on independence assumptions. Their p-values should therefore be interpreted cautiously, particularly because headline variants may differ in several characteristics simultaneously and because experiment-level randomization concerns are documented in the source.

The experiment stopping process was managed operationally by editors. The available documentation does not establish that all experiments used fixed, prespecified sample sizes. This is an additional limitation when interpreting nominal significance tests.

#### Decision

Report the Phase 2.3 results as exploratory, within-experiment associations. Do not claim that any individual headline feature causes higher or lower CTR.

The sensitivity analysis excluding the three exposure-imbalance-flagged experiments present in the comparison dataset produced materially unchanged aggregate estimates. This supports robustness to those three exclusions but does not resolve the broader limitations concerning assignment, dependence, or causal interpretation.

No fixed-effects model, clustered-standard-error analysis, winner's-curse adjustment, or additional sensitivity analysis was performed, in accordance with the project scope.

### Phase 2.3 — Within-Experiment Inference: Results and Limitations

#### Analysis scope

The analysis used 9,778 eligible headline-variant comparison rows across 2,136 experiments. Experiments with unresolved repeated-package identities and changing impression/click counts had already been excluded from the comparison dataset.

Six binary headline features were evaluated using within-experiment comparisons of CTR for feature-present versus feature-absent variants. The reported effect is the mean experiment-level CTR difference, in percentage points (pp). Positive values indicate higher CTR for variants containing the feature; negative values indicate lower CTR.

Two-proportion tests were performed within each eligible experiment-feature combination. Benjamini–Hochberg correction was applied across the complete primary family of 5,280 tests. Bootstrap 95% confidence intervals were estimated by resampling experiment-level effects 10,000 times, giving each tested experiment equal weight in the mean.

#### Aggregate findings

| Headline feature | Experiments tested | Mean CTR difference (pp) | Bootstrap 95% CI (pp) | Median difference (pp) | BH-significant experiment-feature tests |
|---|---:|---:|---:|---:|---:|
| Question mark | 981 | -0.1329 | [-0.1622, -0.1029] | -0.0968 | 233 |
| Exclamation mark | 184 | -0.1558 | [-0.2212, -0.0921] | -0.1347 | 39 |
| Number | 695 | 0.0629 | [0.0266, 0.1002] | 0.0334 | 161 |
| You-family pronoun | 1,162 | 0.0164 | [-0.0140, 0.0473] | -0.0045 | 246 |
| First-person pronoun | 1,095 | 0.0063 | [-0.0243, 0.0363] | -0.0069 | 247 |
| Third-person pronoun | 1,163 | 0.1064 | [0.0726, 0.1400] | 0.0629 | 286 |

The significant-test column counts individual experiment-feature tests with BH-adjusted p-values below 0.05. These are not counts of independently established causal effects.

#### Sensitivity check

Five experiments were flagged for exposure-imbalance review in the separate balance audit. Three were present in the comparison dataset and were excluded in the sensitivity analysis.

The aggregate results changed very little after exclusion. The direction of every mean effect remained the same, and the bootstrap intervals remained below zero for question marks and exclamation marks, above zero for numbers and third-person pronouns, and overlapping zero for you-family and first-person pronouns. BH-significant test counts were unchanged.

This indicates that the reported aggregate patterns are not materially driven by those three flagged experiments. It does not resolve broader questions about assignment quality or dependence.

#### Interpretation

The analysis finds exploratory within-experiment associations between several headline features and CTR:

- Question marks and exclamation marks were associated with lower CTR on average.
- Numbers and third-person pronouns were associated with higher CTR on average.
- The mean effects for you-family and first-person pronouns were small, and their bootstrap intervals included zero.

These are associations, not isolated feature effects. Headlines can differ in multiple ways simultaneously, so the results do not establish that adding or removing a feature would cause the observed CTR difference.

#### Assumptions and limitations

1. **Assignment:** The source describes randomized assignment to headline-and-image packages, but the available aggregate records do not permit verification of assignment for every retained experiment.
2. **Dependence:** Viewer-level records and identifiers are unavailable. Independence across viewers and experiments cannot be directly verified.
3. **Test assumptions:** Two-proportion tests rely on binomial-outcome and independence assumptions. Violations may affect p-values.
4. **Multiple comparisons:** BH correction reduces false-discovery risk across the tested family but does not correct model misspecification, dependence, or confounding.
5. **Experiment selection and stopping:** Operational experiment stopping and documented randomization concerns limit how broadly the results should be generalized.
6. **Winner's curse:** No held-out re-estimation or shrinkage adjustment was performed. Selected large effects may be overstated.
7. **Feature confounding:** The analysis does not isolate a feature's causal effect from other headline characteristics or package differences.
8. **Exposure imbalance:** The sensitivity check excluded the three flagged experiments present in the analysis, but this does not establish that all remaining experiments were well randomized.

#### Decision

Treat these findings as exploratory evidence of within-experiment associations. Do not present them as causal recommendations for headline writing.

Excluded by project scope: fixed-effects models with clustered standard errors, winner's-curse adjustment, and expanded sensitivity analyses.

#### Outputs

- `data/processed/phase23_within_experiment_tests.csv`
- `data/processed/phase23_feature_summary.csv`
- `data/processed/phase23_sensitivity_tests.csv`
- `data/processed/phase23_sensitivity_summary.csv`


## Phase 2.4 — ML Modeling

### Item 1: Target definition and cohort validation

The modeling target is binary. For each headline variant, its CTR is compared with the pooled CTR of all other variants in the same experiment:

\[
\text{Relative CTR}_i =
\frac{\text{clicks}_i}{\text{impressions}_i}
-
\frac{\text{other clicks}_i}{\text{other impressions}_i}
\]

The target is `1` when the relative CTR is positive and `0` otherwise. The comparison uses pooled clicks and impressions for the other variants, rather than an unweighted average of their individual CTRs.

The source comparison dataset contains 9,778 rows across 2,136 experiments. All package IDs were matched to source metadata, and all comparison rows matched their source experiment ID and headline.

Headline-only eligibility was operationally defined as at least two distinct normalized headlines and exactly one distinct image ID per experiment. All 2,136 comparison experiments passed this rule.

The target was reconstructed from the underlying click and impression counts. It agreed with both existing CTR-difference columns for all 9,778 rows.

Target distribution:

| Target | Rows | Proportion |
|---|---:|---:|
| 0 — Does not beat the rest-of-experiment CTR | 5,120 | 52.36% |
| 1 — Beats the rest-of-experiment CTR | 4,658 | 47.64% |
| Total | 9,778 | 100% |

The validated target dataset is saved at `data/processed/phase24_modeling_targets.csv`.

### Item 2: Headline feature construction

The Phase 2.2 engineered features were combined with headline text for TF-IDF feature extraction.

The six binary features are:

- `contains_question_mark`
- `contains_exclamation_mark`
- `contains_number`
- `contains_you_family`
- `contains_first_person_pronoun`
- `contains_third_person_pronoun`

The TF-IDF configuration uses lowercased text, English stop-word removal, unigrams and bigrams, `min_df=2`, a maximum vocabulary size of 5,000, and sublinear term frequency.

Validation confirmed 9,778 matched rows, 2,136 experiments, six binary features, a 5,000-term TF-IDF vocabulary, and a combined sparse feature matrix with 5,006 columns. The row-level dataset is saved at `data/processed/phase24_modeling_features.csv`.

The full-data TF-IDF fit was used only as a construction smoke test. It is not a valid basis for performance evaluation. Model evaluation must fit the vectorizer within each training fold to prevent vocabulary leakage.

### Modeling safeguards and limitations

- Clicks, impressions, CTRs, and CTR-difference columns are used to construct or audit the target, not as predictors.
- Experiment IDs are grouping variables, not predictive features.
- Outcome and editorial fields, including `winner`, `significance`, `first_place`, `lede`, `excerpt`, and `share_text`, must not enter the predictor matrix.
- The one-image rule is an operational definition of headline-only experiments; it does not establish that every other experimental condition was identical.
- No predictive performance results have been calculated yet.
