"""Prepare one Opportunity Insights CSV; use --generate after setting an API key."""
from __future__ import annotations

import argparse
import hashlib
import getpass
import json
import os
import platform
import random
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from autoddg import AutoDDG, __version__, profile_dataset

ROOT = Path(__file__).resolve().parent
SOURCE = 'https://opportunityinsights.org/wp-content/uploads/2018/04/health_ineq_online_table_13.csv'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', type=Path, default=ROOT / 'data/health_ineq_online_table_13.csv')
    parser.add_argument('--output', type=Path, default=ROOT / 'results')
    parser.add_argument('--model', default='gpt-4o-mini')
    parser.add_argument('--sample-rows', type=int, default=10)
    parser.add_argument('--generate', action='store_true', help='Make paid LLM calls and generate the baseline description')
    parser.add_argument('--prompt-for-key', action='store_true', help='Read the key privately for this process only')
    args = parser.parse_args()
    if args.sample_rows < 1:
        parser.error('--sample-rows must be positive')
    if args.generate and args.prompt_for_key and not os.environ.get('OPENAI_API_KEY'):
        os.environ['OPENAI_API_KEY'] = getpass.getpass('OpenAI API key (hidden; not saved): ').strip()
    if args.generate and not os.environ.get('OPENAI_API_KEY'):
        parser.error('Set OPENAI_API_KEY in your terminal first. Do not put it in this script.')
    random.seed(42)
    np.random.seed(42)
    frame = pd.read_csv(args.csv)
    if frame.empty or len(frame.columns) == 0:
        parser.error('The CSV must have at least one data row and column')
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    sample = frame.sample(n=min(args.sample_rows, len(frame)), random_state=42).reset_index(drop=True)
    sample_csv = sample.to_csv(index=False)
    profile, structural_notes = profile_dataset(frame)
    (output / 'sample.csv').write_text(sample_csv)
    (output / 'content_profile.md').write_text(profile)
    (output / 'structural_notes.md').write_text(structural_notes)
    info = {
        'status': 'prepared_awaiting_api_key',
        'prepared_utc': datetime.now(timezone.utc).isoformat(),
        'dataset_file': args.csv.name,
        'dataset_source': SOURCE if args.csv.name == 'health_ineq_online_table_13.csv' else None,
        'csv_sha256': hashlib.sha256(args.csv.read_bytes()).hexdigest(),
        'rows': len(frame), 'columns': list(frame.columns),
        'missing_values': {k: int(v) for k,v in frame.isna().sum().items()},
        'sample_rows': len(sample), 'seed': 42,
        'autoddg_version': __version__, 'python_version': platform.python_version(),
        'model': args.model, 'description_words': 100,
        'used_paper_context': False, 'used_readme_context': False,
        'used_stata_context': False, 'llm_calls_made_by_this_run': False,
    }
    print(f"Loaded {len(frame)} rows and {len(frame.columns)} columns: {', '.join(frame.columns)}")
    print('Saved sample and the original AutoDDG content profile.')
    if not args.generate:
        (output / 'preparation.json').write_text(json.dumps(info, indent=2))
        print('No LLM calls made. Add your API key, then rerun with --generate.')
        return
    from openai import OpenAI
    pipeline = AutoDDG(client=OpenAI(timeout=90, max_retries=1), model_name=args.model,
                       description_temperature=0.0, description_words=100)
    started = time.perf_counter()
    # The baseline receives CSV content only; reference documentation is held out.
    semantic = pipeline.analyze_semantics(sample)
    if not semantic or not semantic.strip():
        raise RuntimeError('AutoDDG returned no semantic profile; inspect the provider response before retrying.')
    (output / 'semantic_profile.md').write_text(semantic)
    prompt, description = pipeline.describe_dataset(
        dataset_sample=sample_csv, dataset_profile=profile, use_profile=True,
        semantic_profile=semantic, use_semantic_profile=True,
        use_topic=False,
    )
    if not description or not description.strip():
        raise RuntimeError('AutoDDG returned an empty description')
    (output / 'prompt.txt').write_text(prompt)
    (output / 'description.md').write_text(description)
    info.update(status='baseline_generated', llm_calls_made_by_this_run=True,
                generation_seconds=time.perf_counter()-started)
    (output / 'generation.json').write_text(json.dumps(info, indent=2))
    print('\nGenerated baseline description:\n')
    print(description)
    print(f"\nSaved description and run metadata in {output}")


if __name__ == '__main__':
    main()
