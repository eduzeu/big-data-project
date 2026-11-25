# Description accuracy and retrieval improvements

Corrected reference descriptions for all ten datasets are available in [reviewed_descriptions](reviewed_descriptions/README.md). These use the supplied table documentation, with paper context where necessary. They are manually reviewed reference corrections, not claims about model performance.

## Implementation

- Table-focused retrieval fuses three complementary BM25 queries, removes unreliable folder table numbers, and preserves neighboring context.
- Candidate claims require evidence for both semantic meaning and table applicability. Review separately checks definitions, table linkage, units/denominators and schema consistency.
- A final independent audit can reject provisional approvals. Final text is rendered verbatim from surviving claims; no writing model can add new claims afterward.
- No supported claims produces an explicit abstention. Failed validation never silently becomes a successful description.
- Field templates such as `_pq_[1-5]` and `kir_[race]_[gender]_p[pctile]` are accepted without allowing model-written citation markers. Existing excerpt IDs are normalized for zero padding; unknown sources still fail.
- A separate documentation-assisted mode binds the CSV to its unique accompanying PDF, prioritizes table definitions over conflicting study-wide methods, and records documentation use and hashes explicitly.

## Live verification

All ten preserved baselines were reused. CSV hashes, dimensions, sampled rows, content profiles and semantic profiles match for every selected output. All source excerpts are exact matches, every final sentence is an approved claim, and run-code hashes match either the initial committed source or the formatting-fix source. **31 offline tests pass.**

| Condition | Drafts with approved claims | Explicit abstentions | Remaining execution failures |
|---|---:|---:|---:|
| Stricter paper-only | 4 | 6 | 0 |
| Documentation-assisted | 10 | 0 | 0 |

The initial passes had six formatting validation failures across the two conditions. Those cases were rerun after targeted fixes; the failed attempts remain preserved. There were 20 selected condition/dataset outputs plus six formatting retries. Counts above distinguish operational completion from semantic coverage.

## Verified improvements and remaining limitations

The documentation-assisted mortality description now states the correct two-year lag through age 63 and income fixed at age 61 for ages 64–76. The county life-expectancy draft identifies both adjusted and unadjusted estimates, standard errors, county rows and the population threshold. The stricter paper-only college-characteristics description correctly distinguishes `exp_instr_pc_2000` as per-student spending and includes Pacific Islanders in the Asian-or-Pacific-Islander field.

**Correction to the earlier audit:** both total and per-student expenditure columns exist in the college CSV. A per-student statement is not inherently wrong; it must be mapped to the correct field. The prior audit overstated that issue without making this distinction. Its historical report is preserved.

Model reviews still miss errors. The documentation-assisted childhood-inventor draft confuses highly cited inventors with patents in two claims. The mobility draft still uses ambiguous joint-versus-conditional rate wording and unclear median-income aggregation wording. Use the separately reviewed reference descriptions for these corrections. The other drafts received a limited source-consistency review, not a formal independent accuracy assessment.

Adding table documentation changes the input condition. Those PDFs were formerly reference material and are now model inputs in the documented mode. Agreement with them is **not held-out accuracy**, and the documented results must not be attributed to the paper-only method. All prompts were developed after inspecting previous failures; these are development results, not a blinded benchmark.

## Saved outputs

[Machine-readable results and selected source paths](description_accuracy_summary.json) include every selected description and the review findings. Local `results/description_accuracy` contains the paper-only and documented attempts, retries, provenance and logs. [Reviewed descriptions](reviewed_descriptions/README.md) are the corrected project text. Older baselines and results remain intact.
