"""Reproduce a focused, source-based paired comparison; no model/API calls."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
FRESH_IDS={'inventors_childhood_cz','college_access_mobility'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_annotations(rubric,annotations):
    if set(annotations['datasets'])!=set(rubric['datasets']):raise ValueError('Dataset annotations are incomplete')
    allowed=set(rubric['labels'])
    for ident,targets in rubric['datasets'].items():
        checks=annotations['datasets'][ident]
        if len(checks)!=len(targets):raise ValueError('Incomplete target coverage for '+ident)
        for i,check in enumerate(checks):
            if check['target']!=targets[i] or check['check_id']!=f'{ident}:{i+1}':raise ValueError('Rubric/annotation identity mismatch')
            if set(check['judgments'])!=set(rubric['conditions']):raise ValueError('Incomplete conditions')
            for value in check['judgments'].values():
                if value['label'] not in allowed:raise ValueError('Unknown outcome label')
                if not value['rationale'].strip() or 'PENDING' in value['rationale']:raise ValueError('Unfinished annotation')


def count_labels(checks,condition,status):
    labels=[c['judgments'][condition]['label'] for c in checks]
    if status=='abstained' and any(x!='abstained' for x in labels):raise ValueError('An abstention cannot receive semantic credit')
    if status!='abstained' and 'abstained' in labels:raise ValueError('Abstained label used for a non-abstaining run')
    return dict(Counter(labels))


def verify_pair(base,folder,condition):
    b=json.loads((base/'generation.json').read_text());info=json.loads((folder/'generation.json').read_text())
    if condition=='csv_baseline':return b
    for name in ['sample.csv','content_profile.md','semantic_profile.md']:
        if (base/name).read_bytes()!=(folder/name).read_bytes():raise ValueError('Pair parity failed: '+name)
    if info['csv_sha256']!=b['csv_sha256'] or info['rows']!=b['rows'] or info['columns']!=b['columns']:
        raise ValueError('Input identity/dimension mismatch')
    if bool(info['used_readme_context'])!=(condition=='documentation_assisted') or info['used_stata_context']:
        raise ValueError('Input condition mislabeled')
    if info['status'] not in ['generated','abstained']:raise ValueError('Cannot evaluate incomplete/failed output as complete')
    return info


def evaluate(args):
    rubric=json.loads((ROOT/'evaluation/rubric.json').read_text())
    annotations=json.loads((ROOT/'evaluation/annotations.json').read_text());validate_annotations(rubric,annotations)
    previous=json.loads((ROOT/'papers/description_accuracy_summary.json').read_text())
    bymode={k:{r['dataset_id']:r for r in v['datasets']} for k,v in previous['conditions'].items()}
    datasets=[];totals={c:Counter() for c in rubric['conditions']}
    for ident in rubric['datasets']:
        base=args.baseline_root/ident/'baseline'
        folders={'csv_baseline':base,'strict_paper_only':args.results_root/bymode['paper_only'][ident]['source_directory'],
                 'documentation_assisted':args.fresh_root/ident if ident in FRESH_IDS else args.results_root/bymode['documentation_assisted'][ident]['source_directory']}
        record={'dataset_id':ident,'checks':annotations['datasets'][ident],'conditions':{}}
        for condition,folder in folders.items():
            info=verify_pair(base,folder,condition)
            counts=count_labels(record['checks'],condition,info['status'])
            totals[condition].update(counts)
            record['conditions'][condition]={'status':info['status'],'description':(folder/'description.md').read_text(),
                'description_sha256':sha(folder/'description.md'),'generation_sha256':sha(folder/'generation.json'),
                'csv_sha256':info['csv_sha256'],
                'source_root':'baseline' if condition=='csv_baseline' else 'fresh' if condition=='documentation_assisted' and ident in FRESH_IDS else 'revised',
                'source_directory':str(folder.relative_to(args.baseline_root if condition=='csv_baseline' else args.fresh_root if condition=='documentation_assisted' and ident in FRESH_IDS else args.results_root)),'labels':counts,
                'rows':info['rows'],'columns':len(info['columns'])}
        if ident in FRESH_IDS:
            prior=args.results_root/bymode['documentation_assisted'][ident]['source_directory']
            record['prior_documented_description_sha256']=sha(prior/'description.md')
            record['fresh_verification']=True
            record['fresh_output_changed']=sha(prior/'description.md')!=sha(folders['documentation_assisted']/'description.md')
        datasets.append(record)
    args.output.mkdir(parents=True,exist_ok=True)
    result={'annotation_method':rubric['annotation_method'],'scope':rubric['scope'],
            'reference_leakage_note':rubric['documentation_rule'],
            'selection_rule':rubric['selection_rule'],
            'limitations':['Focused checks are correlated and incomplete; counts are not overall factual accuracy.',
                'Development cases were inspected previously; there is no blind holdout or independent human rater.',
                'Documentation-assisted agreement is source consistency because the same documentation was a model input.',
                'Generation models, prompts, retrieval, review stages and output lengths differ; this is not a single-component ablation or a matched-token-budget experiment.',
                'One fresh run per flagged case is insufficient to estimate repeatability or variance.'],
            'checks_per_condition':sum(len(v) for v in rubric['datasets'].values()),
            'totals':{c:dict(t) for c,t in totals.items()},'datasets':datasets,
            'annotation_sha256':sha(ROOT/'evaluation/annotations.json'),'rubric_sha256':sha(ROOT/'evaluation/rubric.json')}
    (args.output/'comparison.json').write_text(json.dumps(result,indent=2))
    order=list(rubric['labels']);headers=['Condition']+order
    lines=['# Paired description comparison','',
        'Compared all ten original CSV baselines with the revised paper-only and documentation-assisted outputs. Two previously flagged documented cases received one fresh verification run each under unchanged generation code; both prior outputs are preserved. The fresh outputs are selected regardless of whether they look better. Curated reference descriptions receive no model-performance credit.','',
        '## Focused source-based review','',
        'Four prewritten targets per dataset give 40 checks per condition. Annotations were prepared by Codex from the supplied documentation and CSV, with no independent human rater or blinding. This is a development comparison, not an overall accuracy score.','',
        '| '+' | '.join(headers)+' |','|'+'|'.join(['---']+['---:']*len(order))+'|']
    for c in rubric['conditions']:lines.append('| '+c+' | '+' | '.join(str(totals[c].get(label,0)) for label in order)+' |')
    lines+=['','Supported means the full target is clearly expressed; partial means valid but incomplete. Omitted and abstained are separate from incorrect or ambiguous. Abstention counts refer to target checks, not datasets: six paper-only dataset abstentions produce 24 abstained targets.','',
        '## What changed','',
        '- Baseline errors include treating CZs as cities, income quartiles as calendar quarters, bottom income quintile as a quartile, and mortality cells as individual records.',
        '- The documented outputs explain the mortality denominator and age-specific income lag, both adjustment statuses and standard errors, and adult income-rank fields much more explicitly.',
        '- The paper-only condition remains cautious: four datasets have approved semantic claims and six abstain. Its supported claims do not imply complete table descriptions.',
        '- In the fresh childhood-inventor run, both misleading highly-cited-patent claims disappear. The correct highly-cited-inventor definition is still omitted, so this is not counted as a fully corrected definition.',
        '- In the fresh mobility run, the joint mobility share uses the bottom-parent AND top-child events over students, while the conditional rate is defined separately. The median-income sentence remains ambiguous about household time averaging versus the college-level median.',
        '- Expenditure review respects both actual column families: `exp_instr_*` totals and `exp_instr_pc_*` per-student fields. The former audit’s broader claim that per-student wording was necessarily wrong is not reused.','',
        '## Per-dataset target counts','',
        'Cells show supported / partial / omitted / incorrect / ambiguous / abstained, in that order.','',
        '| Dataset | CSV baseline | Strict paper-only | Documented |','|---|---|---|---|']
    for r in datasets:
        cells=[' / '.join(str(r['conditions'][c]['labels'].get(label,0)) for label in order) for c in rubric['conditions']]
        lines.append('| '+r['dataset_id']+' | '+' | '.join(cells)+' |')
    lines+=['','## Interpretation limits','']+[f'- {x}' for x in result['limitations']]
    lines+=['','Detailed judgments and rationales: `evaluation/annotations.json`. Full selected descriptions, input/output hashes and source locations: `comparison.json`. These artifacts preserve the distinction between model drafts and the separately reviewed reference descriptions.']
    (args.output/'REPORT.md').write_text('\n'.join(lines)+'\n')
    detail=['# Side-by-side outputs','', 'These are generated descriptions, not the corrected reference text. Sources and condition labels are preserved.','']
    for r in datasets:
        detail+=['## '+r['dataset_id'],'']
        for c in rubric['conditions']:detail+=['### '+c,'',r['conditions'][c]['description'].strip(),'']
        detail+=['### Target judgments','','| Target | Baseline | Strict paper | Documented |','|---|---|---|---|']
        for check in r['checks']:detail.append('| '+check['target']+' | '+' | '.join(check['judgments'][c]['label'] for c in rubric['conditions'])+' |')
        detail+=['']
    (args.output/'SIDE_BY_SIDE.md').write_text('\n'.join(detail)+'\n')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline-root',type=Path,required=True)
    p.add_argument('--results-root',type=Path,required=True)
    p.add_argument('--fresh-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();result=evaluate(args)
    print(json.dumps(result['totals'],indent=2))

if __name__=='__main__':main()
