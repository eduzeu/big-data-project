# Paired description comparison

Compared all ten original CSV baselines with the revised paper-only and documentation-assisted outputs. Two previously flagged documented cases received one fresh verification run each under unchanged generation code; both prior outputs are preserved. The fresh outputs are selected regardless of whether they look better. Curated reference descriptions receive no model-performance credit.

## Focused source-based review

Four prewritten targets per dataset give 40 checks per condition. Annotations were prepared by Codex from the supplied documentation and CSV, with no independent human rater or blinding. This is a development comparison, not an overall accuracy score.

| Condition | supported | partial | omitted | incorrect | ambiguous | abstained |
|---|---:|---:|---:|---:|---:|---:|
| csv_baseline | 7 | 5 | 20 | 7 | 1 | 0 |
| strict_paper_only | 5 | 3 | 8 | 0 | 0 | 24 |
| documentation_assisted | 33 | 1 | 5 | 0 | 1 | 0 |

Supported means the full target is clearly expressed; partial means valid but incomplete. Omitted and abstained are separate from incorrect or ambiguous. Abstention counts refer to target checks, not datasets: six paper-only dataset abstentions produce 24 abstained targets.

## What changed

- Baseline errors include treating CZs as cities, income quartiles as calendar quarters, bottom income quintile as a quartile, and mortality cells as individual records.
- The documented outputs explain the mortality denominator and age-specific income lag, both adjustment statuses and standard errors, and adult income-rank fields much more explicitly.
- The paper-only condition remains cautious: four datasets have approved semantic claims and six abstain. Its supported claims do not imply complete table descriptions.
- In the fresh childhood-inventor run, both misleading highly-cited-patent claims disappear. The correct highly-cited-inventor definition is still omitted, so this is not counted as a fully corrected definition.
- In the fresh mobility run, the joint mobility share uses the bottom-parent AND top-child events over students, while the conditional rate is defined separately. The median-income sentence remains ambiguous about household time averaging versus the college-level median.
- Expenditure review respects both actual column families: `exp_instr_*` totals and `exp_instr_pc_*` per-student fields. The former audit’s broader claim that per-student wording was necessarily wrong is not reused.

## Per-dataset target counts

Cells show supported / partial / omitted / incorrect / ambiguous / abstained, in that order.

| Dataset | CSV baseline | Strict paper-only | Documented |
|---|---|---|---|
| inventors_college | 1 / 0 / 2 / 1 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 4 | 3 / 0 / 1 / 0 / 0 / 0 |
| inventors_childhood_cz | 0 / 1 / 2 / 1 / 0 / 0 | 1 / 0 / 3 / 0 / 0 / 0 | 3 / 0 / 1 / 0 / 0 / 0 |
| atlas_county_covariates | 2 / 0 / 1 / 1 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 4 | 3 / 0 / 1 / 0 / 0 / 0 |
| atlas_county_outcomes | 1 / 0 / 2 / 0 / 1 / 0 | 0 / 0 / 0 / 0 / 0 / 4 | 4 / 0 / 0 / 0 / 0 / 0 |
| life_national_mortality | 0 / 1 / 2 / 1 / 0 / 0 | 0 / 2 / 2 / 0 / 0 / 0 | 4 / 0 / 0 / 0 / 0 / 0 |
| life_county_expectancy | 1 / 0 / 2 / 1 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 4 | 4 / 0 / 0 / 0 / 0 / 0 |
| race_national_statistics | 0 / 1 / 3 / 0 / 0 / 0 | 1 / 1 / 2 / 0 / 0 / 0 | 4 / 0 / 0 / 0 / 0 / 0 |
| race_cz_income | 1 / 0 / 2 / 1 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 4 | 3 / 1 / 0 / 0 / 0 / 0 |
| college_access_mobility | 1 / 1 / 1 / 1 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 4 | 3 / 0 / 0 / 0 / 1 / 0 |
| college_characteristics | 0 / 1 / 3 / 0 / 0 / 0 | 3 / 0 / 1 / 0 / 0 / 0 | 2 / 0 / 2 / 0 / 0 / 0 |

## Interpretation limits

- Focused checks are correlated and incomplete; counts are not overall factual accuracy.
- Development cases were inspected previously; there is no blind holdout or independent human rater.
- Documentation-assisted agreement is source consistency because the same documentation was a model input.
- Generation models, prompts, retrieval, review stages and output lengths differ; this is not a single-component ablation or a matched-token-budget experiment.
- One fresh run per flagged case is insufficient to estimate repeatability or variance.

Detailed judgments and rationales: `evaluation/annotations.json`. Full selected descriptions, input/output hashes and source locations: `comparison.json`. These artifacts preserve the distinction between model drafts and the separately reviewed reference descriptions.
