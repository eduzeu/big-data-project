# Improving Dataset Descriptions with Research Papers and Table Documentation

## Project summary

We studied whether research-paper evidence helps AutoDDG describe a dataset more accurately. We compared CSV-only descriptions with a stricter paper-supported pipeline and a separate version that also receives the table's documentation. The documentation-assisted outputs clearly expressed 33 of 40 targeted definitions, compared with 7 for the baseline. These counts describe a focused development review. They do not establish overall accuracy, and the added documentation changes the information available to the model.

## Research question

A CSV shows values and column names, but it often leaves out the definitions needed to interpret them. A field can represent a rate, a count, a rank, or a standard error. Geographic identifiers can describe context without defining the observation unit. Our question was whether retrieving evidence from the associated paper could resolve these ambiguities while preventing unsupported statements about a specific released table.

## Datasets and source material

We used ten Opportunity Insights tables associated with five research projects: inventors, the Opportunity Atlas, income and life expectancy, race and economic opportunity, and college mobility [1-5]. The tables vary in size and observation unit. The local paper corpus contains 422 extracted PDF pages and 1,097 indexed passages. The project records the selected paper versions and file checksums; some paper versions and supplied table documentation differ.

| Dataset | Rows | Columns |
| --- | --- | --- |
| Inventors by college | 423 | 17 |
| Inventors by childhood CZ | 741 | 140 |
| Atlas county characteristics | 3,221 | 35 |
| Atlas county outcomes | 3,219 | 64 |
| National mortality rates | 85,400 | 8 |
| County life expectancy | 1,559 | 49 |
| National outcomes by race | 100 | 69 |
| CZ income ranks by race | 741 | 21 |
| College access and mobility | 2,202 | 15 |
| College characteristics | 2,463 | 49 |

CSV files supplied the data in every condition. The table codebooks were excluded from CSV-only and paper-only generation, then deliberately added in the documentation-assisted condition. Stata files were not used as generation inputs. Folder labels and codebook table numbers occasionally disagreed, so numeric folder labels were not treated as authoritative definitions.

## Method

The baseline uses the recorded AutoDDG implementation [6] to profile the full CSV and analyze a ten-row sample selected with seed 42. It receives the sample, the content profile, and the tentative semantic profile. Baseline semantic analysis and description generation use gpt-4o-mini. Each revised run reuses the same CSV, sampled rows, content profile, and saved semantic profile. The original semantic guesses are preserved for comparison but excluded from the new model requests.

| Condition | Evidence available | Generation stages |
| --- | --- | --- |
| CSV baseline | CSV sample and profiles | gpt-4o-mini semantic analysis and description |
| Strict paper support | Same CSV inputs and mapped paper | gpt-4.1 claims and two gpt-5.1 audits |
| Documentation assisted | Same CSV, paper, and linked table PDF | Same claim and audit stages with table definitions |

Paper retrieval is restricted to the dataset's mapped paper. We split extracted page text into passages of up to 220 words with 40-word overlap. The revised retriever combines three BM25 searches: a dataset-label query with measurement terms, a label query with online-table terms, and a bounded query built from field tokens. Reciprocal-rank fusion selects up to 12 anchor passages. Neighboring windows on the same PDF page preserve definitions that cross passage boundaries.

The extraction stage uses gpt-4.1 to propose up to eight short claims. Each claim must identify evidence for its meaning and its connection to this table. A gpt-5.1 reviewer separately checks the definition, table linkage, units and denominator, and consistency with the CSV schema and observed values. A second gpt-5.1 audit can reject provisional approvals. Both audits use medium reasoning effort. The documentation-assisted version adds the uniquely paired table PDF, records its checksum, and prioritizes its table-specific definitions over conflicting paper methods.

The final renderer copies surviving claims verbatim and attaches source citations. There is no final writing model that can introduce new claims after approval. If no claim survives, the run records an explicit abstention. Schema and citation checks allow one repair attempt per stage. Failed attempts are preserved. Exact quotations and valid citation IDs establish provenance; the reviewers can still approve a mistaken interpretation.

## Evaluation design

We applied four targeted checks to each dataset, giving 40 checks per condition. Targets cover observation units, key measures, groupings, and important qualifications such as adjustment status or rate denominators. Codex prepared the source-based annotations; there was no independent human rater or blinded review. Outcomes remain separate: supported, partial, omitted, incorrect, ambiguous, and abstained. Curated reference descriptions receive no credit as model outputs.

Two documented cases with remaining issues received one fresh run each under unchanged generation code. Both previous outputs were retained, and the fresh outputs were selected regardless of their apparent quality. One verification run per case cannot estimate repeatability or output variance.

## Results

All ten revised cases completed after the preserved formatting failures were resolved. The stricter paper-only condition produced semantic claims for four datasets and abstained for six. The documented condition produced drafts for all ten. All 35 local tests passed. These tests cover execution and integrity, including input matching, evidence IDs, final rendering, and evaluation labels; they do not establish that every claim is true.

| Condition | Supported | Partial | Omitted | Incorrect | Ambiguous | Abstained |
| --- | --- | --- | --- | --- | --- | --- |
| CSV baseline | 7 | 5 | 20 | 7 | 1 | 0 |
| Strict paper | 5 | 3 | 8 | 0 | 0 | 24 |
| Documented | 33 | 1 | 5 | 0 | 1 | 0 |

Each row totals 40 target checks. The 24 paper-only abstentions correspond to six datasets with four targets each. Supported means that the full target definition is clearly expressed. Partial means that valid content is incomplete. An omitted definition is not counted as incorrect, and a withheld description is not counted as a successful semantic description. The zero incorrect entries in the revised rows apply only to these selected targets, not to all generated claims.

## What the added evidence clarified

The CSV-only descriptions sometimes treated commuting zones as cities, income quartiles as calendar quarters, or bottom income quintiles as quartiles. The documented outputs generally identified the released table more precisely. For county life expectancy, the revised text states that estimates are measured at age 40, both adjusted and unadjusted estimates are present, and the uncertainty measures are standard errors. For national mortality, it identifies the beginning-of-year count as the rate denominator and gives the correct income timing: two years earlier at ages 40-63 and income fixed at age 61 for ages 64-76.

The college-characteristics review also exposed an error in our earlier audit. The actual CSV contains both exp_instr_* totals and exp_instr_pc_* per-student fields. A per-student statement is valid when linked to the latter. The revised paper-only output names exp_instr_pc_2000 explicitly and includes Pacific Islanders in the Asian-or-Pacific-Islander share. The comparison therefore does not reuse the earlier claim that per-student wording was inherently wrong.

## What remains unresolved

In the fresh childhood-inventor run, the misleading statements that ranked patents instead of inventors disappeared because the relevant claims were omitted. The output still lacks the correct highly cited inventor definition. In the fresh college-mobility run, the joint share of students with bottom-quintile parents and top-quintile adult income is distinguished from success conditional on low-income parents. However, the median-income sentence still fails to separate the household's five-year income average from the median across students at a college.

Coverage also remains uneven. The documented outputs omit five targets and express one only partially. The stricter paper-only condition clearly expresses five targets, expresses three partially, and omits eight in its non-abstaining outputs. Its cautious behavior reduces unsupported detail at the cost of leaving much of the table unexplained.

## Interpretation and limitations

The results support a practical distinction between paper context and released-table definitions. Papers can explain how a study measures income or constructs an outcome, but a figure's sample, an appendix regression, and an online table may differ. The table's own documentation often provides the missing link between a definition and a specific CSV field. Retrieving a relevant passage is therefore insufficient unless the system also establishes that the passage applies to this table.

The comparison does not isolate the causal effect of retrieval. Models, prompts, review stages, retrieved context, and output lengths changed together. The documented condition also receives additional information. Its agreement with those same documents is a source-consistency result, not held-out accuracy. The targeted checks are incomplete and correlated, the datasets were inspected during development, and the annotations were produced with AI assistance. No statistical significance claim or general performance estimate follows from these counts.

The main operational finding is that explicit table linkage and conservative review make uncertainty visible, but can also suppress useful content. Automatic reviews still miss subtle errors about ranked entities and statistical aggregation. A stronger follow-up evaluation would use unseen datasets, independent human annotations, repeated runs, matched output budgets, and separate experiments for retrieval, review, and documentation access. Stata context remains a possible additional condition rather than a completed part of this evaluation.

## Conclusion

We built a reproducible pipeline that compares CSV-only AutoDDG descriptions with evidence-supported alternatives. Table documentation enabled much fuller expression of the selected definitions, while the paper-only path frequently withheld uncertain claims. The results show the value of linking evidence to the released table and preserving unresolved meanings explicitly. They also show why citations, successful execution, and model approval must be checked separately from factual correctness.

## Reproducibility and project artifacts

The repository preserves separate runners for the baseline, strict paper-only, and documented conditions. Run records contain input and code hashes, samples, profiles, source passages, requests, responses, decisions, and descriptions. evaluate_outputs.py reproduces the comparison without new API calls from evaluation/rubric.json and evaluation/annotations.json. The comparison JSON and side-by-side report identify every selected output. The ten reviewed reference descriptions are stored separately from generated drafts. Reproduction commands and artifact locations are documented in the project README and report directory.

## Dataset results

Each dataset has four targeted definitions. The table reports fully supported targets; partial, omitted, incorrect, ambiguous, and abstained outcomes remain separate in the full evaluation. The documentation column is source consistency, because the table documentation was a generation input.

| Dataset | CSV baseline | Strict paper | Documented |
| --- | --- | --- | --- |
| Inventors by college | 1 | 0 | 3 |
| Inventors by childhood CZ | 0 | 1 | 3 |
| Atlas county characteristics | 2 | 0 | 3 |
| Atlas county outcomes | 1 | 0 | 4 |
| National mortality rates | 0 | 0 | 4 |
| County life expectancy | 1 | 0 | 4 |
| National outcomes by race | 0 | 1 | 4 |
| CZ income ranks by race | 1 | 0 | 3 |
| College access and mobility | 1 | 0 | 3 |
| College characteristics | 0 | 3 | 2 |

## References

[1] [Who Becomes an Inventor in America The Importance of Exposure to Innovation. Selected author-hosted paper, November 2018 version, and supplied Tables 1 and 3 codebooks.](https://opportunityinsights.org/paper/losteinsteins/)

[2] [The Opportunity Atlas Mapping the Childhood Roots of Social Mobility. Selected January 2025 paper and supplied county covariate and outcome codebooks.](https://opportunityinsights.org/paper/the-opportunity-atlas/)

[3] [The Association Between Income and Life Expectancy in the United States 2001-2014. Selected 2016 JAMA reprint and supplied Online Data Tables 11 and 15 documentation.](https://opportunityinsights.org/paper/lifeexpectancy/)

[4] [Race and Economic Opportunity in the United States An Intergenerational Perspective. Selected December 2019 paper and supplied Tables 1 and 4 codebooks.](https://opportunityinsights.org/paper/race/)

[5] [Income Segregation and Intergenerational Mobility Across Colleges in the United States. Selected February 2020 paper and supplied Mobility Report Cards Tables 1 and 10 codebooks.](https://opportunityinsights.org/paper/undermatching/)

[6] [VIDA NYU AutoDDG. Source pinned to commit f286ac697bdb0a199eac1ce0778401f30341b4bb. Project results and evaluation are recorded separately in this repository.](https://github.com/VIDA-NYU/AutoDDG/tree/f286ac697bdb0a199eac1ce0778401f30341b4bb)

