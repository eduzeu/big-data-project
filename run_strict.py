"""Rerun paired datasets with table-specific evidence checks; preserve previous runs."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
import getpass
import json
import os
from pathlib import Path
import time
from openai import OpenAI

from run_grounded import prepare,digest,ROOT
from paper_retrieval import PaperIndex,context_text
from grounded_generation import build_excerpt_catalog,generate_json
from strict_generation import (retrieve_table_evidence,EXTRACT_SYSTEM,AUDIT_SYSTEM,
    FINAL_AUDIT_SYSTEM,validate_claims,validate_audit,approved,render_approved)


def run_one(dataset,baseline,output,key=None,generate=False):
    started=time.perf_counter()
    csv=baseline/'source.csv'
    # Locate original CSV from the downloaded collection, never regenerate it.
    if not csv.exists():
        matches=list((ROOT/'data').rglob(dataset['csv_filename']))
        matching=[p for p in matches if digest(p)==json.loads((baseline/'generation.json').read_text())['csv_sha256']]
        if not matching:raise ValueError('No checksum-matching CSV found for '+dataset['dataset_id'])
        csv=matching[0]
    payload,_,info=prepare(csv,dataset['dataset_id'],baseline,output,None)
    index=PaperIndex();hits,queries=retrieve_table_evidence(index,dataset,payload['columns'])
    catalog=build_excerpt_catalog(hits,' '.join(queries[:2]),limit=96)
    info.update(method='table_specific_verbatim_v2',status='prepared',retrieval_queries=queries,
                retrieval_method='three-query reciprocal-rank fusion; 12 anchors plus same-page neighbors',
                retrieved_chunk_ids=[h['chunk_id'] for h in hits],anchor_chunk_ids=[h['chunk_id'] for h in hits if 'fusion_score' in h],
                retrieval_query=' '.join(queries[:2]),
                code_sha256={n:digest(ROOT/n) for n in ['run_strict.py','strict_generation.py','run_grounded.py','grounded_generation.py','paper_retrieval.py']},
                final_rendering='Verbatim approved claims; no free-form generation after final audit',
                note='Development rerun after inspecting previous failures; not a blinded benchmark. Codebook/README/Stata excluded from generation.')
    payload.pop('tentative_semantic_guesses',None);payload.pop('paper_passages',None)
    payload['dataset_file']=csv.name
    payload['mapped_paper_id']=dataset['paper_id']
    payload['observed_profile']=(baseline/'content_profile.md').read_text()
    output.joinpath('reconciliation_payload.json').write_text(json.dumps(payload,indent=2))
    output.joinpath('retrieved_passages.json').write_text(json.dumps(hits,indent=2))
    output.joinpath('paper_context.txt').write_text(context_text(hits))
    output.joinpath('excerpt_catalog.json').write_text(json.dumps(catalog,indent=2))
    def save():output.joinpath('generation.json').write_text(json.dumps(info,indent=2))
    save()
    if not generate:return info
    calls=0
    try:
        with OpenAI(api_key=key,timeout=240,max_retries=0) as client:
            candidates,n=generate_json(client,'gpt-4.1',EXTRACT_SYSTEM,{**payload,'evidence_excerpts':catalog},
                lambda v:validate_claims(v,payload['columns'],catalog),output,'candidate_claims');calls+=n
            claims=candidates['claims']
            for stage,system in [('table_support_review',AUDIT_SYSTEM),('final_claim_audit',FINAL_AUDIT_SYSTEM)]:
                if not claims:break
                used={e['chunk_id'] for c in claims for e in c['evidence']}
                audit,n=generate_json(client,'gpt-5.1',system,{**payload,'claims':claims,
                    'cited_source_context':[h for h in hits if h['chunk_id'] in used]},
                    lambda v:validate_audit(v,claims),output,stage);calls+=n
                claims=approved(claims,audit)
            output.joinpath('approved_claims.json').write_text(json.dumps(claims,indent=2))
            output.joinpath('description.md').write_text(render_approved(claims,dataset['name'],info['rows'],len(info['columns'])))
            info.update(status='generated' if claims else 'abstained',accepted_claims=len(claims),candidate_claims=len(candidates['claims']),
                        llm_calls=calls,llm_calls_made_by_this_run=True,
                        unresolved_columns=[c for c in payload['columns'] if not any(c in claim['columns'] for claim in claims)],
                        limitations=candidates['limitations'],seconds=time.perf_counter()-started)
            save();return info
    except Exception as e:
        info.update(status='failed',error_type=type(e).__name__,llm_calls=calls,llm_calls_made_by_this_run=True)
        save();raise


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--previous-results',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--dataset-id',action='append')
    p.add_argument('--generate',action='store_true')
    args=p.parse_args()
    datasets=json.loads((ROOT/'papers/manifest.json').read_text())['datasets']
    if args.dataset_id:
        unknown=set(args.dataset_id)-{d['dataset_id'] for d in datasets}
        if unknown:p.error('Unknown datasets: '+', '.join(sorted(unknown)))
        datasets=[d for d in datasets if d['dataset_id'] in args.dataset_id]
    if args.output.exists() and any(args.output.iterdir()):p.error('Use a new empty output root to preserve all attempts')
    for d in datasets:
        if not (args.previous_results/d['dataset_id']/'baseline/generation.json').exists():p.error('Missing preserved baseline: '+d['dataset_id'])
    args.output.mkdir(parents=True,exist_ok=True)
    key=None
    if args.generate:
        key=os.environ.get('OPENAI_API_KEY') or getpass.getpass('API key (hidden; not saved): ').strip()
        if not key:p.error('No API key')
    def job(d):
        print(d['dataset_id'],'started',flush=True)
        try:
            info=run_one(d,args.previous_results/d['dataset_id']/'baseline',args.output/d['dataset_id'],key,args.generate)
            print(d['dataset_id'],info['status'],info.get('accepted_claims',''),flush=True)
            return {'dataset_id':d['dataset_id'],**info}
        except Exception as e:
            print(d['dataset_id'],'failed:',type(e).__name__,flush=True)
            return {'dataset_id':d['dataset_id'],'status':'failed','error_type':type(e).__name__}
    results=[]
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            for f in as_completed([pool.submit(job,d) for d in datasets]):
                results.append(f.result());(args.output/'results.json').write_text(json.dumps(results,indent=2))
    finally:key=None
    print('Statuses:',{s:sum(r['status']==s for r in results) for s in {r['status'] for r in results}},flush=True)

if __name__=='__main__':main()
