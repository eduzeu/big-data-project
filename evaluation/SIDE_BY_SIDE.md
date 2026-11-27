# Side-by-side outputs

These are generated descriptions, not the corrected reference text. Sources and condition labels are preserved.

## inventors_college

### csv_baseline

This dataset contains information from 423 educational institutions, detailing various metrics related to their patent activities. Each entry includes a unique identifier for the institution, the institution's name, and counts of patents filed over five different periods. Additionally, it provides insights into the number of inventors associated with these patents and their citation metrics. The dataset features a range of values for total patents and total citations, highlighting the varying levels of innovation across institutions. The semantic profile indicates that the data is primarily used for measurement and aggregation, making it valuable for analyzing trends in educational patenting.

### strict_paper_only

This dataset contains 423 rows and 17 columns.

No table-specific semantic claim passed both evidence reviews. Field meanings remain unresolved from the available paper evidence.

### documentation_assisted

This dataset contains 423 rows and 17 columns.

Each row represents a college attended by students in the sample. [documentation:inventors_college:p1:w180] [documentation:inventors_college:p2:w0]

The count column reports the number of students assigned to each college. [documentation:inventors_college:p2:w0]

The count_pq1 to count_pq5 columns report the number of students at each college whose parents are in each income quintile. [documentation:inventors_college:p2:w0]

The inventor column gives the share of students at each college who are inventors. [documentation:inventors_college:p2:w0]

The inventor_pq1 to inventor_pq5 columns give the share of students with parents in each income quintile who are inventors at each college. [documentation:inventors_college:p2:w0]

The total_patents and total_cites columns report the total number of patents granted to students and total patent citations obtained by students at each college. [documentation:inventors_college:p2:w0]

### Target judgments

| Target | Baseline | Strict paper | Documented |
|---|---|---|---|
| college row unit | supported | abstained | supported |
| inventor shares and patent/citation totals rather than counts of filings in five periods | incorrect | abstained | supported |
| parent income quintiles | omitted | abstained | supported |
| college assigned by most attendance in ages 19-22 | omitted | abstained | omitted |

## inventors_childhood_cz

### csv_baseline

This dataset contains 741 rows and 140 columns, focusing on various metrics related to cities across the United States. It includes unique identifiers for cities, state names, and abbreviations, along with numerical values such as kid counts and inventor metrics. The dataset features a range of measurements, with some columns representing general numerical values and others specifically related to inventor categories. Notably, the data includes spatial information at both city and state levels, enhancing its utility for geographic analysis. Missing values are present in several columns, indicating areas for potential data improvement.

### strict_paper_only

This dataset contains 741 rows and 140 columns.

Each row in the table represents a childhood commuting zone (CZ), identified by par_cz, par_czname, par_state, and par_stateabbrv. [inventors:p46:w0] [inventors:p46:w180] [inventors:p59:w0]

### documentation_assisted

This dataset contains 741 rows and 140 columns.

Each row in this table represents children born 1980-1984 assigned to a specific childhood commuting zone (CZ), identified by par_cz, par_czname, par_state, and par_stateabbrv. [documentation:inventors_childhood_cz:p1:w0] [documentation:inventors_childhood_cz:p1:w180] [documentation:inventors_childhood_cz:p2:w0]

The variable kid_count gives the number of children in each CZ cohort; cells with fewer than 250 children are omitted. [documentation:inventors_childhood_cz:p1:w180] [documentation:inventors_childhood_cz:p2:w0]

The inventor column reports the share of children in each CZ who go on to become inventors, defined as being listed on a patent application (2001–2012) or grant (1996–2014). [documentation:inventors_childhood_cz:p1:w0] [documentation:inventors_childhood_cz:p2:w0]

Columns inventor_cat_1 through inventor_cat_7 report the share of children who patent in each of seven technology categories, assigned by the category in which they patent most often. [documentation:inventors_childhood_cz:p1:w180] [documentation:inventors_childhood_cz:p2:w0]

Variables with the _g_m and _g_f suffixes restrict the sample to males and females, respectively, for each outcome. [documentation:inventors_childhood_cz:p2:w0]

Variables with the _pq_1 to _pq_5 suffixes restrict the sample to children whose parental income is in the corresponding quintile of the parent income distribution for their birth cohort. [documentation:inventors_childhood_cz:p2:w0] [documentation:inventors_childhood_cz:p2:w180]

### Target judgments

| Target | Baseline | Strict paper | Documented |
|---|---|---|---|
| childhood CZ row unit rather than cities | incorrect | supported | supported |
| share of children becoming inventors | partial | omitted | supported |
| parent income quintiles | omitted | omitted | supported |
| highly cited inventor ranking rather than patent ranking | omitted | omitted | omitted |

## atlas_county_covariates

### csv_baseline

This dataset contains 3,221 rows and 35 columns, providing a comprehensive overview of various socio-economic and demographic factors across different counties and cities in the United States. Key metrics include median household income, poverty rates, educational attainment, and population demographics from 1990 to 2016. The dataset also features commuting times and job growth statistics, offering insights into transportation and employment trends. Each column represents specific measurements related to location, financial metrics, and demographic statistics, making it a valuable resource for analyzing regional disparities and trends over time.

### strict_paper_only

This dataset contains 3,221 rows and 35 columns.

No table-specific semantic claim passed both evidence reviews. Field meanings remain unresolved from the available paper evidence.

### documentation_assisted

This dataset contains 3,221 rows and 35 columns.

Each row reports county-level neighborhood characteristics, uniquely identified by 2010 FIPS state and county codes. [documentation:atlas_county_covariates:p1:w0]

The mean household income in 2000 is reported for each county, based on the 2000 Decennial Census. [documentation:atlas_county_covariates:p2:w0]

The share of people aged 25+ with a college degree or higher is reported for 2000 and 2010, using Census and ACS data. [documentation:atlas_county_covariates:p2:w0]

The share of foreign-born residents in 2010 is calculated as the number of foreign-born divided by the total population (native plus foreign-born). [documentation:atlas_county_covariates:p1:w0]

Median household income is reported for 1990 and 2016, using the 1990 Census and 2012-2016 ACS, respectively. [documentation:atlas_county_covariates:p2:w180]

The share of individuals below the federal poverty line is reported for 1990, 2000, and 2010, using Census and ACS data. [documentation:atlas_county_covariates:p3:w0]

Racial and ethnic shares for White, Black, Hispanic, and Asian populations are reported for 2000 and 2010, with non-Hispanic race categories. [documentation:atlas_county_covariates:p3:w0]

### Target judgments

| Target | Baseline | Strict paper | Documented |
|---|---|---|---|
| county row unit rather than mixed counties/cities | incorrect | abstained | supported |
| income and poverty measures | supported | abstained | supported |
| variable-specific measurement periods | supported | abstained | supported |
| generally population-weighted tract aggregation with exceptions | omitted | abstained | omitted |

## atlas_county_outcomes

### csv_baseline

This dataset contains 3,219 rows and 64 columns, focusing on various demographic and criminal justice metrics across different states and counties in the United States. It includes data on key variables such as the percentage of individuals in different racial and ethnic groups, as well as jail statistics, providing insights into the intersection of race and incarceration. The dataset features unique identifiers for states, counties, and cities, allowing for detailed spatial analysis. Additionally, it includes measurements related to gender and race, making it a valuable resource for understanding demographic trends and disparities in the criminal justice system.

### strict_paper_only

This dataset contains 3,219 rows and 64 columns.

No table-specific semantic claim passed both evidence reviews. Field meanings remain unresolved from the available paper evidence.

### documentation_assisted

This dataset contains 3,219 rows and 64 columns.

Each row reports predicted outcomes for children born 1978-1983 by county, race (Pooled, White, Black, Hispanic), and gender (Pooled, Male, Female). [documentation:atlas_county_outcomes:p1:w0] [documentation:atlas_county_outcomes:p1:w180]

The variable kfr_[race]_[gender]_p25 gives the mean household income rank in adulthood for children whose parents were at the 25th percentile of the national income distribution. [documentation:atlas_county_outcomes:p1:w180]

Children's incomes are measured as mean household earnings in 2014-2015, when they were ages 31-37, and household income includes own and spouse’s income. [documentation:atlas_county_outcomes:p1:w180]

The variable jail_[race]_[gender]_p25 is the fraction of children born 1978-1983 with parents at the 25th percentile of national income who were incarcerated on April 1, 2010. [documentation:atlas_county_outcomes:p2:w0]

Incarceration is defined as residing in a federal detention center, federal prison, state prison, local jail, residential correctional facility, military jail, or juvenile correctional facility. [documentation:atlas_county_outcomes:p2:w0]

The variables kfr_[race]_[gender]_p25_se and jail_[race]_[gender]_p25_se report estimated standard errors for the corresponding outcome variables, incorporating both sampling error and privacy noise. [documentation:atlas_county_outcomes:p1:w0] [documentation:atlas_county_outcomes:p2:w0]

The variables [race]_[gender]_count give the estimated number of children under 18 living in the county with parents whose household income was below the national median, based on the 2000 Census. [documentation:atlas_county_outcomes:p2:w0]

### Target judgments

| Target | Baseline | Strict paper | Documented |
|---|---|---|---|
| county row unit rather than mixed city/state rows | ambiguous | abstained | supported |
| household income rank conditional on parent percentile 25 | omitted | abstained | supported |
| race and gender groupings | supported | abstained | supported |
| incarceration measured April 1, 2010 | omitted | abstained | supported |

## life_national_mortality

### csv_baseline

This dataset contains 85,400 rows and 8 columns, providing insights into various demographic and financial metrics. It includes information on individuals, such as gender, age, and household income, as well as mortality rates and percentile rankings. The age of individuals ranges from 40 to 76 years, with a mean age of approximately 55. The dataset spans years from 2001 to 2014, capturing temporal trends. Key metrics include a mean household income of about $97,996 and a mortality rate with a mean of 0.0061. The data is valuable for analyzing healthcare outcomes and financial conditions across different demographics.

### strict_paper_only

This dataset contains 85,400 rows and 8 columns.

Income percentile is assigned based on household earnings relative to all other individuals of the same sex and age in the United States during each year, after excluding those with zero income. [life_expectancy:p2:w180]

Household income is measured as adjusted gross income plus tax-exempt interest minus taxable Social Security and disability benefits for filers, and as wage earnings plus unemployment benefits for non-filers, adjusted to 2012 dollars. [life_expectancy:p2:w180]

Mortality rates are calculated using Social Security Administration death records, with total deaths closely matching National Center for Health Statistics data. [life_expectancy:p2:w180]

Mortality rates are reported for ages 40 to 76, with empirical rates observed until age 76 and a minimum reported age_at_d of 40. [life_expectancy:p2:w360] [life_expectancy:p3:w180]

Income data are available for each individual for every year from 1999 through 2014, but mortality rates are reported for years 2001 to 2014 due to the 2-year lag. [life_expectancy:p2:w180] [life_expectancy:p2:w360]

### documentation_assisted

This dataset contains 85,400 rows and 8 columns.

Each row reports the US mortality rate for a specific gender, age at death (40–76), year of death (2001–2014), and household income percentile (1–100). [documentation:life_national_mortality:p1:w0]

The 'mortrate' column gives the mortality rate for the specified group, with the denominator being the 'count' at the beginning of the year. [documentation:life_national_mortality:p1:w0]

The 'gnd' column indicates gender for each group. [documentation:life_national_mortality:p1:w0]

The 'pctile' column specifies the household income percentile for the group. [documentation:life_national_mortality:p1:w0]

The 'lag' column records the number of years between income measurement and mortality rate calculation. [documentation:life_national_mortality:p1:w0]

Household incomes are measured two years prior to the mortality rate for ages 40–63, and at age 61 for ages 64–76. [documentation:life_national_mortality:p1:w0]

The 'hh_inc' column gives the mean household income for each group. [documentation:life_national_mortality:p1:w0]

### Target judgments

| Target | Baseline | Strict paper | Documented |
|---|---|---|---|
| aggregated mortality cell rather than individual record | incorrect | omitted | supported |
| gender-age-year-income-percentile cell grouping | partial | partial | supported |
| mortality rate denominator is beginning-of-year count | omitted | omitted | supported |
| income lag two years at ages 40-63 and income at age 61 for ages 64-76 | omitted | partial | supported |

## life_county_expectancy

### csv_baseline

This dataset contains demographic and spatial information across various counties in the United States, with a total of 1,559 rows and 49 columns. It includes key variables such as county names, populations from the year 2000, and life expectancy metrics for both females and males across four quarters. The dataset also features unique identifiers for states and cities, allowing for detailed geographic analysis. Each column represents specific types of data, including population counts and life expectancy measures, which are essential for demographic studies and public health assessments. Overall, this dataset serves as a valuable resource for researchers and policymakers.

### strict_paper_only

This dataset contains 1,559 rows and 49 columns.

No table-specific semantic claim passed both evidence reviews. Field meanings remain unresolved from the available paper evidence.

### documentation_assisted

This dataset contains 1,559 rows and 49 columns.

Each row reports county-level life expectancy point estimates and standard errors for men and women at age 40, by income quartile. [documentation:life_county_expectancy:p1:w0]

Both race-adjusted and unadjusted life expectancy estimates are reported for each gender and income quartile. [documentation:life_county_expectancy:p1:w0]

Estimates are reported only for counties with populations larger than 25,000. [documentation:life_county_expectancy:p1:w0]

The table includes standard errors for each life expectancy estimate by gender, income quartile, and adjustment status. [documentation:life_county_expectancy:p1:w0] [documentation:life_county_expectancy:p2:w0]

Counts of individuals by gender and income quartile are provided for each county. [documentation:life_county_expectancy:p2:w0]

Each row identifies the county and its population in 2000, as well as the corresponding commuting zone and state. [documentation:life_county_expectancy:p1:w0]

### Target judgments

| Target | Baseline | Strict paper | Documented |
|---|---|---|---|
| county row unit rather than city/CZ/state observations | supported | abstained | supported |
| income quartiles rather than calendar quarters | incorrect | abstained | supported |
| both adjusted and unadjusted estimates | omitted | abstained | supported |
| uncertainty fields are standard errors | omitted | abstained | supported |

## race_national_statistics

### csv_baseline

This dataset contains 100 rows and 69 columns, focusing on various demographic and educational metrics across different racial and ethnic groups. Key variables include counts of individuals from different backgrounds, such as American Indian, Asian, Black, Hispanic, and White populations, along with their respective densities and educational attainment levels. The dataset also measures factors like the percentage of children attending college, hours worked, and incarceration rates, providing a comprehensive view of socio-economic conditions. Each column serves a specific function, such as measurement or aggregation, making this dataset valuable for analyzing demographic trends and disparities.

### strict_paper_only

This dataset contains 100 rows and 69 columns.

Each row in the table represents children grouped by their parents' national income percentile, as indicated by the par_pctile column. [race_opportunity:p47:w180] [race_opportunity:p59:w180] [race_opportunity:p94:w0]

Children are assigned income percentile ranks relative to all other children in their birth cohort, while parents are ranked relative to all parents with children in the same birth cohort. [race_opportunity:p59:w180]

### documentation_assisted

This dataset contains 100 rows and 69 columns.

Each row represents statistics for children born in 1978-83 at a specific parent household income percentile. [documentation:race_national_statistics:p1:w0]

The column count_pooled gives the number of children born to parents at a given income percentile, rounded to the next 100s. [documentation:race_national_statistics:p1:w0]

The columns count_[race]_pooled report the number of children born to parents at a given income percentile by race, rounded to the next 100s. [documentation:race_national_statistics:p1:w0] [documentation:race_national_statistics:p1:w180]

The columns kfr_[race]_[gender] and kfr_[race]_pooled report mean child family (household) income rank by race and gender, or pooled across gender. [documentation:race_national_statistics:p2:w0]

The columns kid_college_[race]_[gender] give the percentage of children with college attendance by race and gender, defined as having at least some college credit at age 20 or older (2005-2015 ACS). [documentation:race_national_statistics:p2:w0]

The columns kid_jail_[race]_[gender] report the percentage of children incarcerated by race and gender, defined as being incarcerated on April 1, 2010 (2010 Census short form). [documentation:race_national_statistics:p2:w0]

The columns spouse_rank_[race]_[gender] report the mean individual income rank of spouse by race and gender; children not married are assigned spousal income of 0 and are included. [documentation:race_national_statistics:p3:w0] [documentation:race_national_statistics:p3:w180]

### Target judgments

| Target | Baseline | Strict paper | Documented |
|---|---|---|---|
| one row per parent income percentile | omitted | supported | supported |
| 1978-1983 birth cohorts | omitted | omitted | supported |
| race and gender groupings | partial | omitted | supported |
| adult household income ranks rather than demographic densities | omitted | partial | supported |

## race_cz_income

### csv_baseline

This dataset contains demographic information from various cities, focusing on population statistics from the year 2000. It includes total population figures as well as breakdowns by race, specifically Black, Hispanic, and White populations. The dataset features 741 rows and 21 columns, with key metrics such as the mean population and specific population percentages for different racial groups. Each city is represented by its name and a unique identifier. The data is primarily used for demographic measurement and analysis, providing insights into the racial composition and population dynamics of urban areas.

### strict_paper_only

This dataset contains 741 rows and 21 columns.

No table-specific semantic claim passed both evidence reviews. Field meanings remain unresolved from the available paper evidence.

### documentation_assisted

This dataset contains 741 rows and 21 columns.

Each row represents a commuting zone (CZ), identified by cz and cz_name. [documentation:race_cz_income:p1:w0] [documentation:race_cz_income:p2:w0]

cz_pop2000 is the total population of the CZ in the 2000 Census. [documentation:race_cz_income:p2:w0]

cz_pop_black2000, cz_pop_hisp2000, and cz_pop_white2000 are 2000 Census counts for non-Hispanic Black, Hispanic, and non-Hispanic White residents in each CZ. [documentation:race_cz_income:p2:w0]

kfr_pooled_p25 is the mean household income rank for children with parents at the 25th percentile, pooled across race and gender. [documentation:race_cz_income:p2:w0]

kfr_black_pooled_p25 and kfr_white_pooled_p25 are mean household income ranks for Black and White children with parents at the 25th percentile, pooled across gender. [documentation:race_cz_income:p2:w0]

kir_[race]_[gender]_p[pctile] columns report mean individual income rank for children by race, gender, and parent income percentile. [documentation:race_cz_income:p2:w0]

Income rank statistics are reported as bin midpoints, rounded to the second decimal; bins with fewer than 20 children are omitted. [documentation:race_cz_income:p1:w0]

### Target judgments

| Target | Baseline | Strict paper | Documented |
|---|---|---|---|
| CZ row unit rather than cities | incorrect | abstained | supported |
| adult individual and household income ranks | omitted | abstained | supported |
| predictions at parent income percentiles 25 and 75 | omitted | abstained | partial |
| 2000 Census population counts | supported | abstained | supported |

## college_access_mobility

### csv_baseline

This dataset contains information on various educational institutions across the United States, with 2,202 entries and 15 columns. Each entry includes a unique identifier, the name of the institution, its location, and various financial metrics such as median parental income and median student income. The dataset also features key measurements like the first quartile of parental income and the top 1% income share. Additionally, it provides insights into trends and counts related to these institutions. The data is structured to facilitate analysis of educational and economic factors at both city and state levels, making it a valuable resource for researchers and policymakers.

### strict_paper_only

This dataset contains 2,202 rows and 15 columns.

No table-specific semantic claim passed both evidence reviews. Field meanings remain unresolved from the available paper evidence.

### documentation_assisted

This dataset contains 2,202 rows and 15 columns.

Median parent household income (par_median) is measured as average annual pre-tax household income (Adjusted Gross Income), inflation-adjusted to 2015 dollars, over the five years when the child was ages 15-19. [documentation:college_access_mobility:p1:w0] [documentation:college_access_mobility:p1:w180] [documentation:college_access_mobility:p1:w360]

Median child individual earnings in 2014 (k_median) are reported, rounded to the nearest $100. [documentation:college_access_mobility:p1:w0] [documentation:college_access_mobility:p1:w180] [documentation:college_access_mobility:p1:w360]

kq5_cond_parq1 is the percent of children who reach the top 20% of the income distribution among those whose parents were in the bottom 20%. [documentation:college_access_mobility:p1:w360]

mr_kq5_pq1 is the mobility rate: percent of students who have parents in the bottom 20% and themselves reach the top 20% of the income distribution. [documentation:college_access_mobility:p1:w360]

count is the average number of children per cohort for each college, calculated over the 1980, 1981, and 1982 birth cohorts (using 1983 and 1984 if needed). [documentation:college_access_mobility:p1:w0] [documentation:college_access_mobility:p1:w180] [documentation:college_access_mobility:p2:w0]

### Target judgments

| Target | Baseline | Strict paper | Documented |
|---|---|---|---|
| college reporting unit | supported | abstained | supported |
| bottom parent income quintile rather than quartile | incorrect | abstained | supported |
| joint mobility share of all students versus conditional success rate | omitted | abstained | supported |
| per-household five-year income average versus across-student median | partial | abstained | ambiguous |

## college_characteristics

### csv_baseline

This dataset contains information on various educational institutions across the United States, including details such as institution name, location, enrollment figures, and financial metrics. It features 2,463 rows and 49 columns, with key identifiers like super_opeid and geographic data including state and county. The dataset also includes financial data such as average faculty salaries and sticker prices for tuition over different years. Additionally, it provides demographic breakdowns of student populations by race and field of study. Each column is carefully categorized, allowing for comprehensive analysis of educational trends and institutional performance.

### strict_paper_only

This dataset contains 2,463 rows and 49 columns.

The variable black_share_fall_2000 represents the fraction of undergraduate students at a college who are Black alone, as measured in the IPEDS Fall Enrollment survey in 2000. [college_mobility:p60:w0] [college_mobility:p60:w180] [college_mobility:p69:w180]

The variable asian_or_pacific_share_fall_2000 is defined as the fraction of undergraduate students at a college who are Asian or Pacific Islander, based on IPEDS data from 2000. [college_mobility:p60:w0] [college_mobility:p69:w180]

The variable hisp_share_fall_2000 measures the fraction of undergraduate students at a college who are Hispanic, using IPEDS Fall Enrollment survey data from 2000. [college_mobility:p60:w0] [college_mobility:p69:w180]

The variable grad_rate_150_p_2002 measures the graduation rate for full-time undergraduates who graduate within 150% of normal time, as reported in IPEDS for 2002. [college_mobility:p69:w180]

The variable exp_instr_pc_2000 is defined as instructional expenditure per student, excluding operations, maintenance, and interest, divided by total enrollment in IPEDS for 2000. [college_mobility:p69:w180]

The variable endowment_pc_2000 is computed as the ending value of endowment assets in 2000 divided by total undergraduate enrollment in the fall of 2000, both from IPEDS. [college_mobility:p60:w0]

The variable avgfacsal_2001 measures the average salary for full-time faculty members on 9-month equated contracts in the academic year 2001-02, as reported in the IPEDS Delta Cost Project Database. [college_mobility:p60:w0]

The variables pct_arthuman_2000, pct_business_2000, pct_health_2000, pct_multidisci_2000, pct_publicsocial_2000, pct_stem_2000, pct_socialscience_2000, and pct_tradepersonal_2000 represent the share of degrees awarded by college in IPEDS (2000) categorized by major field. [college_mobility:p105:w0] [college_mobility:p105:w180]

### documentation_assisted

This dataset contains 2,463 rows and 49 columns.

Each row represents a college or college group, uniquely identified by super_opeid, with enrollment-weighted means for grouped colleges except for location and tier variables, which use the largest college. [documentation:college_characteristics:p1:w0]

The region column codes the Census region of the college: 1=Northeast, 2=Midwest, 3=South, 4=West. [documentation:college_characteristics:p1:w0]

The tier column categorizes colleges by selectivity and type, with values from 1 (Ivy Plus) to 12 (Less than two year schools of any type). [documentation:college_characteristics:p1:w0] [documentation:college_characteristics:p1:w180]

The grad_rate_150_p_2013 column reports the percentage of students graduating within 150 percent of normal time at four-year and two-year institutions in 2013. [documentation:college_characteristics:p2:w0]

The scorecard_netprice_2013 column gives the net cost of attendance for students in the bottom 20% income quintile in 2013, from the College Scorecard. [documentation:college_characteristics:p2:w0] [documentation:college_characteristics:p2:w180]

The black_share_fall_2000 column measures the share of Black undergraduate students enrolled in Fall 2000. [documentation:college_characteristics:p2:w180]

The avgfacsal_2013 column gives the average faculty salary at the college in 2013. [documentation:college_characteristics:p2:w0]

### Target judgments

| Target | Baseline | Strict paper | Documented |
|---|---|---|---|
| college or college-group row unit | partial | omitted | supported |
| correct field-specific expenditure units: exp_instr_pc is per student; exp_instr is total | omitted | supported | omitted |
| Asian OR Pacific Islander coverage when describing that share | omitted | supported | omitted |
| graduation within 150% of normal time | omitted | supported | supported |

