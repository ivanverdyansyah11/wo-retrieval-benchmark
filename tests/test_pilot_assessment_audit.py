"""Offline audit/alias/comparison fixtures; never generate actual second judgments."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from repository_integrity import research_baseline

spec=importlib.util.spec_from_file_location('pilot_audit',Path(__file__).parents[1]/'scripts/audit_pilot_assessments.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)


class PilotAssessmentAuditTests(unittest.TestCase):
    def fixtures(self):
        inputs=[{'assessment_id':f'a{i}','query_id':f'q{i}','chunk_id':f'c{i}',
                 'query_text':'Synthetic question','serialized_chunk_text':'Synthetic chunk evidence.',
                 'query_text_sha256':audit.text_hash('Synthetic question'),
                 'serialized_text_sha256':audit.text_hash('Synthetic chunk evidence.'),
                 'source_snapshot_id':'synthetic','source_snapshot_fingerprint':'synthetic'} for i in range(2)]
        results=[{'assessment_id':r['assessment_id'],'query_id':r['query_id'],'chunk_id':r['chunk_id'],
                 'grade':i*2,'status':'RESOLVED','evidence':'chunk evidence.','rationale':'Synthetic fixture only',
                 'uncertainty_reason':None} for i,r in enumerate(inputs)]
        return inputs,results

    def test_schema_ids_and_evidence_validation(self):
        inputs,results=self.fixtures();audit.validate_records(results,inputs)
        for bad in (results[:1],results+[results[0]],[results[0],results[0]]):
            with self.assertRaises(ValueError):audit.validate_records(bad,inputs)
        for change in ({'query_id':'bad'},{'grade':True},{'grade':3},{'status':'PENDING'},
                       {'evidence':'invented'},{'evidence':None},{'rationale':''}):
            bad=deepcopy(results);bad[0].update(change)
            with self.assertRaises(ValueError):audit.validate_records(bad,inputs)

    def test_unresolved_never_zero(self):
        inputs,results=self.fixtures()
        results[0].update(status='UNRESOLVED',grade=None,evidence=None,uncertainty_reason='Missing context')
        audit.validate_records(results,inputs)
        results[0]['grade']=0
        with self.assertRaises(ValueError):audit.validate_records(results,inputs)

    def test_alias_roundtrip_and_determinism(self):
        inputs,_=self.fixtures();styles={'q0':'lexical','q1':'mixed'}
        second,mapping=audit.second_package(inputs,styles)
        self.assertEqual((second,mapping),audit.second_package(list(reversed(inputs)),styles))
        by={x['assessment_alias']:x for x in mapping}
        original={x['assessment_id']:x for x in inputs}
        for r in second:
            old=original[by[r['assessment_id']]['original_assessment_id']]
            self.assertEqual(r['query_text'],old['query_text'])
            self.assertEqual(r['serialized_chunk_text'],old['serialized_chunk_text'])
            self.assertEqual(set(r),{'assessment_id','query_id','chunk_id','query_text','serialized_chunk_text','query_text_sha256','serialized_text_sha256'})

    def test_confusion_distance_and_common_resolved_denominator(self):
        rows=[{'left_grade':0,'right_grade':0},{'left_grade':1,'right_grade':2},
              {'left_grade':None,'right_grade':0},{'left_grade':2,'right_grade':None},
              {'left_grade':None,'right_grade':None}]
        r=audit.compare(rows)
        self.assertEqual(r['pairs'],5);self.assertEqual(r['common_resolved'],2)
        self.assertEqual(r['exact_grade_agreement_count'],1)
        self.assertEqual(r['grade_distance'],{'0':1,'1':1})
        self.assertEqual(r['unresolved_on_one_side'],2)
        self.assertEqual(r['both_unresolved'],1)
        self.assertEqual(r['grade_1_vs_2'],1)

    def test_hand_calculated_linear_kappa(self):
        same=[{'left_grade':g,'right_grade':g} for g in (0,2)]
        opposite=[{'left_grade':g,'right_grade':2-g} for g in (0,2)]
        self.assertEqual(audit.compare(same)['linear_weighted_cohens_kappa'],1)
        self.assertEqual(audit.compare(opposite)['linear_weighted_cohens_kappa'],-1)
        self.assertIsNone(audit.compare([{'left_grade':0,'right_grade':0}]*2)['linear_weighted_cohens_kappa'])
        self.assertIsNone(audit.compare([])['exact_grade_agreement_fraction'])

    def test_comparison_cli_synthetic_only(self):
        inputs,first=self.fixtures();styles={'q0':'lexical','q1':'mixed'}
        second,mapping=audit.second_package(inputs,styles)
        second_results=[]
        for r in second:
            second_results.append({'assessment_id':r['assessment_id'],'query_id':r['query_id'],'chunk_id':r['chunk_id'],
                'grade':0,'status':'RESOLVED','evidence':'chunk evidence.','rationale':'SYNTHETIC TEST ONLY','uncertainty_reason':None})
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);package=root/'package';package.mkdir()
            (package/'pilot_second_input.jsonl').write_text(audit.jsonl_text(second),encoding='utf8')
            (package/'alias_mapping_private.jsonl').write_text(audit.jsonl_text(mapping),encoding='utf8')
            audit.write_json(package/'manifest.json',{'outputs':{p.name:audit.file_hash(p) for p in package.iterdir()}})
            source=root/'second-SYNTHETIC.jsonl';source.write_text(audit.jsonl_text(second_results),encoding='utf8')
            with patch.object(audit,'OUTPUT',package),patch.object(audit,'preflight',return_value=(inputs,first,{},{})),patch.object(audit,'file_hash',return_value='synthetic'):
                # Real checksums are exercised separately; fixture execution tests reconciliation only.
                m=json.loads((package/'manifest.json').read_text());m['outputs']={k:'synthetic' for k in m['outputs']}
                audit.write_json(package/'manifest.json',m)
                audit.compare_second(source,root/'comparison')
                r=json.loads((root/'comparison/comparison.json').read_text())
                self.assertEqual(r['overall']['common_resolved'],2)
                self.assertEqual(len(audit.jsonl(root/'comparison/adjudication_candidates.jsonl')),1)
                with self.assertRaises(ValueError):audit.compare_second(source,root/'comparison')


class PublishedAuditTests(unittest.TestCase):
    def test_actual_preflight_and_flags(self):
        historical=json.loads((audit.OUTPUT/'protected_integrity.json').read_text(encoding='utf8'))['hashes']
        scoped=research_baseline(audit.ROOT,historical)
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)
            (target/'protected_integrity.json').write_text(json.dumps({'hashes':scoped['hashes']}),encoding='utf8')
            with patch.object(audit,'OUTPUT',target):
                pilot,first,_,baseline=audit.preflight()
        self.assertEqual(len(pilot),30);self.assertEqual(len(first),30)
        flagged={x['assessment_id']:x for x in first}
        self.assertIsNone(flagged['WO-POOL-V2-0107']['grade'])
        for k in ('WO-POOL-V2-0438','WO-POOL-V2-0526','WO-POOL-V2-0163'):self.assertEqual(flagged[k]['grade'],1)
        self.assertGreaterEqual(len(historical),728)
        self.assertEqual(baseline,scoped['hashes'])
        self.assertEqual(len(baseline)+len(scoped['excluded']),len(historical))

    def test_package_allowlist_and_exact_text(self):
        pilot=audit.jsonl(audit.SOURCE/'blind_pilot_30.jsonl')
        queries=audit.jsonl(audit.ROOT/'data/benchmark/development_queries_draft.jsonl')
        expected,mapping=audit.second_package(pilot,{r['query_id']:r['style'] for r in queries})
        actual=audit.jsonl(audit.OUTPUT/'pilot_second_input.jsonl')
        self.assertEqual(actual,expected)
        self.assertEqual(audit.jsonl(audit.OUTPUT/'alias_mapping_private.jsonl'),mapping)
        self.assertNotEqual([x['query_text'] for x in actual],[x['query_text'] for x in pilot])
        with zipfile.ZipFile(audit.OUTPUT/'second_assessor_package.zip') as z:
            self.assertIsNone(z.testzip())
            self.assertEqual(set(z.namelist()),{'pilot_second_input.jsonl','second_assessor_prompt.md'})
            self.assertIn((audit.SOURCE/'rubric_workflow.md').read_bytes(),z.read('second_assessor_prompt.md'))
        for r in actual:
            self.assertFalse({'grade','rationale','method','rank','score','previously_judged','query_style'}&set(r))


if __name__=='__main__':unittest.main()
