from copy import deepcopy
from dataclasses import asdict, replace
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from wo_retrieval.hybrid.retrieval import HybridRetriever, fuse, ready, validate_policy
from wo_retrieval.retrieval.lexical import RetrievalResult, digest, file_hash, read_protocol


ROOT = Path(__file__).resolve().parents[1]
CONFIG = read_protocol(ROOT)
ROWS = [{'chunk_id': c, 'document_id': 'D' + c, 'text_sha256': digest(c)} for c in 'ABC']


def ranking(method, pairs):
    return [RetrievalResult(method, c, 'D' + c, i, score, 'S') for i, (c, score) in enumerate(pairs, 1)]


class Stub:
    def __init__(self, method, results):
        self.method, self.results, self.rows, self.snapshot_id = method, results, deepcopy(ROWS), 'S'
        self.calls = []

    def retrieve(self, query, top_k):
        self.calls.append((query, top_k))
        return self.results[:top_k]


def fixture():
    config = deepcopy(CONFIG)
    config['snapshot'].update(id='S', manifest_sha256='sha', aggregate_fingerprint='fp', chunks=3)
    config['R4']['dense_candidate_depth'] = 3
    bm = Stub('R2', ranking('R2', [('B', 9), ('A', 2)]))
    dense = Stub('R3', ranking('R3', [('A', .9), ('C', .2), ('B', -.1)]))
    common = {'snapshot_id': 'S', 'snapshot_sha256': 'sha', 'snapshot_fingerprint': 'fp',
              'protocol_sha256': 'p', 'serializer_version': 's', 'serialization_policy_hash': 'h'}
    stats = {'serialized_inputs_hash': 'texts', 'universe_hash': 'ids'}
    bm.manifest = {**common, 'completion_status': 'COMPLETE', 'serialization_statistics': stats}
    manifest = {'completion_status': 'COMPLETE', 'identity': {**common, **stats}}
    return bm, dense, manifest, config


class FusionTests(unittest.TestCase):
    def test_formula_different_rankings_dense_only_negative_cosine(self):
        bm, dense, _, _ = fixture()
        results, diagnostics = fuse(bm.results, dense.results, ROWS, 'S', 99)
        self.assertEqual([r.chunk_id for r in results], ['A', 'B', 'C'])
        self.assertEqual([r.rank for r in results], [1, 2, 3])
        self.assertEqual(results[0].score, 1/62 + 1/61)
        self.assertEqual(results[1].score, 1/61 + 1/63)
        self.assertEqual(results[2].score, 1/62)
        self.assertIsNone(diagnostics[2]['bm25_rank'])
        self.assertEqual(diagnostics[2]['bm25_contribution'], 0)
        self.assertEqual(len({r.chunk_id for r in results}), 3)
        self.assertEqual(set(asdict(results[0])), {'method_id','chunk_id','document_id','rank','score','snapshot_id'})

    def test_zero_negative_bm25_excluded_no_pseudo_rank(self):
        dense = ranking('R3', [('A', 1), ('B', 0), ('C', -1)])
        bm = ranking('R2', [('B', 10), ('A', 0), ('C', -4)])
        results, diagnostics = fuse(bm, dense, ROWS, 'S', 3)
        by_id = {r['chunk_id']: r for r in diagnostics}
        self.assertEqual(by_id['B']['bm25_rank'], 1)
        for c in 'AC':
            self.assertIsNone(by_id[c]['bm25_rank'])
            self.assertEqual(by_id[c]['bm25_contribution'], 0)
        empty, _ = fuse([], dense, ROWS, 'S', 3)
        self.assertEqual([r.chunk_id for r in empty], ['A','B','C'])
        self.assertEqual([r.score for r in empty], [1/61,1/62,1/63])

    def test_ties_id_order_and_no_iteration_order_dependency(self):
        bm = ranking('R2', [('B', 4), ('A', 3)])
        dense = ranking('R3', [('A', .8), ('B', .7), ('C', .1)])
        a = fuse(bm, dense, ROWS, 'S', 3)
        b = fuse(bm, dense, list(reversed(ROWS)), 'S', 3)
        self.assertEqual(a, b)
        self.assertEqual(a[0][0].score, a[0][1].score)
        self.assertEqual([r.chunk_id for r in a[0]][:2], ['A','B'])

    def test_topk_invalid(self):
        bm,dense,_,_=fixture()
        self.assertEqual(len(fuse(bm.results,dense.results,ROWS,'S',1)[0]),1)
        for bad in [0,-1,True,1.5,'3',None]:
            with self.assertRaises(ValueError):
                fuse(bm.results,dense.results,ROWS,'S',bad)

    def test_missing_duplicate_nonfinite_bad_rank_metadata_order(self):
        bm,dense,_,_=fixture()
        bad_cases = [dense.results[:-1], dense.results + [dense.results[0]],
                     [replace(dense.results[0],score=float('nan'))]+dense.results[1:],
                     [replace(dense.results[0],rank=0)]+dense.results[1:],
                     [replace(dense.results[0],snapshot_id='OTHER')]+dense.results[1:],
                     [replace(dense.results[0],document_id='wrong')]+dense.results[1:],
                     [replace(dense.results[0],method_id='R2')]+dense.results[1:],
                     ranking('R3',[('C',.2),('A',.9),('B',-.1)])]
        for bad in bad_cases:
            with self.assertRaises(ValueError):
                fuse(bm.results,bad,ROWS,'S',5)
        with self.assertRaises(ValueError):
            fuse(bm.results,dense.results,ROWS+ROWS[:1],'S',5)

    def test_dense_full_371_no_top100_cutoff(self):
        rows=[{'chunk_id':f'C{i:03}', 'document_id':f'DC{i:03}'} for i in range(371)]
        dense=ranking('R3',[(r['chunk_id'],float(371-i)) for i,r in enumerate(rows)])
        bm=ranking('R2',[('C370',1)])
        results,diag=fuse(bm,dense,rows,'S',371)
        self.assertEqual(len(results),371)
        self.assertEqual(next(d for d in diag if d['chunk_id']=='C370')['dense_rank'],371)


class HybridTests(unittest.TestCase):
    def test_same_query_full_depth_and_common_interface(self):
        bm,dense,manifest,config=fixture()
        h=HybridRetriever(bm,dense,manifest,config)
        results=h.retrieve('  koordinasi\r\nvendor  ',2)
        self.assertEqual(bm.calls,[('koordinasi\nvendor',3)])
        self.assertEqual(bm.calls,dense.calls)
        self.assertEqual(len(results),2)
        self.assertTrue(all(r.method_id=='R4' for r in results))

    def test_empty_invalid_no_component_calls(self):
        bm,dense,manifest,config=fixture()
        h=HybridRetriever(bm,dense,manifest,config)
        self.assertEqual(h.retrieve(' \n ',5),[])
        for value in [0,-1,True,1.2]:
            with self.assertRaises(ValueError): h.retrieve('WO',value)
        for value in [None,[],42]:
            with self.assertRaises((ValueError,TypeError)): h.retrieve(value,5)
        self.assertEqual(bm.calls+dense.calls,[])

    def test_fingerprint_inputs_universe_incomplete_rejection(self):
        for key in ['snapshot_id','snapshot_sha256','snapshot_fingerprint','protocol_sha256',
                    'serializer_version','serialization_policy_hash','serialized_inputs_hash','universe_hash']:
            bm,dense,manifest,config=fixture()
            manifest['identity'][key]='bad'
            with self.assertRaises(ValueError): HybridRetriever(bm,dense,manifest,config)
        for method in ['R2','R3']:
            bm,dense,manifest,config=fixture()
            (bm.manifest if method=='R2' else manifest)['completion_status']='INCOMPLETE'
            with self.assertRaises(ValueError): HybridRetriever(bm,dense,manifest,config)
        bm,dense,manifest,config=fixture()
        dense.rows[0]['text_sha256']='bad'
        with self.assertRaises(ValueError): HybridRetriever(bm,dense,manifest,config)

    def test_policy_conflict_rejected(self):
        for key,value in [('rank_constant',61),('weights',[2,1]),('retrieval_candidate_truncation',True),
                          ('dense_candidate_depth',100),('zero_score_tail_filling',True)]:
            config=deepcopy(CONFIG); config['R4'][key]=value
            with self.assertRaises(ValueError): validate_policy(config)

    def test_existing_corruption_loader_error_propagates_no_build(self):
        with patch('wo_retrieval.hybrid.retrieval.load',side_effect=ValueError('Derived artifact hash mismatch')):
            with self.assertRaisesRegex(ValueError,'hash mismatch'): ready(ROOT)

    def test_existing_dense_incomplete_error_propagates_no_build(self):
        bm,_,_,_=fixture()
        with patch('wo_retrieval.hybrid.retrieval.load',return_value=bm), \
             patch('wo_retrieval.dense.model.model_files',return_value=(ROOT,{})), \
             patch('wo_retrieval.dense.model.BGEEncoder'), \
             patch('wo_retrieval.dense.index.token_audit',return_value=([],{})), \
             patch('wo_retrieval.dense.index.cache_identity',return_value={}), \
             patch('wo_retrieval.dense.index.cache_paths',return_value=(ROOT,ROOT)), \
             patch('wo_retrieval.dense.index.load_vectors',side_effect=ValueError('Incomplete/incompatible R3 index')):
            with self.assertRaisesRegex(ValueError,'Incomplete'): ready(ROOT)

    def test_cli_resource_stop_prevents_loading_no_retry(self):
        from wo_retrieval.hybrid.cli import run
        from unittest.mock import MagicMock
        with tempfile.TemporaryDirectory() as folder:
            config=deepcopy(CONFIG)
            config['R3']['cache']['root']=folder
            encoder=MagicMock(model=None,lock=None)
            monitor=MagicMock(); monitor.summary={}
            monitor.__enter__.return_value=monitor
            with patch('wo_retrieval.hybrid.cli.read_protocol',return_value=config), \
                 patch('wo_retrieval.hybrid.cli.ready',return_value=(None,encoder,{})), \
                 patch('wo_retrieval.hybrid.cli.Monitor',return_value=monitor), \
                 patch('wo_retrieval.hybrid.cli.resource',return_value={}), \
                 patch('wo_retrieval.hybrid.cli.gpu_resource',return_value={}), \
                 patch('wo_retrieval.hybrid.cli.gate',side_effect=RuntimeError('resource gate')):
                with self.assertRaisesRegex(RuntimeError,'resource gate'):
                    run(ROOT,'retrieve','WO')
            encoder.load.assert_not_called()
            encoder.encode.assert_not_called()
            encoder.close.assert_not_called()
            report=json.loads(next(Path(folder).rglob('run.json')).read_text())
            self.assertEqual(report['loading'],'NOT RUN')
            self.assertEqual(report['status'],'STOPPED')

    def test_cli_parser_and_empty_query(self):
        from wo_retrieval.hybrid.cli import main, run
        with patch('sys.argv',['wo-hybrid','retrieve']):
            with self.assertRaises(SystemExit) as ctx: main()
            self.assertEqual(ctx.exception.code,2)
        with patch('wo_retrieval.hybrid.cli.ready') as loader:
            self.assertEqual(run(ROOT,'retrieve',' \n ',5),{'results':[],'diagnostics':[]})
            loader.assert_not_called()

    def test_default_six_and_approved_five_gib_gate_and_evidence(self):
        from wo_retrieval.hybrid.cli import run
        from wo_retrieval.dense.resources import gate, unsafe
        from unittest.mock import MagicMock
        sample={'available_ram_bytes':int(5.5*1024**3),'commit_headroom_bytes':8*1024**3,
                'memory_load_percent':65,'disk_free_bytes':{'C:/':12*1024**3,'D:/':100*1024**3}}
        gpu={'free_mib':4007,'used_mib':0}
        for approved,expected_error in [(False,'below 6 GiB'),(True,'gate passed without loading')]:
            with tempfile.TemporaryDirectory() as folder:
                config=deepcopy(CONFIG); config['R3']['cache']['root']=folder
                encoder=MagicMock(model=None,lock=None)
                monitor=MagicMock();monitor.summary={}
                policies=[]
                def checked(sample,gpu,policy,flag):
                    self.assertEqual(flag,approved)
                    policies.append(policy)
                    gate(sample,gpu,policy,flag)
                    raise RuntimeError('gate passed without loading')
                with patch('wo_retrieval.hybrid.cli.read_protocol',return_value=config), \
                     patch('wo_retrieval.hybrid.cli.ready',return_value=(None,encoder,{})), \
                     patch('wo_retrieval.hybrid.cli.Monitor',return_value=monitor) as monitor_factory, \
                     patch('wo_retrieval.hybrid.cli.resource',return_value=sample), \
                     patch('wo_retrieval.hybrid.cli.gpu_resource',return_value=gpu), \
                     patch('wo_retrieval.hybrid.cli.gate',side_effect=checked):
                    with self.assertRaisesRegex(RuntimeError,expected_error):
                        run(ROOT,'retrieve','WO',5,approved,'explicit test authorization' if approved else None)
                encoder.load.assert_not_called()
                evidence=json.loads(next(Path(folder).rglob('run.json')).read_text())
                self.assertEqual(evidence['approved_low_memory'],approved)
                self.assertEqual(evidence['model_loading_gate_gib'],5 if approved else 6)
                self.assertEqual(monitor_factory.call_args.args[0],policies[0])
                if approved:
                    self.assertEqual(evidence['approval_note'],'explicit test authorization')
                    policy=evidence['effective_resource_policy']
                    self.assertEqual(policy['stop_available_ram_mib'],2048)
                    self.assertEqual(policy['stop_sustained_seconds'],0)
                    self.assertTrue(unsafe({**sample,'available_ram_bytes':2*1024**3-1},policy))
                    with self.assertRaisesRegex(RuntimeError,'below 5 GiB'):
                        gate({**sample,'available_ram_bytes':5*1024**3-1},gpu,policy,True)
                else:
                    self.assertEqual(evidence['effective_resource_policy'],config['hardware'])
                self.assertEqual(config['hardware'],CONFIG['hardware'])

    def test_low_memory_cli_requires_and_forwards_approval(self):
        from wo_retrieval.hybrid.cli import main, run
        with self.assertRaisesRegex(ValueError,'approval note'):
            run(ROOT,'smoke',approved_low_memory=True)
        with patch('sys.argv',['wo-hybrid','smoke','--approved-low-memory']):
            with self.assertRaises(SystemExit) as ctx: main()
            self.assertEqual(ctx.exception.code,2)
        with patch('sys.argv',['wo-hybrid','smoke','--approved-low-memory','--approval-note','human approval']), \
             patch('wo_retrieval.hybrid.cli.run',return_value={}) as called:
            main()
            self.assertEqual(called.call_args.args[4:],(True,'human approval'))


if __name__=='__main__':
    unittest.main()
