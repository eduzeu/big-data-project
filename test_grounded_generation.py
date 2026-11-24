"""Offline checks for evidence provenance, input parity, and prompt isolation."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pandas as pd
from grounded_generation import validate_facts, validate_description, validate_proposals, generate_json, apply_review, build_excerpt_catalog, render_sentences
from run_grounded import prepare, run

HITS=[{'chunk_id':'paper:p3:w0','title':'Fixture paper','pdf_page':3,'source_url':'https://example.org/paper.pdf','text':'Example measures are reported for counties with income groups.'}]
FACTS={'facts':[{'columns':['cty'],'interpretation':'County identifier',
                 'evidence':[{'chunk_id':'paper:p3:w0','quote':'reported for counties'}]}],
       'unresolved_columns':['x']}

class EvidenceTests(unittest.TestCase):
    def test_exact_quote_and_column_coverage(self):
        self.assertEqual(validate_facts(FACTS,['cty','x'],HITS),FACTS)
        for change in ['fabricated_quote','unknown_id','unknown_column','unaccounted_column','both_unresolved']:
            value=copy.deepcopy(FACTS)
            if change=='fabricated_quote':value['facts'][0]['evidence'][0]['quote']='unsupported invented quotation'
            elif change=='unknown_id':value['facts'][0]['evidence'][0]['chunk_id']='other:p99'
            elif change=='unknown_column':value['facts'][0]['columns']=['invented']
            elif change=='unaccounted_column':value['unresolved_columns']=[]
            else:value['unresolved_columns']=['cty','x']
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_facts(value,['cty','x'],HITS)

    def test_pdf_spacing_can_change_but_words_cannot(self):
        value=copy.deepcopy(FACTS)
        value['facts'][0]['evidence'][0]['quote']='reportedforcounties'
        validate_facts(value,['cty','x'],HITS)
        value['facts'][0]['evidence'][0]['quote']='reportedforcities'
        with self.assertRaises(ValueError):validate_facts(value,['cty','x'],HITS)

    def test_missing_and_fabricated_citations_rejected(self):
        good={'description':'County measures [paper:p3:w0].',
              'paper_claims':[{'text':'County measures [paper:p3:w0].','chunk_ids':['paper:p3:w0']}]}
        validate_description(good,FACTS)
        for bad in [dict(good,description='No citations.'),
                    dict(good,description='County measures [other:p99].'),
                    dict(good,paper_claims=[]),
                    dict(good,paper_claims=[{'text':'Absent statement [paper:p3:w0]','chunk_ids':['paper:p3:w0']}])]:
            with self.assertRaises(ValueError):validate_description(bad,FACTS)

    def test_excerpt_ids_attach_original_source_text(self):
        catalog=build_excerpt_catalog(HITS)
        value={'facts':[{'columns':['cty'],'interpretation':'County identifier','evidence_ids':['E0000']}]}
        result=validate_proposals(value,['cty','x'],HITS,catalog)
        self.assertEqual(result['facts'][0]['evidence'][0]['quote'],HITS[0]['text'])
        value['facts'][0]['evidence_ids']=['E0']
        validate_proposals(value,['cty','x'],HITS,catalog)
        value['facts'][0]['evidence_ids']=['E9999']
        with self.assertRaises(ValueError):validate_proposals(value,['cty','x'],HITS,catalog)

    def test_unmapped_columns_are_computed(self):
        result=validate_proposals({'facts':FACTS['facts']},['cty','x'],HITS)
        self.assertEqual(result['unresolved_columns'],['x'])

    def test_two_rejected_responses_never_create_success(self):
        calls=[]
        def create(**kwargs):
            calls.append(kwargs)
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='{}'))])
        client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            with self.assertRaises(ValueError):
                generate_json(client,'mock','rules',{},lambda v:validate_description(v,FACTS),output,'rejected')
            self.assertEqual(len(calls),2)
            self.assertFalse((output/'rejected.json').exists())
            self.assertTrue((output/'rejected_validation_2.json').exists())

    def test_rejected_interpretations_cannot_enter_description(self):
        review={'verdicts':[{'fact_index':0,'supported':False,'reason':'Quote does not define the field'}]}
        with self.assertRaises(ValueError):apply_review(FACTS,review,['cty','x'])

    def test_citations_are_rendered_from_accepted_facts(self):
        result=render_sentences({'sentences':[{'text':'County measures','fact_ids':['F0']}]},FACTS,2,2)
        self.assertIn('[paper:p3:w0]',result['description'])
        self.assertIn('2 rows and 2 columns',result['description'])
        with self.assertRaises(ValueError):render_sentences({'sentences':[{'text':'Wrong','fact_ids':['F99']}]},FACTS,2,2)

    def test_description_cannot_silently_drop_a_condition(self):
        facts=copy.deepcopy(FACTS)
        facts['facts'].append(copy.deepcopy(facts['facts'][0]))
        with self.assertRaises(ValueError):render_sentences({'sentences':[{'text':'County measures','fact_ids':['F0']}]},facts,2,2)

    def test_empty_reasoning_output_stops_without_another_paid_attempt(self):
        calls=[]
        def create(**kwargs):
            calls.append(kwargs)
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=''),finish_reason='length')])
        client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)
            with self.assertRaises(RuntimeError):generate_json(client,'gpt-5.1','rules',{},lambda v:v,output,'empty')
            self.assertEqual(len(calls),1)
            self.assertNotIn('temperature',calls[0])
            self.assertEqual(calls[0]['reasoning_effort'],'medium')
            self.assertEqual(json.loads((output/'empty_provider_1.json').read_text())['finish_reason'],'length')

    def setup_inputs(self,tmp):
        csv=tmp/'health_ineq_online_table_11.csv'
        frame=pd.DataFrame({'cty':[1,2],'x':[10,20]});frame.to_csv(csv,index=False)
        base=tmp/'baseline';base.mkdir()
        (base/'sample.csv').write_text(frame.sample(n=2,random_state=42).reset_index(drop=True).to_csv(index=False))
        (base/'semantic_profile.md').write_text('Unverified guess: city quarters')
        (base/'content_profile.md').write_text('2 rows; 2 columns')
        (base/'generation.json').write_text(json.dumps({'status':'baseline_generated',
          'csv_sha256':hashlib.sha256(csv.read_bytes()).hexdigest(),'rows':2,'columns':['cty','x'],
          'sample_rows':2,'seed':42,'model':'mock-model'}))
        return csv,base

    def fake_index(self):
        obj=SimpleNamespace(data={'datasets':[{'dataset_id':'life_county_expectancy',
            'name':'County measures','csv_filename':'health_ineq_online_table_11.csv'}]},
            search=lambda *a:HITS)
        return obj

    def test_baseline_parity_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp);csv,base=self.setup_inputs(tmp);out=tmp/'new'
            with patch('run_grounded.PaperIndex',return_value=self.fake_index()):
                payload,hits,info=prepare(csv,'life_county_expectancy',base,out,'measures')
                self.assertEqual((base/'sample.csv').read_bytes(),(out/'sample.csv').read_bytes())
                self.assertFalse(info['used_readme_context'])
                with self.assertRaises(ValueError): prepare(csv,'life_county_expectancy',base,out,'measures')
                csv.write_text('cty,x\n3,30\n')
                with self.assertRaises(ValueError):prepare(csv,'life_county_expectancy',base,tmp/'other','measures')

    def test_full_adapter_hides_guesses_and_repairs_invalid_json_once(self):
        messages=[]
        valid=[{'columns':['cty'],'interpretation':'County identifier','evidence_ids':['E0000']}]
        bad=copy.deepcopy(valid);bad[0]['evidence_ids']=['invented']
        replies=[{'facts':bad},{'facts':valid},
                 {'verdicts':[{'fact_index':0,'supported':True,'reason':'Direct evidence'}]},
                 {'sentences':[{'text':'County measures','fact_ids':['F0']}]}]
        def create(**kwargs):
            messages.append(copy.deepcopy(kwargs['messages']))
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(replies.pop(0))))])
        client=SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp);csv,base=self.setup_inputs(tmp);out=tmp/'new'
            with patch('run_grounded.PaperIndex',return_value=self.fake_index()):
                payload,hits,info=prepare(csv,'life_county_expectancy',base,out,'measures')
            result=run(client,payload,hits,info,out)
            self.assertEqual(info['llm_calls'],4)
            self.assertNotIn('Unverified guess',messages[0][1]['content'])
            self.assertNotIn('Unverified guess',messages[-1][1]['content'])
            self.assertNotIn('city quarters',messages[-1][1]['content'])
            self.assertNotIn('content_profile',messages[-1][1]['content'])
            self.assertNotIn('column_names',messages[-1][1]['content'])
            self.assertIn('County identifier',messages[-1][1]['content'])
            self.assertTrue((out/'reconciled_semantics_validation_1.json').exists())
            self.assertEqual(json.loads((out/'generation.json').read_text())['status'],'paper_reconciled_generated')

if __name__=='__main__':unittest.main()
