"""Generate reviewed descriptions with explicitly added table documentation.

This is a separate input condition, not a held-out-codebook evaluation.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
import getpass
import hashlib
import json
import os
from pathlib import Path
import re
import time
from openai import OpenAI
from pypdf import PdfReader
from run_grounded import ROOT,prepare,digest
from paper_retrieval import PaperIndex,context_text
from grounded_generation import build_excerpt_catalog,generate_json
from strict_generation import (retrieve_table_evidence,EXTRACT_SYSTEM,AUDIT_SYSTEM,
    FINAL_AUDIT_SYSTEM,validate_claims,validate_audit,approved,render_approved)

DOCUMENTED_EXTRACT = EXTRACT_SYSTEM + """
This run ALSO provides the released table's own documentation, explicitly bound
to the CSV filename by their common source folder. This is intentional additional
input, not held-out evaluation data. Prefer its definitions over general paper
methods, figure definitions and conflicting paper versions. Documentary table
numbers may differ from the source folder's label. The explicit binding establishes
which table a documentation passage describes, so do not demand that every quote
repeat the CSV filename. Cite documentation for table-specific mappings and paper
only for additional consistent context. Prioritize row unit, population/grouping,
measurement periods and important distinctions among fields. Do not silently
combine incompatible definitions. If useful definitions need more than eight
sentences, select the important ones and report remaining limitations.
"""
DOCUMENTED_AUDIT = """
This is a documentation-assisted run: the table documentation is provided and
explicitly bound to the CSV filename by their shared source folder. It is an
additional input, not an independent evaluation reference. This binding is valid
source metadata for table applicability; the documentation need not repeat the
CSV filename in every sentence. Prefer table-specific documentation to paper
figure/regression definitions when they conflict, and flag the disagreement.
Check the full supplied documentation context, not just isolated fragments.
"""


def documentation_hits(pdf,dataset_id):
    sha=digest(pdf);hits=[]
    for page_num,page in enumerate(PdfReader(pdf).pages,1):
        words=(page.extract_text() or '').split()
        for start in range(0,len(words),180):
            text=' '.join(words[start:start+220])
            if len(text)<12:continue
            hits.append({'chunk_id':f'documentation:{dataset_id}:p{page_num}:w{start}',
                'paper_id':'documentation:'+dataset_id,'title':pdf.name,'pdf_page':page_num,
                'source_url':pdf.name,'pdf_sha256':sha,'text':text,'source_type':'table_documentation'})
            if start+220>=len(words):break
    if not hits:raise ValueError('No text extracted from table documentation')
    return hits


def one(dataset,previous,inputs,output,key):
    started=time.perf_counter();csvs=list(inputs.rglob(dataset['csv_filename']))
    if len(csvs)!=1:raise ValueError('Expected exactly one CSV')
    csv=csvs[0];pdfs=list(csv.parent.glob('*.pdf'))
    if len(pdfs)!=1:raise ValueError('Expected one table documentation PDF alongside CSV')
    pdf=pdfs[0];baseline=previous/dataset['dataset_id']/'baseline'
    payload,_,info=prepare(csv,dataset['dataset_id'],baseline,output,None)
    paper_hits,queries=retrieve_table_evidence(PaperIndex(),dataset,payload['columns'])
    doc_hits=documentation_hits(pdf,dataset['dataset_id']);hits=doc_hits+paper_hits
    # Never let paper relevance ranking crowd the table's own definitions out.
    docs=build_excerpt_catalog(doc_hits,limit=150)
    papers=build_excerpt_catalog(paper_hits,' '.join(queries[:2]),limit=32)
    catalog=[]
    for item in docs+papers:catalog.append(dict(item,excerpt_id=f'E{len(catalog):04d}'))
    payload.pop('tentative_semantic_guesses',None);payload.pop('paper_passages',None)
    binding={'dataset_file':csv.name,'documentation_file':pdf.name,
             'same_source_folder':str(csv.parent.relative_to(inputs)),
             'csv_sha256':digest(csv),'documentation_sha256':digest(pdf)}
    payload.update(dataset_file=csv.name,documentation_binding=binding,
                   observed_profile=(baseline/'content_profile.md').read_text())
    info.update(status='prepared',method='table_documentation_assisted_verbatim_v1',
                used_readme_context=True,used_table_documentation=True,
                documentation_binding=binding,retrieval_queries=queries,
                retrieved_chunk_ids=[h['chunk_id'] for h in hits],
                code_sha256={n:digest(ROOT/n) for n in ['run_documented.py','strict_generation.py','run_grounded.py','grounded_generation.py','paper_retrieval.py']},
                final_rendering='Verbatim claims surviving both audits',
                evaluation_warning='Documentation is generation input in this condition; agreement with the same documentation is a consistency check, not held-out accuracy.',
                note='Separate from preserved CSV-only and paper-only results; no Stata context.')
    def save():output.joinpath('generation.json').write_text(json.dumps(info,indent=2))
    save()
    for name,value in [('reconciliation_payload.json',payload),('retrieved_passages.json',hits),('excerpt_catalog.json',catalog)]:
        output.joinpath(name).write_text(json.dumps(value,indent=2))
    output.joinpath('paper_context.txt').write_text(context_text(hits))
    calls=0
    try:
        with OpenAI(api_key=key,timeout=240,max_retries=0) as client:
            candidates,n=generate_json(client,'gpt-4.1',DOCUMENTED_EXTRACT,{**payload,'evidence_excerpts':catalog},
                lambda v:validate_claims(v,payload['columns'],catalog),output,'candidate_claims');calls+=n
            claims=candidates['claims']
            for stage,system in [('table_support_review',AUDIT_SYSTEM),('final_claim_audit',FINAL_AUDIT_SYSTEM)]:
                if not claims:break
                used={e['chunk_id'] for c in claims for e in c['evidence']}
                # The short codebook is complete here to avoid clipped definitions.
                contexts=doc_hits+[h for h in paper_hits if h['chunk_id'] in used]
                audit,n=generate_json(client,'gpt-5.1',system+DOCUMENTED_AUDIT,
                    {**payload,'claims':claims,'cited_source_context':contexts},
                    lambda v:validate_audit(v,claims),output,stage);calls+=n
                claims=approved(claims,audit)
            output.joinpath('approved_claims.json').write_text(json.dumps(claims,indent=2))
            output.joinpath('description.md').write_text(render_approved(claims,dataset['name'],info['rows'],len(info['columns'])))
            info.update(status='generated' if claims else 'abstained',accepted_claims=len(claims),candidate_claims=len(candidates['claims']),
                        llm_calls=calls,llm_calls_made_by_this_run=True,limitations=candidates['limitations'],seconds=time.perf_counter()-started,
                        unresolved_columns=[c for c in payload['columns'] if not any(c in claim['columns'] for claim in claims)])
            save();return info
    except Exception as e:
        info.update(status='failed',error_type=type(e).__name__,llm_calls=calls,llm_calls_made_by_this_run=True);save();raise


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--previous-results',type=Path,required=True)
    p.add_argument('--inputs',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--dataset-id',action='append')
    args=p.parse_args()
    datasets=json.loads((ROOT/'papers/manifest.json').read_text())['datasets']
    if args.dataset_id:
        unknown=set(args.dataset_id)-{d['dataset_id'] for d in datasets}
        if unknown:p.error('Unknown dataset ID')
        datasets=[d for d in datasets if d['dataset_id'] in args.dataset_id]
    if args.output.exists() and any(args.output.iterdir()):p.error('Use a fresh output root')
    for d in datasets:
        if not (args.previous_results/d['dataset_id']/'baseline/generation.json').exists():p.error('Missing baseline: '+d['dataset_id'])
        matches=list(args.inputs.rglob(d['csv_filename']))
        if len(matches)!=1 or len(list(matches[0].parent.glob('*.pdf')))!=1:p.error('Ambiguous CSV/documentation binding: '+d['dataset_id'])
    key=os.environ.get('OPENAI_API_KEY') or getpass.getpass('API key (hidden; not saved): ').strip()
    if not key:p.error('No API key')
    args.output.mkdir(parents=True,exist_ok=True);results=[]
    def job(d):
        print(d['dataset_id'],'started',flush=True)
        try:
            info=one(d,args.previous_results,args.inputs,args.output/d['dataset_id'],key)
            print(d['dataset_id'],info['status'],info.get('accepted_claims'),flush=True)
            return {'dataset_id':d['dataset_id'],**info}
        except Exception as e:
            print(d['dataset_id'],'failed:',type(e).__name__,flush=True)
            return {'dataset_id':d['dataset_id'],'status':'failed','error_type':type(e).__name__}
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            for f in as_completed([pool.submit(job,d) for d in datasets]):
                results.append(f.result());(args.output/'results.json').write_text(json.dumps(results,indent=2))
    finally:key=None
    print('Statuses:',{s:sum(r['status']==s for r in results) for s in {r['status'] for r in results}},flush=True)

if __name__=='__main__':main()
