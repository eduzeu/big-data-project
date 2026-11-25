# life_national_mortality

This dataset contains 85,400 rows and 8 columns. Each row records a national mortality-rate cell by gender, age at death, year of death and household income percentile. The CSV covers ages 40–76. Income is measured two years before mortality for ages 40–63, and at age 61 for ages 64–76. The lag column records the years between income and mortality measurement. mortrate is the mortality rate; count is its beginning-of-year population denominator; hh_inc is mean household income. To protect confidentiality, rates corresponding to one or two deaths are recoded to reflect three deaths. These mortality cells are distinct from derived life-expectancy estimates.

Source: supplied `health_ineq_online_table_15_readme.pdf, page 1`.

Status: manually reviewed against the table documentation. This is a reference correction, not a paper-only generated result. It is excluded from generation inputs and from claims about model accuracy.
