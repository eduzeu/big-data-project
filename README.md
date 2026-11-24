# AutoDDG Baseline Task Summary

The first setup task is complete: the original AutoDDG pipeline generated a description for one Opportunity Insights CSV. This establishes a baseline for testing whether research papers and Stata code improve the descriptions.

## Work completed

- Cloned the official AutoDDG code and installed version 0.1.2 in a separate Python 3.11 environment.
- Used the international life expectancy at age 40 dataset: 194 rows and three columns, `country`, `le_F`, and `le_M`. Profiled the full CSV and selected a reproducible 10-row sample using seed 42.
- Generated column semantics and a description with `gpt-4o-mini`, without adding paper, README, or Stata context.
- Saved the profiles, sample, prompt, description, and run metadata.

## Results

Semantic profiling and description generation took **8.48 seconds**. The description reported the row count, columns, means, and ranges correctly. It omitted **“at age 40”** and described trends despite having no time column.

The raw output is preserved for the later comparison. These limitations have not yet been evaluated across the full dataset collection.

## How to run it

### 1. Clone the project repository

```bash
git clone --branch feature/autoddg-baseline https://github.com/eduzeu/big-data-project.git
cd big-data-project
```

### 2. Set up the environment and generate the description

This branch includes the runner, source-pinned requirements, starter CSV, and saved baseline results. The Python environment and API key are not included.

With Python 3.11 and Git installed, run:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_baseline.py --generate --prompt-for-key --output results/new-run
```

Paste the OpenAI API key only at the hidden prompt. The key is not saved. The run makes paid API calls and writes the new description to `results/new-run/description.md`, with supporting outputs in that folder. The original baseline in `results/` stays unchanged.

To verify setup without making LLM calls:

```bash
python run_baseline.py --output results/setup-check
```

For another dataset, add `--csv path/to/dataset.csv` and choose a new `--output` folder. Each run can overwrite files in its output folder, so use a different folder for each dataset or experiment.

`requirements.txt` pins the official AutoDDG source commit. `requirements-lock.txt` records the resolved versions from the original Python 3.11 environment.

## Saved baseline outputs

- `results/description.md`: original generated description.
- `results/content_profile.md` and `results/structural_notes.md`: algorithmic profiling outputs.
- `results/semantic_profile.md`: generated column semantics.
- `results/prompt.txt`: exact description prompt.
- `results/sample.csv`: reproducible 10-row input sample.
- `results/generation.json`: successful run configuration and timing.
- `results/preparation.json`: earlier preparation-only record; it does not indicate failure of the later successful run.

Do not commit API keys or credential files. `.gitignore` excludes common credential files and local Python environments.

## Next step

Run the same configuration on the selected team datasets, using a separate `--output` folder for each. Then add paper retrieval and compare the enriched descriptions with the saved baselines.

## Sources

- [Official AutoDDG repository](https://github.com/VIDA-NYU/AutoDDG)
- [Opportunity Insights dataset README](https://opportunityinsights.org/wp-content/uploads/2018/04/health_ineq_online_table_13_readme.pdf)



## Research paper collection

The paper corpus covers the 10 selected dataset tables with five research papers.
`papers/manifest.json` records the source links, paper versions, and dataset mapping.

```bash
python -m pip install -r requirements-papers.txt
python collect_papers.py
```

No API key is needed. Existing PDFs are reused; use `--refresh` to download them again.
The command returns an error if a download or title/extraction check fails.

Local outputs in `papers/local/`:

- `pdf/`: the five original papers.
- `text/`: extracted text with page markers.
- `pages/`: one JSON record per PDF page, with paper ID, text, source URL, PDF checksum, and page label.
- `extraction_report.json`: counts, checksums, and extraction failures.

`pdf_page` starts at 1 and counts physical PDF pages. `page_label` retains the PDF's
label, which may differ from the printed article number. Cite the physical page
alongside the paper title when inspecting a retrieved passage.

| Paper family | Selected CSV tables |
| --- | --- |
| Inventors | `table_3.csv`, `table_1a.csv` |
| Opportunity Atlas | `cty_covariates.csv`, `county_outcomes_simple.csv` |
| Life expectancy | `health_ineq_online_table_15.csv`, `health_ineq_online_table_11.csv` |
| Race and opportunity | `table_1.csv`, `table_4.csv` |
| College mobility | `mrc_table1.csv`, `mrc_table10.csv` |

The mapping follows the selected folder inventory and the official research families;
CSV contents have not been checked. Two Atlas folder table numbers differ from their
codebook filenames; the manifest flags those pairs for review. Codebooks and READMEs
are held out of this corpus for evaluation. Stata `.do` files and the separate life
expectancy technical supplement are not included.

The PDFs and extracted full text stay local and are ignored by Git. Source URLs and
the collector are shared so teammates can recreate the corpus. The committed
`papers/extraction_summary.json` records the verified collection, without full text.
Text extraction checks confirm usable text, not perfect recovery of tables or equations.

The retrieval and description adapters built on this corpus are described below.

## Search papers and prepare enriched descriptions

This branch adds local BM25 keyword retrieval. It needs no embedding service or API
key. Pages are split into 220-word passages with 40-word overlap; passages stay within
one PDF page. Results are restricted to the paper mapped to the selected dataset,
ranked by BM25, and limited to one passage per page to reduce duplicate evidence.

After collecting papers:

```bash
python paper_retrieval.py build
python paper_retrieval.py search --dataset-id life_county_expectancy --query "How is life expectancy estimated by income quartile?"
```

Each result includes the passage, score, chunk ID, paper title, source URL, physical
PDF page, page label, and PDF checksum. BM25 scores indicate word-match relevance;
they are not probabilities or proof that a passage answers the question. Queries
using different terminology may need rewording. PDF extraction can merge words,
especially in the life expectancy article. Formal retrieval quality evaluation is
still pending; current checks cover filtering, provenance, and a method lookup.

To try the description workflow with a real selected CSV, download the public county
table (or use your team's copy):

```bash
curl --fail --location https://opportunityinsights.org/wp-content/uploads/2018/04/health_ineq_online_table_11.csv --output data/health_ineq_online_table_11.csv
python run_baseline.py --csv data/health_ineq_online_table_11.csv --dataset-id life_county_expectancy --output papers/local/demo_run
```

This prepares the sample, profile, retrieved passages, and combined description
profile without LLM calls. To generate an enriched description, repeat with
`--generate --prompt-for-key`. The key is entered privately and is not saved.
Use `--paper-query "your question"` to override the default query made from the
manifest dataset name and CSV column names.

AutoDDG's existing semantic analysis still receives the CSV sample only. The final
description call receives the content profile plus the retrieved paper evidence.
The runner saves `retrieved_passages.json`, `paper_context.txt`, and
`description_profile.md`, then saves the actual prompt, description, and generation
metadata when `--generate` succeeds. Paper-derived claims are requested to cite
chunk IDs, but generated citations still need review. Filename matching is a guard
against choosing the wrong dataset ID, not a validation of CSV contents.

Omit `--dataset-id` to retain the original baseline behavior. Paper runs require a
separate output directory so they cannot overwrite the default baseline results.
Use separate directories for baseline and enriched comparisons with the same CSV,
model, sample size, and seed. No generated improvement claim is made yet.

Offline checks (after downloading the county CSV and building the index):

```bash
python -m unittest discover -s . -p test_paper_retrieval.py -v
```

The generation integration test uses a mocked model, so it checks that evidence is
passed through without making paid API calls. Local indexes, downloaded datasets,
and run outputs remain outside Git.

## Reconcile evidence before generating a description

`run_grounded.py` is an experimental adapter around the saved AutoDDG baseline.
The first live pilot showed that adding passages to the content profile alone did
not correct wrong semantic guesses. This adapter adds three explicit model stages:

1. Extract source-supported meanings from the paper and the CSV column names,
   independently of the baseline guesses to avoid anchoring on their errors.
   The model selects numbered source excerpts; code inserts their original text
   and passage references, so the model cannot invent a quote. Up to six atomic supported facts are requested; unresolved columns are computed by code.
2. Review each interpretation against its quoted excerpts and reject unsupported
   mappings. If none survive, stop rather than generate a description.
3. Generate the description from the dataset label, dimensions, and accepted facts.
   Raw profiles and unresolved column names are excluded from the final request.
   The original semantic guesses are excluded from this final request. Paper claims
   must reference accepted fact IDs; code inserts the corresponding inline
   citations and constructs the claim list.

The excerpt catalog removes duplicate overlap text and selects up to 30 spans by
query relevance, favoring definitions over chart fragments. Source IDs are selected
by the model; quotes and final citations are attached programmatically.

The retriever also includes adjacent windows on each selected page so definitions
cut at passage boundaries are available. This changes evidence coverage relative
to the first pilot; it must be reported as part of the experimental condition.

The adapter checks JSON structure, column coverage, quoted-excerpt provenance, and
citation IDs. It permits one repair attempt per stage and fails without creating a
successful description if validation still fails. These checks **do not establish
semantic entailment**: a real excerpt can still be misinterpreted, so factual review
and independent evaluation remain necessary.

First generate a CSV-only baseline in its own directory:

```bash
python run_baseline.py --csv data/health_ineq_online_table_11.csv --output papers/local/paired_baseline --generate --prompt-for-key
```

Then reuse that baseline:

```bash
python run_grounded.py --csv data/health_ineq_online_table_11.csv --dataset-id life_county_expectancy --baseline-dir papers/local/paired_baseline --output papers/local/reconciled --paper-query "life expectancy county income quartile age 40 estimation" --generate --prompt-for-key
```

Omit `--generate --prompt-for-key` to prepare the inputs without making API calls.
Choose a new empty output directory for every run. The runner verifies the CSV
checksum, row/column counts and sampled rows against the baseline, and reuses its
model. Its original semantic profile is preserved for comparison, but excluded
from all new model requests. Baseline and first enriched-run artifacts are
preserved. Fact extraction defaults to `gpt-4.1` and support review to `gpt-5.1` with medium
reasoning effort (override with `--reconciliation-model` and `--review-model`); final description generation uses the original baseline
model. This stronger review stage adds API cost, and model-based support review can
still make mistakes. This changes the generation prompts and adds reconciliation and support-review calls; it
is a new experimental condition, not the unmodified upstream AutoDDG generator.

Saved artifacts include `reconciled_semantics.json`, `evidence_review.json`,
`accepted_semantics.json`, `grounded_description.json`,
`excerpt_catalog.json`, the description, exact requests and raw responses, validation records, retrieved
passages and generation metadata. Keep outputs local: they contain paper excerpts.
Codebooks/READMEs remain excluded from generation; they can be consulted separately
for post-run evaluation. No dataset-specific correction dictionary is injected.

```bash
python -m unittest test_grounded_generation test_paper_retrieval -v
```

The tests cover fabricated excerpts/IDs, missing citations, unresolved columns,
input parity, overwrite protection, bounded repair, and isolation of the original
guesses from the new model requests. They make no provider calls.
