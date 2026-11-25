"""Regression tests for table linkage, units, abstention and final text integrity."""
import copy
import unittest
from strict_generation import validate_claims,validate_audit,approved,render_approved,retrieve_table_evidence

CATALOG=[{'excerpt_id':'E0000','chunk_id':'p:p1:w0','quote':'The released table reports total instructional expenditure.'}]
CANDIDATE={'claims':[{'text':'Instructional expenditure is a total amount.', 'columns':['exp_instr_2000'],
                      'meaning_evidence_ids':['E0000'],'table_evidence_ids':['E0000']}],'limitations':[]}

def verdict(**overrides):
    return {'claim_index':0,'supported':True,'reason':'Both meaning and table link are explicit.',
            'definition_supported':True,'table_link_supported':True,
            'units_and_denominator_supported':True,'schema_consistent':True,**overrides}

class StrictTests(unittest.TestCase):
    def test_missing_table_link_rejected(self):
        bad=copy.deepcopy(CANDIDATE);bad['claims'][0]['table_evidence_ids']=[]
        with self.assertRaises(ValueError):validate_claims(bad,['exp_instr_2000'],CATALOG)

    def test_unknown_column_or_quote_rejected(self):
        for field,value in [('columns',['exp_per_student']),('meaning_evidence_ids',['E9999'])]:
            bad=copy.deepcopy(CANDIDATE);bad['claims'][0][field]=value
            with self.assertRaises(ValueError):validate_claims(bad,['exp_instr_2000'],CATALOG)

    def test_units_or_scope_failure_cannot_be_overridden_by_supported(self):
        for key in ['units_and_denominator_supported','table_link_supported','schema_consistent','definition_supported']:
            with self.subTest(key=key),self.assertRaises(ValueError):
                validate_audit({'verdicts':[verdict(**{key:False})]},[{}])

    def test_rejected_units_do_not_reach_description(self):
        claims=validate_claims(CANDIDATE,['exp_instr_2000'],CATALOG)['claims']
        audit={'verdicts':[verdict(supported=False,units_and_denominator_supported=False)]}
        accepted=approved(claims,audit)
        text=render_approved(accepted,'College characteristics',20,2)
        self.assertNotIn('Instructional expenditure',text)
        self.assertIn('No table-specific semantic claim',text)

    def test_render_preserves_exact_reviewed_claim_without_new_facts(self):
        claims=validate_claims(CANDIDATE,['exp_instr_2000'],CATALOG)['claims']
        text=render_approved(claims,'College characteristics',20,2)
        self.assertEqual(text,'This dataset contains 20 rows and 2 columns.\n\n'+CANDIDATE['claims'][0]['text']+' [p:p1:w0]\n')
        self.assertNotIn('per student',text)

    def test_abstention_is_valid_and_duplicate_verdicts_are_not(self):
        self.assertEqual(validate_claims({'claims':[],'limitations':['Units unresolved']},[],CATALOG)['claims'],[])
        with self.assertRaises(ValueError):validate_audit({'verdicts':[verdict(),verdict()]},[{}])

    def test_retrieval_uses_three_queries_and_expands_same_page_only(self):
        class Index:
            data={'chunks':[dict(paper_id='p',pdf_page=1,chunk_id='p:p1:w0',text='definition'),
                            dict(paper_id='p',pdf_page=1,chunk_id='p:p1:w180',text='continuation'),
                            dict(paper_id='other',pdf_page=1,chunk_id='other:p1:w0',text='unrelated')]}
            def search(self,q,dataset_id,top_k):return [self.data['chunks'][0]]
        hits,queries=retrieve_table_evidence(Index(),{'name':'Table 99 College Characteristics','dataset_id':'example'},['x'])
        self.assertEqual(len(queries),3)
        self.assertTrue(all('Table 99' not in q for q in queries))
        self.assertEqual([h['chunk_id'] for h in hits],['p:p1:w0','p:p1:w180'])

if __name__=='__main__':unittest.main()
