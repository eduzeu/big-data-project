# Nine-dataset validation

All nine additional datasets completed CSV-only baseline and paper-supported generation. The existing pilot was also rerun. All 18 offline tests pass. Samples, content profiles, semantic profiles, dimensions, CSV checksums and grounded-code checksums match for every pair. No codebook, README or Stata content was supplied to generation.

These checks establish execution and provenance, not factual accuracy. The post-run codebook audit found substantive errors or ambiguity in five descriptions, partial support/coverage in two, and consistency for the limited claims checked in two. This is a development audit, not a blinded benchmark.

| Dataset | Rows × columns | Audit |
|---|---:|---|
| inventors_college | 423 × 17 | needs revision |
| atlas_county_covariates | 3,221 × 35 | checked claims consistent |
| inventors_childhood_cz | 741 × 140 | needs revision |
| life_national_mortality | 85,400 × 8 | needs revision |
| atlas_county_outcomes | 3,219 × 64 | checked claims consistent |
| race_cz_income | 741 × 21 | partial support |
| race_national_statistics | 100 × 69 | partial support |
| college_access_mobility | 2,202 × 15 | needs revision |
| college_characteristics | 2,463 × 49 | needs revision |

## Adjustment wording

The blanket claim that estimates are adjusted is now rejected in fact validation and sentence rendering. Prompts preserve the scope of the paper’s adjusted estimates. Exact adjusted/unadjusted field mappings cannot be established by the main paper alone. The separately reviewed [pilot description](pilot_reviewed_description.md) states that the CSV includes both race-adjusted and unadjusted estimates and standard errors, based on its held-out codebook.

The default-query pilot and a rerun using the original query both avoided the blanket adjustment wording, but introduced other semantic errors. Both outputs are preserved; neither is presented as a validated complete description.

## Main findings

**inventors_college**: Generated college attendance at age 20; table codebook defines institution attended for the greatest amount of time in the four calendar years when the child turned 19-22. Generated definition concerns highly-cited patents; the table codebook defines highly-cited inventors as the top 5% of inventors by citations within birth cohort.

**atlas_county_covariates**: The three stated measures, periods and sources agree with the held-out codebook. This is a limited claim audit, not complete schema coverage.
Coverage: Description covers only three of the 35 fields. Inherited folder label says Table 12; supplied codebook calls this Table 10.

**inventors_childhood_cz**: Claims parents are not inventors; the supplied table codebook does not impose that restriction. Claims CZs with fewer than 1,000 children are excluded; table codebook states cells with fewer than 250 children are omitted. Describes child-level assignments without clearly stating one row per childhood CZ.

**life_national_mortality**: Age 63 is placed in both income-measurement categories. Codebook and observed lag field establish a two-year lag for ages 40-63, and income at age 61 for ages 64-76. Conflates paper-level life expectancy adjustment/extrapolation with the observed mortality table; this CSV contains ages 40-76 only. Adds unsupported promotional wording about enhancing reliability.

**atlas_county_outcomes**: Limited claim consistency, not a complete table description.
Coverage: Only the incarceration definition is explained; parent income at percentile 25, income outcomes, and 1978-1983 cohorts are omitted. Inherited folder label says Table 4; supplied codebook calls this Table 2.

**race_cz_income**: Limited checked claims agree with the codebook.
Coverage: Parent percentile 75, household income ranks and population fields are omitted. Age-based assignment, proportional exposure and measurement-age statements require checking the referred paper sections; the table codebook alone does not establish them.

**race_national_statistics**: Description focuses on a regression-based study method; the CSV is percentile-level outcome summaries, so it does not clearly explain the stored measurements.
Coverage: Does not identify the 1978-1983 cohorts or explain the outcome columns. Does not explicitly state one row per parent income percentile.

**college_access_mobility**: Mobility-rate wording leaves the denominator ambiguous and can be read as the conditional success rate. mr_kq5_pq1 is the percent of all students with bottom-quintile parents AND top-quintile adult income; kq5_cond_parq1 is the separate conditional rate.
Coverage: Only one measure is explained; access rates, median incomes, trends and college assignment are omitted.

**college_characteristics**: Calls exp_instr instructional expenditure per student; supplied codebook describes Total Instructional Expenditures, so the unit/denominator mapping is not established. Calls asian_or_pacific_share_fall_2000 an Asian share, omitting Pacific Islanders.
Coverage: Emphasizes 2000 and omits the 2013 measures and college-group row definition.

## Next implementation work

Add table-specific evidence selection and a final claim-to-fact support check. Preserve measurement units and denominators, prevent study-wide definitions from becoming CSV fields, and resolve paper/codebook version mismatches. Do not report the current model-based review as a semantic accuracy guarantee.

Detailed audit: [dataset_audit.json](dataset_audit.json). Input/code provenance and generated descriptions: [dataset_validation_summary.json](dataset_validation_summary.json). Full requests, provider responses, retrieved passages, logs and baseline descriptions remain in the local `results/dataset_validation` directory.
