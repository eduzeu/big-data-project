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
git clone https://github.com/eduzeu/big-data-project.git
cd big-data-project
```

### 2. Add the baseline files

The baseline script, requirements, and data have **not yet been committed to this repository**. Copy these items from the prepared local project into the cloned folder before continuing:

- `run_baseline.py`
- `requirements.txt`
- `data/`, containing `health_ineq_online_table_13.csv`

### 3. Set up the environment and generate the description

With Python 3.11 and Git installed, run:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_baseline.py --generate --prompt-for-key
```

Paste the OpenAI API key only at the hidden prompt. The key is not saved. The run makes paid API calls and writes the description to `results/description.md`, with supporting outputs in the same folder.

Do not commit API keys or credential files.

## Next step

Run the same configuration on the selected team datasets, using a separate `--output` folder for each. Then add paper retrieval and compare the enriched descriptions with the saved baselines.

## Sources

- [Official AutoDDG repository](https://github.com/VIDA-NYU/AutoDDG)
- [Opportunity Insights dataset README](https://opportunityinsights.org/wp-content/uploads/2018/04/health_ineq_online_table_13_readme.pdf)

