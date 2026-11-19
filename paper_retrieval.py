"""Build and search a local BM25 paper index. No API calls or embeddings required."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parent
STOP = set('a an and are as at be by for from has have how in is it of on or that the their this to was were what which with'.split())


def tokens(text):
    text = unicodedata.normalize('NFKC', text)
    return [t for t in re.findall(r'[a-z0-9]+', text.lower()) if t not in STOP]


def build_index(output=ROOT/'papers/local/index.json', words=220, overlap=40):
    if not 0 <= overlap < words:
        raise ValueError('Require 0 <= overlap < chunk words')
    manifest_path = ROOT/'papers/manifest.json'
    manifest = json.loads(manifest_path.read_text())
    report = json.loads((ROOT/'papers/local/extraction_report.json').read_text())
    if report.get('status') != 'complete':
        raise ValueError('Run collect_papers.py successfully before indexing')
    if report['manifest_sha256'] != hashlib.sha256(manifest_path.read_bytes()).hexdigest():
        raise ValueError('Manifest changed; rerun collect_papers.py')
    chunks = []
    for paper in manifest['papers']:
        ident = paper['paper_id']
        digest = hashlib.sha256((ROOT/f'papers/local/pdf/{ident}.pdf').read_bytes()).hexdigest()
        pages = [json.loads(line) for line in (ROOT/f'papers/local/pages/{ident}.jsonl').read_text().splitlines()]
        for page in pages:
            if page['pdf_sha256'] != digest:
                raise ValueError(f'Stale page extraction for {ident}')
            parts = page['text'].split()
            for start in range(0, len(parts), words-overlap):
                text = ' '.join(parts[start:start+words])
                if not text:
                    continue
                chunk = {k: page[k] for k in ('paper_id','title','pdf_page','page_label','source_url','pdf_sha256')}
                chunk.update(chunk_id=f'{ident}:p{page["pdf_page"]}:w{start}', text=text)
                chunks.append(chunk)
                if start+words >= len(parts):
                    break
    result = dict(schema_version=1, method='BM25', chunk_words=words, overlap_words=overlap,
                  manifest_sha256=report['manifest_sha256'], datasets=manifest['datasets'], chunks=chunks)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False))
    return result


class PaperIndex:
    def __init__(self, path=ROOT/'papers/local/index.json'):
        self.data = json.loads(Path(path).read_text())
        current = hashlib.sha256((ROOT/'papers/manifest.json').read_bytes()).hexdigest()
        if self.data['manifest_sha256'] != current:
            raise ValueError('Stale index; rebuild it')
        for ident in {c['paper_id'] for c in self.data['chunks']}:
            digest = hashlib.sha256((ROOT/f'papers/local/pdf/{ident}.pdf').read_bytes()).hexdigest()
            if any(c['pdf_sha256'] != digest for c in self.data['chunks'] if c['paper_id'] == ident):
                raise ValueError('Paper PDF changed; rerun extraction and rebuild the index')
        self.mapping = {d['dataset_id']:d['paper_id'] for d in self.data['datasets']}

    def search(self, query, dataset_id, top_k=4):
        if dataset_id not in self.mapping:
            raise ValueError(f'Unknown dataset ID: {dataset_id}')
        if not 1 <= top_k <= 20:
            raise ValueError('top_k must be between 1 and 20')
        terms = set(tokens(query))
        if not terms:
            return []
        # Restrict evidence to the mapped paper before calculating scores.
        docs = [c for c in self.data['chunks'] if c['paper_id']==self.mapping[dataset_id]]
        counts = [Counter(tokens(c['text'])) for c in docs]
        lengths = [sum(c.values()) for c in counts]
        avg = sum(lengths)/max(len(docs),1)
        df = Counter(t for c in counts for t in c)
        ranked = []
        for doc, count, length in zip(docs, counts, lengths):
            score = 0.0
            for term in terms:
                tf = count[term]
                if tf:
                    idf = math.log(1+(len(docs)-df[term]+0.5)/(df[term]+0.5))
                    score += idf*tf*2.5/(tf+1.5*(0.25+0.75*length/avg))
            if score > 0:
                ranked.append(dict(doc, score=round(score,6)))
        ranked.sort(key=lambda c: (-c['score'], c['chunk_id']))
        # Suppress overlapping windows from the same page among top results.
        hits=[]; pages=set()
        for hit in ranked:
            key=(hit['paper_id'],hit['pdf_page'])
            if key not in pages:
                hits.append(hit); pages.add(key)
            if len(hits)==top_k:
                break
        return hits


def context_text(hits):
    return '\n\n'.join(f"[{h['chunk_id']}] {h['title']} | PDF page {h['pdf_page']} | {h['source_url']}\n{h['text']}" for h in hits)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('build')
    search=sub.add_parser('search')
    search.add_argument('--dataset-id',required=True)
    search.add_argument('--query',required=True)
    search.add_argument('--top-k',type=int,default=4)
    args=parser.parse_args()
    if args.command=='build':
        data=build_index(); print(f"Indexed {len(data['chunks'])} passages from five papers.")
    else:
        print(json.dumps(PaperIndex().search(args.query,args.dataset_id,args.top_k),indent=2,ensure_ascii=False))

if __name__=='__main__':
    main()
