"""Offline checks using the real corpus. Run after collect_papers.py and index build."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

from paper_retrieval import PaperIndex, ROOT


class RetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=PaperIndex()

    def test_all_ten_dataset_filters_and_citations(self):
        for dataset in self.index.data['datasets']:
            with self.subTest(dataset=dataset['dataset_id']):
                hits=self.index.search(dataset['name'],dataset['dataset_id'])
                self.assertTrue(hits)
                self.assertTrue(all(h['paper_id']==dataset['paper_id'] for h in hits))
                self.assertEqual(len(hits),len({h['pdf_page'] for h in hits}))
                for hit in hits:
                    pages=ROOT/f"papers/local/pages/{hit['paper_id']}.jsonl"
                    page=next(json.loads(line) for line in pages.read_text().splitlines() if json.loads(line)['pdf_page']==hit['pdf_page'])
                    self.assertIn(hit['text'],' '.join(page['text'].split()))
                    self.assertEqual(hit['pdf_sha256'],page['pdf_sha256'])

    def test_unknown_and_unmatched_queries(self):
        with self.assertRaises(ValueError):
            self.index.search('income','not_a_dataset')
        self.assertEqual(self.index.search('zzzzunmatchedtoken','life_county_expectancy'),[])
        self.assertEqual(self.index.search('the and','life_county_expectancy'),[])

    def test_method_passage_is_retrieved(self):
        hits=self.index.search('How are inventors linked to college attendance?', 'inventors_college',3)
        self.assertTrue(any('College Attendance' in h['text'] for h in hits))

    def test_stale_index_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'index.json'
            p.write_text(json.dumps(dict(self.index.data,manifest_sha256='old')))
            with self.assertRaises(ValueError): PaperIndex(p)

    def test_generation_receives_evidence_without_network(self):
        import run_baseline
        captured={}
        class FakePipeline:
            def __init__(self,**kwargs): pass
            def analyze_semantics(self,sample): return 'Test semantics'
            def describe_dataset(self,**kwargs):
                captured.update(kwargs)
                return 'Test prompt','Test description'
        with tempfile.TemporaryDirectory() as tmp:
            args=['run_baseline.py','--csv',str(ROOT/'data/health_ineq_online_table_11.csv'),
                  '--dataset-id','life_county_expectancy','--output',tmp,'--generate']
            with patch.object(sys,'argv',args), patch.dict('os.environ',{'OPENAI_API_KEY':'offline-test-placeholder'}), patch.object(run_baseline,'AutoDDG',FakePipeline), patch('openai.OpenAI'):
                run_baseline.main()
            info=json.loads((Path(tmp)/'generation.json').read_text())
            self.assertEqual(info['status'],'paper_enriched_generated')
            self.assertTrue(info['used_paper_context'])
            self.assertIn('RESEARCH PAPER EVIDENCE',captured['dataset_profile'])
            self.assertIn('PDF page',captured['dataset_profile'])
            self.assertFalse(info['used_readme_context'])

if __name__=='__main__': unittest.main()
