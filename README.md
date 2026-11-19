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

Next: split these pages into passages, index them, and test retrieval with questions
about each dataset before connecting retrieved passages to AutoDDG.
