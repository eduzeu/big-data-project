"""Run preserved CSV-only / paper-grounded pairs for the manifest datasets."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import getpass
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--pilot-baseline', type=Path)
    p.add_argument('--workers', type=int, default=2, choices=[1,2])
    p.add_argument('--generate', action='store_true')
    args=p.parse_args()
    datasets=json.loads((ROOT/'papers/manifest.json').read_text())['datasets']
    jobs=[]
    for d in datasets:
        matches=list(args.data_root.rglob(d['csv_filename']))
        if len(matches)!=1: p.error(f"Expected one {d['csv_filename']}; found {len(matches)}")
        csv=matches[0].resolve()
        jobs.append(dict(dataset_id=d['dataset_id'],csv=str(csv),csv_sha256=hashlib.sha256(csv.read_bytes()).hexdigest(),
                         development_case=d['dataset_id']=='life_county_expectancy'))
    args.output.mkdir(parents=True,exist_ok=True)
    plan={'created_utc':datetime.now(timezone.utc).isoformat(),'jobs':jobs,
          'used_readme_context':False,'used_stata_context':False,
          'code_sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['grounded_generation.py','run_grounded.py','run_baseline.py','run_validation.py']}}
    (args.output/'plan.json').write_text(json.dumps(plan,indent=2))
    if not args.generate:
        print(f'Prepared {len(jobs)} datasets; no API calls made.');return
    env=os.environ.copy()
    if not env.get('OPENAI_API_KEY'):env['OPENAI_API_KEY']=getpass.getpass('API key (hidden; not saved): ').strip()
    if not env['OPENAI_API_KEY']:p.error('No API key provided')
    def job(spec):
        folder=args.output/spec['dataset_id'];folder.mkdir(exist_ok=True)
        baseline=args.pilot_baseline if spec['development_case'] and args.pilot_baseline else folder/'baseline'
        stages=[] if baseline==args.pilot_baseline else [
            ('baseline',[sys.executable,str(ROOT/'run_baseline.py'),'--csv',spec['csv'],'--output',str(baseline),'--generate'])]
        stages.append(('grounded',[sys.executable,str(ROOT/'run_grounded.py'),'--csv',spec['csv'],
            '--dataset-id',spec['dataset_id'],'--baseline-dir',str(baseline),'--output',str(folder/'grounded'),'--generate']))
        result={**spec,'status':'running'}
        for stage,cmd in stages:
            donefile=baseline/'generation.json' if stage=='baseline' else folder/'grounded/generation.json'
            if donefile.exists() and json.loads(donefile.read_text()).get('status') in ['baseline_generated','paper_reconciled_generated']:
                print(spec['dataset_id'],stage,'already complete',flush=True);continue
            print(spec['dataset_id'],stage,'started',flush=True)
            with (folder/f'{stage}.log').open('w') as log:
                try: completed=subprocess.run(cmd,env=env,stdout=log,stderr=log,timeout=1200)
                except subprocess.TimeoutExpired:result.update(status='failed',stage=stage,error='timeout');break
            if completed.returncode:
                result.update(status='failed',stage=stage,error='See local stage log');break
            print(spec['dataset_id'],stage,'complete',flush=True)
        else:
            result['status']='complete'
            result['baseline_description']=(baseline/'description.md').read_text()
            result['grounded_description']=(folder/'grounded/description.md').read_text()
            meta=json.loads((folder/'grounded/generation.json').read_text())
            result.update(rows=meta['rows'],column_count=len(meta['columns']),accepted_facts=meta['accepted_facts'])
        (folder/'result.json').write_text(json.dumps(result,indent=2));return result
    results=[]
    try:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for future in as_completed([pool.submit(job,j) for j in jobs]):
                results.append(future.result())
                (args.output/'results.json').write_text(json.dumps(results,indent=2))
    finally:env.pop('OPENAI_API_KEY',None)
    print(f"Completed {sum(r['status']=='complete' for r in results)}/{len(jobs)} pairs",flush=True)

if __name__=='__main__':main()
