from copy import deepcopy
from fractions import Fraction
import json
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from wo_retrieval.dense.index import DenseRetriever
from wo_retrieval.hybrid.retrieval import HybridRetriever
from wo_retrieval.query_vectors.artifacts import (
    CachedEncoder, contract, load_artifact, publish, validate_vector,
)
from wo_retrieval.query_vectors.offline import retrievers
from wo_retrieval.query_vectors.__main__ import encode, main
from wo_retrieval.retrieval.lexical import file_hash
from wo_retrieval.dense.model import unit_vectors
from wo_retrieval.retrieval.lexical import RetrievalResult
from test_hybrid_retrieval import fixture


QUERY = "Siapa yang mengoordinasikan vendor saat acara?"


class QueryArtifactsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name) / "synthetic-query"
        self.addCleanup(self.temp.cleanup)
        self.bm, _, self.manifest, self.config = fixture()
        self.manifest['identity'].update(model_id='SYNTHETIC_NOT_BGE', model_revision='fixture-only',
                                         device='cuda:0', precision='float16', batch_size=1, max_length=640)
        self.expected = contract(self.manifest)
        self.vector = np.zeros((1, 1024), dtype=np.float32)
        self.vector[0, :3] = [1, .5, -.25]
        self.encoding = dict(device='cuda:0', precision='float16', batch_size=1, max_length=640,
                             actual_tokens_including_special=14, truncation=False)

    def save(self, query=QUERY):
        return publish(self.directory, self.expected, 'SYNTHETIC-001', query, self.vector, self.encoding)

    def load(self, query=QUERY, expected=None):
        return load_artifact(self.directory, expected or self.expected, 'SYNTHETIC-001', query)

    def mutate(self, action):
        path = self.directory / 'manifest.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        action(data)
        path.write_text(json.dumps(data), encoding='utf-8')

    def test_complete_roundtrip_verbatim_readonly_and_no_overwrite(self):
        self.save()
        vector, manifest = self.load()
        self.assertTrue(np.array_equal(vector, self.vector))
        self.assertFalse(vector.flags.writeable)
        self.assertEqual(manifest['completion_status'], 'COMPLETE')
        with self.assertRaises(FileExistsError): self.save()

    def test_exact_query_hash_including_outer_whitespace_and_id(self):
        self.save()
        for query in (QUERY+' ', QUERY.replace('vendor', 'katering'), '', None):
            with self.subTest(query=query), self.assertRaises(ValueError): self.load(query)
        with self.assertRaises(ValueError):
            load_artifact(self.directory, self.expected, 'OTHER', QUERY)

    def test_model_config_snapshot_index_and_serializer_mismatches(self):
        self.save()
        for key in ('model_id', 'model_revision', 'snapshot_id', 'protocol_sha256', 'precision', 'max_length'):
            expected = deepcopy(self.expected)
            expected['dense_identity'][key] = 'changed'
            with self.subTest(key=key), self.assertRaises(ValueError): self.load(expected=expected)
        for key in ('query_input_contract', 'vector_stage', 'dimension', 'corpus_index_manifest_sha256_canonical'):
            expected = deepcopy(self.expected); expected[key] = 'changed'
            with self.subTest(key=key), self.assertRaises(ValueError): self.load(expected=expected)

    def test_corruption_and_missing_payload(self):
        self.save()
        path = self.directory / 'vector.npy'
        path.write_bytes(path.read_bytes() + b'corruption')
        with self.assertRaisesRegex(ValueError, 'checksum'): self.load()
        path.unlink()
        with self.assertRaises(ValueError): self.load()

    def test_incomplete_and_effective_input_mismatch(self):
        self.save()
        self.mutate(lambda m: m.update(completion_status='INCOMPLETE'))
        with self.assertRaises(ValueError): self.load()
        self.mutate(lambda m: m.update(completion_status='COMPLETE', effective_input_sha256='wrong'))
        with self.assertRaises(ValueError): self.load()

    def test_malformed_manifest_rejected(self):
        self.save()
        for contents in ('[]', '{broken', '{}'):
            (self.directory/'manifest.json').write_text(contents,encoding='utf-8')
            with self.subTest(contents=contents), self.assertRaises(ValueError): self.load()

    def test_invalid_vectors_even_with_updated_checksum(self):
        self.save()
        invalid = [np.zeros((1,1023), np.float32), np.zeros((1024,), np.float32),
                   self.vector.astype(np.float64), np.zeros((1,1024), np.float32),
                   np.full((1,1024), np.nan, np.float32), np.full((1,1024), np.inf, np.float32),
                   np.full((1,1024), 1e38, np.float32)]
        for vector in invalid:
            with self.subTest(shape=vector.shape, dtype=vector.dtype), np.errstate(over='ignore'):
                with self.assertRaises(ValueError): validate_vector(vector)
                np.save(self.directory/'vector.npy', vector, allow_pickle=False)
                self.mutate(lambda m: m.update(artifact_sha256={'vector.npy':file_hash(self.directory/'vector.npy')}))
                with self.assertRaises(ValueError): self.load()

    def test_provenance_truncation_timestamp_and_payload_set(self):
        baseline = self.save()
        for action in (lambda m: m['encoding'].update(actual_tokens_including_special=641),
                       lambda m: m['encoding'].update(truncation=True),
                       lambda m: m['encoding'].update(device='cpu'),
                       lambda m: m.update(created_at_utc='2026-10-09T01:00:00'),
                       lambda m: m.update(artifact_sha256={'../escape': 'hash'})):
            (self.directory/'manifest.json').write_text(json.dumps(baseline), encoding='utf-8')
            self.mutate(action)
            with self.assertRaises(ValueError): self.load()

    def test_cached_adapter_rejects_other_input(self):
        self.save()
        encoder = CachedEncoder(self.directory, self.expected, 'SYNTHETIC-001', QUERY)
        with self.assertRaises(ValueError): encoder.encode(QUERY+' altered')

    def test_shared_r3_r4_exact_ranking_scores_and_independent_rrf(self):
        self.save()
        corpus = np.zeros((3,1024), np.float32)
        corpus[:, :3] = np.eye(3, dtype=np.float32)
        components = self.bm, corpus, self.manifest, self.config, Path('unused')
        dense, hybrid = retrievers(components, self.directory, 'SYNTHETIC-001', QUERY)
        results, breakdown, ranks = hybrid.retrieve_with_diagnostics(QUERY, 3)
        r3 = dense.retrieve(QUERY, 3)
        self.assertIs(hybrid.dense, dense)
        self.assertEqual(r3, ranks['R3'])
        self.assertEqual(self.bm.calls, [(QUERY,3)])
        original = MagicMock(); original.encode.return_value = self.vector.copy()
        live_shape_fixture = DenseRetriever(self.bm.rows, corpus, original, 'S')
        self.assertEqual(r3, live_shape_fixture.retrieve(QUERY, 3))
        original.encode.assert_called_once_with(QUERY)
        oracle = {}
        for row in ranks['R3']:
            bm_rank = next((r.rank for r in ranks['R2'] if r.chunk_id==row.chunk_id and r.score>0), None)
            oracle[row.chunk_id] = Fraction(1,60+row.rank) + (Fraction(1,60+bm_rank) if bm_rank else 0)
        self.assertEqual([r.chunk_id for r in results], sorted(oracle, key=lambda c:(-oracle[c],c)))
        for row in breakdown:
            self.assertEqual(row['rrf_score'], row['bm25_contribution']+row['dense_contribution'])
            self.assertAlmostEqual(row['rrf_score'],float(oracle[row['chunk_id']]),places=15)

    def test_normalization_parity_empty_invalid_and_topk(self):
        query = '  koordinasi\r\nvendor  '
        self.save(query)
        corpus = np.zeros((3,1024), np.float32); corpus[:,:3] = np.eye(3, dtype=np.float32)
        dense, hybrid = retrievers((self.bm,corpus,self.manifest,self.config,Path('unused')),
                                   self.directory,'SYNTHETIC-001',query)
        hybrid.retrieve(query,1)
        self.assertEqual(self.bm.calls,[('koordinasi\nvendor',3)])
        for retriever in (dense,hybrid):
            self.assertEqual(retriever.retrieve(' ',5),[])
            for k in (0,-1,True,1.2):
                with self.assertRaises(ValueError): retriever.retrieve(query,k)
            with self.assertRaises(ValueError): retriever.retrieve(None,5)

    def test_full_371_shared_dense_ranking_and_tail_eligibility(self):
        self.save()
        self.bm.rows = [{'chunk_id':f'C{i:03}', 'document_id':f'D{i:03}', 'text_sha256':str(i)} for i in range(371)]
        self.bm.results = [RetrievalResult('R2','C370','D370',1,2.0,'S')]
        config = deepcopy(self.config)
        config['snapshot']['chunks']=371
        config['R4']['dense_candidate_depth']=371
        corpus = unit_vectors(np.random.default_rng(42).normal(size=(371,1024)).astype(np.float32))
        dense, hybrid = retrievers((self.bm,corpus,self.manifest,config,Path('unused')),
                                   self.directory,'SYNTHETIC-001',QUERY)
        r3 = dense.retrieve(QUERY,371)
        results, diagnostics, components = hybrid.retrieve_with_diagnostics(QUERY,371)
        self.assertEqual(r3,components['R3'])
        self.assertEqual(len(results),371)
        self.assertEqual(len({r.chunk_id for r in results}),371)
        tail = next(row for row in diagnostics if row['chunk_id']=='C370')
        self.assertEqual(tail['bm25_rank'],1)
        self.assertEqual(tail['bm25_contribution'],1/61)

    def test_score_cli_synthetic_shared_artifact_no_encoder_loading(self):
        self.save()
        corpus = np.zeros((3,1024), np.float32); corpus[:,:3] = np.eye(3,dtype=np.float32)
        components = self.bm,corpus,self.manifest,self.config,Path('unused')
        for method in ('R3','R4'):
            with patch('sys.argv',['query_vectors','score','--corpus-index','fixture',
                                   '--artifact',str(self.directory),'--query-id','SYNTHETIC-001',
                                   '--query',QUERY,'--method',method]), \
                 patch('wo_retrieval.query_vectors.__main__.load_components',return_value=components), \
                 patch('wo_retrieval.query_vectors.__main__.encode') as encoder, \
                 patch('sys.stdout',new_callable=io.StringIO) as output:
                main()
                data=json.loads(output.getvalue())
                self.assertEqual(data['method_id'],method)
                self.assertEqual(data['mode'],'technical_offline_cached_query')
                self.assertEqual(data['live_end_to_end_latency'],'NOT MEASURED')
                encoder.assert_not_called()


class EncoderSafetyTests(unittest.TestCase):
    def test_explicit_approval_required_before_model_initialization(self):
        with patch('wo_retrieval.dense.model.BGEEncoder') as encoder:
            with self.assertRaises(ValueError): encode(Path('.'),None,Path('unused'),'Q',QUERY)
            encoder.assert_not_called()

    def test_default_and_approved_final_gates_preserved_no_loading_on_failure(self):
        from wo_retrieval.retrieval.lexical import read_protocol
        config = read_protocol(Path(__file__).resolve().parents[1])
        components = (None,None,{},config,Path('unused'))
        with tempfile.TemporaryDirectory(prefix='synthetic-safety-') as temporary:
            base = Path(temporary)
            def fixture_path(value):
                return base if str(value)=='D:/ModelCache/wo-retrieval-benchmark/query_vectors' else Path(value)
            for approved in (False,True):
                output = base/str(approved)
                with patch('wo_retrieval.dense.model.BGEEncoder') as encoder, \
                     patch('wo_retrieval.query_vectors.__main__.Path',side_effect=fixture_path), \
                     patch('wo_retrieval.dense.model.offline_environment'), \
                     patch('wo_retrieval.dense.resources.resource',return_value={}), \
                     patch('wo_retrieval.dense.resources.gpu_resource',return_value={}), \
                     patch('wo_retrieval.dense.resources.Monitor'), \
                     patch('wo_retrieval.dense.resources.gate',side_effect=[None,RuntimeError('final gate')]) as gate, \
                     patch.dict('sys.modules',{'torch':MagicMock(),'FlagEmbedding':MagicMock()}):
                    encoder.return_value.tokens.return_value={'input_ids':[1,2,3]}
                    with self.assertRaisesRegex(RuntimeError,'final gate'):
                        encode(Path('.'),components,output,'SYNTHETIC',QUERY,approved,'unit-test approval only')
                    self.assertEqual(gate.call_count,2)
                    for call in gate.call_args_list:
                        self.assertIs(call.args[3],approved)
                        self.assertEqual(call.args[2]['recommended_available_ram_gib'],6)
                        self.assertEqual(call.args[2]['stop_available_ram_mib'],2048)
                        self.assertEqual(call.args[2]['stop_sustained_seconds'],0)
                    encoder.return_value.load.assert_not_called()
                    encoder.return_value.encode.assert_not_called()
                    self.assertFalse(output.exists())
                    evidence=json.loads(output.with_name(output.name+'.run.json').read_text(encoding='utf8'))
                    self.assertEqual(evidence['completion_status'],'INCOMPLETE')
                    self.assertIn('final gate',evidence['error'])

    def test_real_cache_boundary_rejects_unapproved_path_before_loading(self):
        with tempfile.TemporaryDirectory() as tmp,patch('wo_retrieval.dense.model.BGEEncoder') as encoder:
            with self.assertRaisesRegex(ValueError,'approved D: query cache'):
                encode(Path('.'),None,Path(tmp)/'outside','SYNTHETIC',QUERY,False,'unit-test approval only')
            encoder.assert_not_called()


if __name__ == '__main__':
    unittest.main()
