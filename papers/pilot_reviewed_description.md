# County life expectancy: reviewed wording

This dataset contains 1,559 county observations and 49 columns. It reports life expectancy at age 40 for men and women in each quartile of the national income distribution. **Both race-adjusted and unadjusted estimates are included**, along with their standard errors. The `le_raceadj_*` fields contain race-adjusted point estimates; `le_agg_*` fields contain unadjusted point estimates. The `sd_le_*` fields are standard errors, despite the `sd` prefix. Estimates are reported only for counties with populations larger than 25,000. County, state and commuting-zone identifiers and population fields provide geographic context; the rows themselves are counties.

Source: supplied `health_ineq_online_table_11_readme.pdf`, pages 1–2.

This is a manually reviewed correction using the held-out codebook. It is kept separately from generated descriptions and is not counted as a paper-only model result. The main article does not establish the unadjusted column mapping by itself.
