"""Download the five project papers and extract text with PDF page references."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import ssl
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def download(url, target):
    request = urllib.request.Request(url, headers={'User-Agent': 'BigDataProjectPaperCollector/1.0'})
    # Use the interpreter's normal certificate checks; do not disable TLS verification.
    with urllib.request.urlopen(request, timeout=120, context=ssl.create_default_context()) as response:
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as out:
            temporary = Path(out.name)
            try:
                size = 0
                while chunk := response.read(1024 * 1024):
                    size += len(chunk)
                    if size > 100 * 1024 * 1024:
                        raise ValueError('Paper exceeds the 100 MB download limit')
                    out.write(chunk)
            except BaseException:
                temporary.unlink(missing_ok=True)
                raise
        resolved_url = response.url
    if not temporary.read_bytes().startswith(b'%PDF-'):
        temporary.unlink(missing_ok=True)
        raise ValueError('Source returned a non-PDF response')
    temporary.replace(target)
    return resolved_url


def extract(paper, pdf_path, output, resolved_url):
    reader = PdfReader(pdf_path)
    if reader.is_encrypted:
        raise ValueError('Encrypted PDF requires a different public source')
    digest = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
    records = []
    labels = reader.page_labels
    for index, page in enumerate(reader.pages):
        text = page.extract_text() or ''
        # Preserve original extracted wording; remove only NULs and trailing whitespace.
        text = '\n'.join(line.rstrip() for line in text.replace('\x00', '').splitlines()).strip()
        records.append(dict(paper_id=paper['paper_id'], title=paper['title'],
            pdf_page=index + 1, page_label=labels[index], source_url=paper['pdf_url'],
            pdf_sha256=digest, text=text))
    first_pages = re.sub(r'\s+', ' ', ' '.join(r['text'] for r in records[:3])).lower()
    if not all(term.lower() in first_pages for term in paper['title_terms']):
        raise ValueError('Expected title not found in first three pages; inspect this PDF')
    chars = sum(len(r['text']) for r in records)
    if len(records) < 10 or chars < 10_000:
        raise ValueError('Extraction too short for the expected full research paper')
    page_dir = output / 'pages'
    text_dir = output / 'text'
    page_dir.mkdir(exist_ok=True)
    text_dir.mkdir(exist_ok=True)
    (page_dir / f"{paper['paper_id']}.jsonl").write_text(
        ''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in records), encoding='utf-8')
    (text_dir / f"{paper['paper_id']}.txt").write_text(
        '\n\n'.join(f"[PDF page {r['pdf_page']}; label {r['page_label']}]\n{r['text']}" for r in records), encoding='utf-8')
    return dict(paper_id=paper['paper_id'], title=paper['title'],
        source_url=paper['pdf_url'], resolved_url=resolved_url,
        pdf_sha256=digest, pdf_bytes=pdf_path.stat().st_size,
        page_count=len(records), extracted_characters=chars,
        low_text_pdf_pages=[r['pdf_page'] for r in records if len(r['text']) < 100],
        title_verified=True, status='extracted')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT/'papers/manifest.json')
    parser.add_argument('--output', type=Path, default=ROOT/'papers/local')
    parser.add_argument('--refresh', action='store_true', help='Redownload existing PDFs; checksums may change')
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    paper_ids = [p['paper_id'] for p in manifest['papers']]
    dataset_ids = [d['dataset_id'] for d in manifest['datasets']]
    assert len(paper_ids) == len(set(paper_ids)), 'Duplicate paper IDs'
    assert len(dataset_ids) == len(set(dataset_ids)), 'Duplicate dataset IDs'
    assert all(d['paper_id'] in paper_ids for d in manifest['datasets']), 'Unmapped dataset'
    output = args.output
    pdf_dir = output / 'pdf'
    pdf_dir.mkdir(parents=True, exist_ok=True)
    report = dict(created_utc=datetime.now(timezone.utc).isoformat(),
        manifest_sha256=hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
        dataset_count=len(dataset_ids), paper_count=len(paper_ids), papers=[], errors=[])
    for paper in manifest['papers']:
        ident = paper['paper_id']
        if not re.fullmatch(r'[a-z0-9_]+', ident):
            raise ValueError('Unsafe paper ID')
        pdf_path = pdf_dir / f'{ident}.pdf'
        try:
            resolved = download(paper['pdf_url'], pdf_path) if args.refresh or not pdf_path.exists() else None
            result = extract(paper, pdf_path, output, resolved)
            report['papers'].append(result)
            print(f"{ident}: {result['page_count']} pages; {result['extracted_characters']:,} text characters", flush=True)
        except Exception as error:
            report['errors'].append(dict(paper_id=ident, error=str(error)))
            print(f'{ident}: FAILED ({type(error).__name__})', flush=True)
        write_json(output/'extraction_report.json', report)
    report['status'] = 'complete' if not report['errors'] else 'incomplete'
    write_json(output/'extraction_report.json', report)
    if report['errors']:
        raise SystemExit('Some papers failed. See extraction_report.json; incomplete papers must not be indexed.')
    print(f"Complete: {len(report['papers'])} papers mapped to {len(dataset_ids)} datasets.")


if __name__ == '__main__':
    main()
