"""Blinding/pending status are enforced without assigning actual relevance labels."""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from repository_integrity import research_baseline

sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
import prepare_judgment_pool as pool


class JudgmentPoolTests(unittest.TestCase):
    def fixture(self):
        queries={f'q{i}':{'text':f'Question {i}?','style':s} for i,s in enumerate(['lexical_oriented']*6+['semantic_paraphrase']*6+['mixed_natural']*6)}
        rows={f'c{i}':{'text':f'Chunk {i}. Direct content.','document_id':'doc'} for i in range(5)}
        pairs={(q,c):[] for q in queries for c in rows}
        return queries,rows,pairs

    def test_deterministic_shuffle_and_pilot_strata(self):
        q,r,pairs=self.fixture()
        a=pool.blind_ledger(pairs,q,r,'snapshot','fingerprint')
        b=pool.blind_ledger(dict(reversed(list(pairs.items()))),q,r,'snapshot','fingerprint')
        self.assertEqual(a,b)
        self.assertNotEqual([x['assessment_id'] for x in a],sorted(x['assessment_id'] for x in a))
        pilot=pool.select_pilot(a,q)
        self.assertEqual(len(pilot),30)
        self.assertEqual({x['query_id'] for x in pilot},set(q))
        self.assertEqual(set(Counter(q[x['query_id']]['style'] for x in pilot).values()),{10})

    def test_exact_bindings_and_pending_not_grade_zero(self):
        q,r,pairs=self.fixture()
        for x in pool.blind_ledger(pairs,q,r,'snapshot','fingerprint'):
            pool.validate_assessment(x)
            self.assertIsNone(x['relevance_grade'])
            self.assertEqual(x['serialized_chunk_text'],r[x['chunk_id']]['text'])
            self.assertEqual(x['query_text'],q[x['query_id']]['text'])

    def test_hidden_fields_are_rejected(self):
        q,r,pairs=self.fixture(); x=pool.blind_ledger(pairs,q,r,'snapshot','fingerprint')[0]
        for field in ('method','rank','score','existing_grade','preferred_method','query_style'):
            bad={**x,field:'leak'}
            with self.assertRaises(ValueError):pool.validate_assessment(bad)

    def test_tampered_text_is_rejected(self):
        q,r,pairs=self.fixture(); x=pool.blind_ledger(pairs,q,r,'snapshot','fingerprint')[0]
        x['query_text']='Changed'
        with self.assertRaises(ValueError):pool.validate_assessment(x)

    def test_grade_schema_and_unresolved_preservation(self):
        q,r,pairs=self.fixture(); x=pool.blind_ledger(pairs,q,r,'snapshot','fingerprint')[0]
        x.update(assessment_status='ASSESSED',relevance_grade=1,rationale='Synthetic test rationale',
            ambiguity_flag=False,uncertainty_notes='Synthetic fixture, not an actual judgment',evidence=['Direct content.'],
            assessor_provenance={'label':'AI SILVER — PROVISIONAL','human_validated':False,'model_id':'synthetic',
                'model_revision':'synthetic','assessed_at':'synthetic','rubric_version':'synthetic','session_id':'synthetic'})
        pool.validate_assessment(x)
        for bad_grade in (None,True,3,-1,'1'):
            with self.assertRaises(ValueError):pool.validate_assessment({**x,'relevance_grade':bad_grade})
        unresolved={**x,'assessment_status':'UNRESOLVED','relevance_grade':None,'ambiguity_flag':True,'evidence':[]}
        pool.validate_assessment(unresolved)
        with self.assertRaises(ValueError):pool.validate_assessment({**unresolved,'relevance_grade':0})
        with self.assertRaises(ValueError):pool.validate_assessment({**x,'evidence':['invented quote']})
        with self.assertRaises(ValueError):pool.validate_assessment({**x,'assessor_provenance':None})

    def test_dedup_sources_and_duplicate_rejection(self):
        runs=[{'query_id':'q','method':m,'results':[{'chunk_id':'a','rank':1,'score':.5}]} for m in ('R1','R2','R3','R4')]
        p=pool.build_pool(runs)
        self.assertEqual(len(p),1)
        self.assertEqual(len(p['q','a']),4)
        self.assertEqual(p,pool.build_pool(list(reversed(runs))))
        with self.assertRaises(ValueError):pool.build_pool(runs+[runs[0]])
        bad=deepcopy(runs);bad[0]['results']*=2
        with self.assertRaises(ValueError):pool.build_pool(bad)


class PublishedPoolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not pool.OUTPUT.exists():raise unittest.SkipTest('Pool not yet published')
        cls.ledger=pool.read_jsonl(pool.OUTPUT/'blind_assessment_ledger.jsonl')
        cls.origin=pool.read_jsonl(pool.OUTPUT/'pool_origin_audit.jsonl')

    def test_pool_exact_pair_bindings(self):
        runs=pool.read_jsonl(pool.PREVIOUS/'rankings.jsonl')
        p=pool.build_pool(runs)
        self.assertEqual(len(p),654)
        self.assertEqual({(r['query_id'],r['chunk_id']) for r in self.ledger},set(p))
        self.assertEqual(len({r['assessment_id'] for r in self.ledger}),654)
        for r in self.ledger:pool.validate_assessment(r)
        self.assertEqual(sum(r['existing_grade'] is not None for r in self.origin),90)
        self.assertEqual(sum(r['existing_grade'] is None for r in self.origin),564)
        queries={r['query_id']:r for r in pool.read_jsonl(pool.ROOT/'data/benchmark/development_queries_draft.jsonl')}
        rows={r['chunk_id']:r for r in json.loads((pool.ROOT/'experiments/indexes/v2_ai_corrected/R2/documents.json').read_text(encoding='utf8'))}
        for r in self.ledger:
            self.assertEqual(r['query_text'],queries[r['query_id']]['text'])
            self.assertEqual(r['serialized_chunk_text'],rows[r['chunk_id']]['text'])
            self.assertEqual(r['source_snapshot_fingerprint'],pool.full_colab.FINGERPRINT)
            self.assertEqual(r['document_id'],rows[r['chunk_id']]['document_id'])
        pilot=pool.read_jsonl(pool.OUTPUT/'blind_pilot_30.jsonl')
        self.assertEqual(pilot,pool.select_pilot(self.ledger,queries))
        self.assertEqual(len(pilot),30)

    def test_previous_outputs_and_protected_artifacts(self):
        integrity=json.loads((pool.OUTPUT/'protected_integrity.json').read_text(encoding='utf8'))
        scoped=research_baseline(pool.ROOT,integrity['hashes'])
        self.assertEqual(pool.verify_baseline(scoped['hashes'])['status'],'PASS')
        self.assertEqual(len(scoped['hashes'])+len(scoped['excluded']),len(integrity['hashes']))
        m=json.loads((pool.PREVIOUS/'run_manifest.json').read_text(encoding='utf8'))
        for name,h in m['outputs'].items():self.assertEqual(pool.full_colab.file_hash(pool.PREVIOUS/name),h)
        qrels=pool.read_jsonl(pool.ROOT/'data/versions/v2_ai_corrected/benchmark/development_qrels_ai_silver_v2.jsonl')
        self.assertEqual(Counter(x['grade'] for x in qrels),{0:621,1:32,2:31})


if __name__=='__main__':
    unittest.main()
