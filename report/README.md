# Project write-up

[Read the report](PROJECT_REPORT.md) or open
[the editable Word version](Dataset_Description_Project_Report.docx).
The Word report is five pages, uses black text, and has no personal name or
completion date. It covers the research question, ten datasets, three conditions,
retrieval and review methods, evaluation, results, limitations, and references.

The results describe a focused development comparison. Codebook agreement in the
documented condition is source consistency because the codebooks were generation
inputs. The report includes the remaining median-income ambiguity and missing
highly cited inventor definition. It has not been checked against a separate
course submission rubric.

## Recompute the evaluation

Run from the project root with the preserved local results in place:

```bash
python evaluate_outputs.py \
  --baseline-root results/dataset_validation \
  --results-root results/description_accuracy \
  --fresh-root results/step3-verification \
  --output results/paired_evaluation
```

This uses saved outputs and annotations and makes no generation API calls.
Raw run artifacts and downloaded source documents remain local; they are not
included in the public repository.

## Rebuild the Word report

Use a Python environment with the dependencies in `report/requirements.txt`:

```bash
python -m pip install -r report/requirements.txt
python report/build_report.py
```

`content.json` holds the report prose. Tables are populated from
`evaluation/comparison.json`. The builder checks the evaluation checksum and
stops if the results have changed, so the narrative must be reviewed before it
can be rebuilt against a different evaluation. The generated Markdown and Word
versions share the same prose and tables. Recheck pagination after layout edits.

## Evidence behind the report

- `evaluation/rubric.json` defines the 40 targeted checks.
- `evaluation/annotations.json` contains the Codex-assisted judgments and rationales.
- `evaluation/comparison.json` records selected outputs and provenance.
- `papers/manifest.json` identifies the paper versions and dataset mappings.
- `papers/reviewed_descriptions/` contains corrected reference text, kept separate
  from generated results and model-performance counts.
