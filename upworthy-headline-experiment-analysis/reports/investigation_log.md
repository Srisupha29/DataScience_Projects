# Upworthy Headline Experiment Analysis
## Data Investigation Log

**Project phase:** Phase 1: Data Understanding and Profiling  
**Status:** Phase 1 closeout under review; documentation reconciliation pending.
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
- Experiments with multiple distinct headlines: 2,607 (53.5%)
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

1. **Headline variation:** 2,607 experiments have multiple distinct headlines, representing approximately 53.5% of all experiments.
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

### Phase 1 Completion Criteria

Phase 1 is ready for review when:

- [ ] The dataset schema and row-level unit are documented.
- [ ] Missing values and basic data-quality checks are documented.
- [ ] Experiment structure and headline/image variation are documented.
- [ ] Analytical limitations and open questions are recorded.
- [ ] The raw data remains unchanged.

### Phase 1 Status

**Status: Pending final documentation reconciliation and validation.**

The initial investigations and analytical-dataset validation are complete. Finalize the investigation log by reconciling historical raw-text counts with current normalized-headline classifications, verifying image-ID missingness wording, and confirming that the documented next step matches the current workflow. Unresolved questions about repeated records and experimental design remain explicit limitations.

## Phase 1 completion criteria

Phase 1 is complete when:

- The schema and principal identifiers are understood.
- The unit of observation is documented.
- Basic engagement-count checks are complete.
- Missingness and variation patterns are quantified.
- The distinction between descriptive findings and causal conclusions is explicit.
- A data dictionary and initial data-quality report are available.
- The remaining structural questions have been investigated sufficiently to justify the next phase.

**Next planned step:** Begin Phase 2.1 with an eligibility audit using the current analytical datasets and `src/classify_comparison_candidates.py`. Define which experiments are suitable for each descriptive comparison, document diagnostic flags and exclusions, and retain unresolved experimental-design questions. Do not make causal or inferential claims until the assumptions and analysis method are justified.

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