"""Evaluation-integrity checks; no API calls."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from evaluate_outputs import count_labels,verify_pair,validate_annotations,ROOT

class EvaluationTests(unittest.TestCase):
    def test_abstention_cannot_get_semantic_credit(self):
        checks=[{'judgments':{'paper':{'label':'supported'}}}]
        with self.assertRaises(ValueError):count_labels(checks,'paper','abstained')
        checks[0]['judgments']['paper']['label']='abstained'
        self.assertEqual(count_labels(checks,'paper','abstained'),{'abstained':1})
        with self.assertRaises(ValueError):count_labels(checks,'paper','generated')

    def make_pair(self,root):
        base=root/'base';other=root/'other';base.mkdir();other.mkdir()
        info={'csv_sha256':'same','rows':2,'columns':['x'],'status':'generated',
              'used_readme_context':False,'used_stata_context':False}
        for folder in [base,other]:
            (folder/'generation.json').write_text(json.dumps(info))
            for name in ['sample.csv','content_profile.md','semantic_profile.md']:(folder/name).write_text('same')
        return base,other

    def test_changed_sample_cannot_be_compared_as_matched(self):
        with tempfile.TemporaryDirectory() as tmp:
            base,other=self.make_pair(Path(tmp));(other/'sample.csv').write_text('changed')
            with self.assertRaises(ValueError):verify_pair(base,other,'strict_paper_only')

    def test_documented_run_cannot_be_mislabeled_paper_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            base,other=self.make_pair(Path(tmp));info=json.loads((other/'generation.json').read_text())
            info['used_readme_context']=True;(other/'generation.json').write_text(json.dumps(info))
            with self.assertRaises(ValueError):verify_pair(base,other,'strict_paper_only')
            verify_pair(base,other,'documentation_assisted')

    def test_incomplete_annotation_cannot_publish(self):
        rubric=json.loads((ROOT/'evaluation/rubric.json').read_text())
        annotations=json.loads((ROOT/'evaluation/annotations.json').read_text())
        validate_annotations(rubric,annotations)
        bad=copy.deepcopy(annotations)
        first=next(iter(bad['datasets'].values()))[0]
        first['judgments']['csv_baseline']['rationale']='PENDING review'
        with self.assertRaises(ValueError):validate_annotations(rubric,bad)
        bad=copy.deepcopy(annotations);next(iter(bad['datasets'].values())).pop()
        with self.assertRaises(ValueError):validate_annotations(rubric,bad)

if __name__=='__main__':unittest.main()
