"""Coverage accounting is independent of relevance unknown outside the pool."""
import importlib.util
import csv
import json
from pathlib import Path
import unittest
from repository_integrity import research_baseline

from wo_retrieval.retrieval.lexical import RetrievalResult
from wo_retrieval.hybrid.retrieval import fuse

spec = importlib.util.spec_from_file_location('pilot', Path(__file__).parents[1]/'scripts/run_development_pilot.py')
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


def result(method, chunk, rank, score):
    return RetrievalResult(method, chunk, 'doc', rank, score, 'snapshot')


class DevelopmentPilotTests(unittest.TestCase):
    def test_unknown_is_not_zero(self):
        ranking = [result('R1', str(i), i+1, 4-i) for i in range(4)]
        labels = {('q','0'):0, ('q','1'):1, ('q','2'):2}
        c = pilot.coverage(ranking,labels,'q',5)
        self.assertEqual([c[k] for k in ('grade_0','grade_1','grade_2','unjudged','missing_slots')],[1,1,1,1,1])
        self.assertEqual(c['judged_pct'],75)
        self.assertEqual(c['judged_pct_requested'],60)
        self.assertTrue(c['query_has_judged_relevant'])
        self.assertFalse(c['complete_returned_window'])

    def test_empty_window_denominator(self):
        c = pilot.coverage([],{},'q',10)
        self.assertIsNone(c['judged_pct'])
        self.assertIsNone(c['unjudged_pct'])
        self.assertEqual(c['unjudged'],0)
        self.assertEqual(c['missing_slots'],10)
        self.assertFalse(c['complete_returned_window'])

    def test_macro_and_micro_differ(self):
        rows = []
        for q, ranking in [('a',[result('R1','a',1,1)]),('b',[result('R1','b',1,2),result('R1','c',2,1)])]:
            rows.append(dict(method='R1',**pilot.coverage(ranking,{('a','a'):0},q,3)))
        s=pilot.summarize(rows,'style','lexical')
        self.assertAlmostEqual(s['judged_pct'],100/3)
        self.assertEqual(s['macro_judged_pct'],50)

    def test_rank_validation_rejects_bad_data(self):
        valid=[result('R1','a',1,1)]
        pilot.validate_ranking(valid,'R1',{'a':'doc'},'snapshot')
        for bad in ([valid[0],valid[0]],[result('R1','a',1,float('nan'))],
                    [result('R1','a',2,1)],[result('R1','unknown',1,1)],
                    [result('R1','a',1,0)]):
            with self.assertRaises(ValueError):
                pilot.validate_ranking(bad,'R1',{'a':'doc'},'snapshot')
        with self.assertRaises(ValueError):
            pilot.validate_ranking([], 'R3', {'a':'doc'}, 'snapshot')

    def test_independent_rrf_absent_and_positive(self):
        rows=[{'chunk_id':c,'document_id':'doc'} for c in ('a','b')]
        bm=[result('R2','b',1,2)]
        dense=[result('R3','a',1,.9),result('R3','b',2,.8)]
        hybrid,detail=fuse(bm,dense,rows,'snapshot',2)
        pilot.verify_rrf(bm,dense,hybrid,detail)
        self.assertEqual(hybrid[0].chunk_id,'b')
        self.assertEqual(hybrid[0].score,1/61+1/62)
        self.assertEqual(hybrid[1].score,1/61)


class PublishedPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output=pilot.OUTPUT
        if not cls.output.exists():
            raise unittest.SkipTest('Pilot artifacts not yet created')
        cls.manifest=json.loads((cls.output/'run_manifest.json').read_text(encoding='utf8'))
        cls.rankings=pilot.read_jsonl(cls.output/'rankings.jsonl')

    def test_outputs_and_version_isolation(self):
        self.assertEqual(self.manifest['completion_status'],'COMPLETE')
        self.assertEqual(self.manifest['snapshot']['id'],pilot.full_colab.SNAPSHOT)
        self.assertEqual(self.manifest['snapshot']['aggregate_fingerprint'],pilot.full_colab.FINGERPRINT)
        for name,digest in self.manifest['outputs'].items():
            self.assertEqual(pilot.full_colab.file_hash(self.output/name),digest)
        integrity=json.loads((self.output/'protected_integrity.json').read_text(encoding='utf8'))
        scoped=research_baseline(pilot.ROOT,integrity['hashes'])
        self.assertEqual(pilot.verify_baseline(scoped['hashes'])['status'],'PASS')
        self.assertEqual(len(scoped['hashes'])+len(scoped['excluded']),len(integrity['hashes']))

    def test_shared_input_and_cached_rrf(self):
        self.assertEqual(len(self.rankings),72)
        queries=pilot.read_jsonl(pilot.ROOT/'data/benchmark/development_queries_draft.jsonl')
        for q in queries:
            runs=[r for r in self.rankings if r['query_id']==q['query_id']]
            self.assertEqual({r['method'] for r in runs},{'R1','R2','R3','R4'})
            for r in runs:
                self.assertEqual(r['query_text'],q['text'])
                self.assertEqual(r['query_text_sha256'],pilot.text_hash(q['text']))
            by={r['method']:r for r in runs}
            components={m:[RetrievalResult(**{k:v for k,v in r.items() if k in
                ('method_id','chunk_id','document_id','rank','score','snapshot_id')}) for r in by[m]['results']]
                for m in by}
            universe={r.chunk_id:r.document_id for r in components['R3']}
            for m in components:
                pilot.validate_ranking(components[m],m,universe,pilot.full_colab.SNAPSHOT)
            pilot.verify_rrf(components['R2'],components['R3'],components['R4'],by['R4']['rrf_breakdown'])

    def test_coverage_independent_accounting(self):
        with (self.output/'coverage.csv').open(encoding='utf-8-sig') as f:
            audits=list(csv.DictReader(f))
        self.assertEqual(len(audits),360)
        for a in audits:
            run=next(r for r in self.rankings if (r['query_id'],r['method'])==(a['query_id'],a['method']))
            grades=[r['silver_grade'] for r in run['results'][:int(a['top_k'])]]
            for grade in (0,1,2):
                self.assertEqual(int(a[f'grade_{grade}']),grades.count(grade))
            self.assertEqual(int(a['unjudged']),grades.count(None))
            self.assertEqual(int(a['judged'])+int(a['unjudged']),len(grades))


if __name__ == '__main__':
    unittest.main()
