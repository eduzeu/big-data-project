"""Check documentation provenance and separate citation namespaces offline."""
import hashlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from run_documented import documentation_hits,DOCUMENTED_EXTRACT,DOCUMENTED_AUDIT
from grounded_generation import build_excerpt_catalog,normalize

class DocumentationTests(unittest.TestCase):
    def test_table_document_excerpts_have_distinct_ids_and_exact_provenance(self):
        text=' '.join('word'+str(i) for i in range(500))
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'codebook.pdf';p.write_bytes(b'offline fixture')
            with patch('run_documented.PdfReader',return_value=SimpleNamespace(pages=[SimpleNamespace(extract_text=lambda:text)])):
                hits=documentation_hits(p,'table_a')
            self.assertEqual(len(hits),3)
            self.assertEqual(len({h['chunk_id'] for h in hits}),3)
            self.assertTrue(all(h['chunk_id'].startswith('documentation:table_a:') for h in hits))
            self.assertTrue(all(h['pdf_sha256']==hashlib.sha256(p.read_bytes()).hexdigest() for h in hits))
            for e in build_excerpt_catalog(hits,limit=150):
                source=next(h for h in hits if h['chunk_id']==e['chunk_id'])
                self.assertIn(normalize(e['quote']),normalize(source['text']))

    def test_empty_document_fails_instead_of_silently_using_paper(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'empty.pdf';p.write_bytes(b'fixture')
            with patch('run_documented.PdfReader',return_value=SimpleNamespace(pages=[SimpleNamespace(extract_text=lambda:'')])):
                with self.assertRaises(ValueError):documentation_hits(p,'table_a')

    def test_documentation_is_declared_as_additional_input(self):
        self.assertIn('not held-out evaluation',DOCUMENTED_EXTRACT)
        self.assertIn('additional input',DOCUMENTED_AUDIT)

if __name__=='__main__':unittest.main()
