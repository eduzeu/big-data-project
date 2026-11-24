"""Generate a reconciled paper-enriched description using a preserved baseline run."""
from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
from pathlib import Path
import time

import pandas as pd

from paper_retrieval import PaperIndex, context_text
from grounded_generation import (RECONCILE_SYSTEM, REVIEW_SYSTEM, DESCRIPTION_SYSTEM, generate_json,
                                 validate_proposals, validate_description, validate_review, apply_review, build_excerpt_catalog, render_sentences)

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(csv, dataset_id, baseline_dir, output, query, reconciliation_model='gpt-4.1', review_model='gpt-5.1'):
    baseline = json.loads((baseline_dir/'generation.json').read_text())
    if baseline.get('status') != 'baseline_generated' or any(baseline.get(k) for k in
            ['used_paper_context','used_readme_context','used_stata_context']):
        raise ValueError('Supply a completed CSV-only baseline, not an enriched run')
    if digest(csv) != baseline['csv_sha256']:
        raise ValueError('CSV differs from the baseline input')
    if output.resolve() == baseline_dir.resolve() or output.exists() and any(output.iterdir()):
        raise ValueError('Choose a new empty output directory; completed runs are preserved')
    frame = pd.read_csv(csv)
    if frame.empty or list(frame.columns) != baseline['columns'] or len(frame) != baseline['rows']:
        raise ValueError('CSV dimensions/columns do not match the baseline')
    sample = frame.sample(n=min(baseline['sample_rows'],len(frame)),random_state=baseline['seed']).reset_index(drop=True).to_csv(index=False)
    if sample != (baseline_dir/'sample.csv').read_text():
        raise ValueError('Sample differs from baseline; check pandas version and settings')
    semantic = (baseline_dir/'semantic_profile.md').read_text()
    if not semantic.strip():
        raise ValueError('Baseline semantic profile is empty')
    index = PaperIndex()
    dataset = next((d for d in index.data['datasets'] if d['dataset_id']==dataset_id),None)
    if dataset is None or dataset['csv_filename'] != csv.name:
        raise ValueError('Dataset ID does not match the CSV filename')
    query = query or dataset['name']+' '+' '.join(frame.columns)
    hits = index.search(query,dataset_id)
    if not hits:
        raise ValueError('No evidence retrieved; revise the query')
    # Include adjacent windows so definitions cut at a passage boundary remain readable.
    anchors=list(hits)
    seen={h['chunk_id'] for h in hits}
    for hit in anchors:
        window=[c for c in index.data.get('chunks',[])
                if c['paper_id']==hit['paper_id'] and c['pdf_page']==hit['pdf_page']]
        ids=[c['chunk_id'] for c in window]
        if hit['chunk_id'] not in ids:
            continue
        position=ids.index(hit['chunk_id'])
        for c in window[max(0,position-1):position+2]:
            if c['chunk_id'] not in seen:
                hits.append(c);seen.add(c['chunk_id'])
    payload = {'dataset_label':dataset['name'],'columns':list(frame.columns),
               'observed_rows':len(frame),'csv_sample':sample,
               'tentative_semantic_guesses':semantic,'paper_passages':hits}
    output.mkdir(parents=True,exist_ok=True)
    for name in ['sample.csv','content_profile.md','semantic_profile.md']:
        output.joinpath(name).write_bytes(baseline_dir.joinpath(name).read_bytes())
    output.joinpath('retrieved_passages.json').write_text(json.dumps(hits,indent=2))
    output.joinpath('paper_context.txt').write_text(context_text(hits))
    output.joinpath('reconciliation_payload.json').write_text(json.dumps(payload,indent=2))
    info = {'status':'prepared','method':'paper_semantic_reconciliation_v1',
        'dataset_id':dataset_id,'dataset_file':csv.name,'csv_sha256':baseline['csv_sha256'],
        'rows':len(frame),'columns':list(frame.columns),'model':baseline['model'],
        'reconciliation_model':reconciliation_model,'review_model':review_model,
        'reconciliation_reasoning_effort':'medium' if reconciliation_model.startswith('gpt-5') else None,
        'review_reasoning_effort':'medium' if review_model.startswith('gpt-5') else None,
        'sample_rows':baseline['sample_rows'],'seed':baseline['seed'],
        'baseline_generation_sha256':digest(baseline_dir/'generation.json'),
        'semantic_profile_sha256':digest(baseline_dir/'semantic_profile.md'),
        'baseline_semantics_usage':'Preserved for comparison only; excluded from new model requests',
        'code_sha256':{name:digest(ROOT/name) for name in ['run_grounded.py','grounded_generation.py']},
        'index_sha256':digest(ROOT/'papers/local/index.json'),
        'retrieval_query':query,'anchor_chunk_ids':[h['chunk_id'] for h in anchors],
        'context_expansion':'one adjacent window before/after each anchor, within the same PDF page',
        'retrieved_chunk_ids':[h['chunk_id'] for h in hits],
        'used_paper_context':True,'used_readme_context':False,'used_stata_context':False,
        'description_words':100,'llm_calls_made_by_this_run':False,
        'note':'Preserves the baseline for comparison; the profile is used only for support review, and final generation receives only the dataset label, dimensions and accepted facts.'}
    output.joinpath('generation.json').write_text(json.dumps(info,indent=2))
    return payload, hits, info


def run(client,payload,hits,info,output):
    start=time.perf_counter()
    catalog=build_excerpt_catalog(hits,info['retrieval_query'])
    output.joinpath('excerpt_catalog.json').write_text(json.dumps(catalog,indent=2))
    reconciliation_input={k:v for k,v in payload.items() if k not in ['csv_sample','paper_passages','tentative_semantic_guesses']}
    reconciliation_input['evidence_excerpts']=catalog
    facts, reconcile_calls = generate_json(client,info['reconciliation_model'],RECONCILE_SYSTEM,
        reconciliation_input,
        lambda value:validate_proposals(value,payload['columns'],hits,catalog),output,'reconciled_semantics')
    review, review_calls = generate_json(client,info['review_model'],REVIEW_SYSTEM,
        {'dataset_label':payload['dataset_label'],'columns':payload['columns'],'csv_sample':payload['csv_sample'],
         'observed_profile':(output/'content_profile.md').read_text(),'proposed_facts':facts['facts']},
        lambda value:validate_review(value,facts),output,'evidence_review')
    accepted=apply_review(facts,review,payload['columns'])
    output.joinpath('accepted_semantics.json').write_text(json.dumps(accepted,indent=2))
    # Raw semantic guesses are deliberately absent from the final description request.
    final_payload={'dataset_label':payload['dataset_label'],
        'observed_rows':info['rows'],'observed_columns':len(info['columns']),

        'accepted_facts':{f'F{i}':f for i,f in enumerate(accepted['facts'])},
        'unresolved_column_count':len(accepted['unresolved_columns'])}
    result, description_calls = generate_json(client,info['model'],DESCRIPTION_SYSTEM,final_payload,
        lambda value:render_sentences(value,accepted,info['rows'],len(info['columns'])),output,'grounded_description')
    output.joinpath('description.md').write_text(result['description']+'\n')
    info.update(status='paper_reconciled_generated',llm_calls_made_by_this_run=True,
                llm_calls=reconcile_calls+review_calls+description_calls,
                accepted_facts=len(accepted['facts']),unresolved_columns=accepted['unresolved_columns'],generation_seconds=time.perf_counter()-start,
                citation_validation='Passed ID and exact-excerpt checks; semantic support still needs review')
    output.joinpath('generation.json').write_text(json.dumps(info,indent=2))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv',type=Path,required=True)
    parser.add_argument('--dataset-id',required=True)
    parser.add_argument('--baseline-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--paper-query')
    parser.add_argument('--reconciliation-model',default='gpt-4.1')
    parser.add_argument('--review-model',default='gpt-5.1')
    parser.add_argument('--generate',action='store_true')
    parser.add_argument('--prompt-for-key',action='store_true')
    args=parser.parse_args()
    payload,hits,info=prepare(args.csv,args.dataset_id,args.baseline_dir,args.output,args.paper_query,args.reconciliation_model,args.review_model)
    print(f'Prepared {len(hits)} passages; reusing the exact baseline sample and semantic profile.',flush=True)
    if not args.generate:
        print('No API calls made. Add --generate --prompt-for-key to run.')
        return
    from openai import OpenAI
    key=None
    if args.prompt_for_key:
        key=getpass.getpass('API key (hidden; not saved): ').strip()
    if not key and not os.environ.get('OPENAI_API_KEY'):
        parser.error('No API key provided')
    try:
        with OpenAI(api_key=key or os.environ['OPENAI_API_KEY'],timeout=180,max_retries=0) as client:
            result=run(client,payload,hits,info,args.output)
    except KeyboardInterrupt:
        info.update(status='cancelled',llm_calls_made_by_this_run=True)
        (args.output/'generation.json').write_text(json.dumps(info,indent=2))
        raise
    except Exception as error:
        info.update(status='failed',error_type=type(error).__name__,llm_calls_made_by_this_run=True)
        (args.output/'generation.json').write_text(json.dumps(info,indent=2))
        raise
    finally:
        key=None
    print(result['description'])

if __name__=='__main__':main()
