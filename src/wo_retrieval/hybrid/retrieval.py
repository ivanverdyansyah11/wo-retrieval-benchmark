"""Full Dense plus positive BM25 reciprocal rank fusion; never builds indexes."""

from datetime import datetime, timezone
import math
from pathlib import Path

from wo_retrieval.retrieval.lexical import RetrievalResult, digest, file_hash, load, read_protocol
from wo_retrieval.retrieval.text import normalize


def validate_policy(config):
    cfg = config['R4']
    expected = {'components': ['R2', 'R3'], 'rank_constant': 60, 'weights': [1.0, 1.0],
                'candidate_policy': 'full dense ranking plus every strictly positive BM25 candidate',
                'dense_candidate_depth': config['snapshot']['chunks'], 'retrieval_candidate_truncation': False,
                'absent_candidate_contribution': 0.0, 'zero_score_tail_filling': False,
                'bm25_zero_score_policy': 'excluded before ranks, contributes nothing'}
    if any(cfg.get(key) != value for key, value in expected.items()):
        raise ValueError('R4 policy conflict; no automatic policy change')
    if config['ranking']['sort'] != ['score_descending_unrounded', 'chunk_id_ascending_unicode_codepoint']:
        raise ValueError('Unsupported ranking policy')


def fuse(bm25, dense, rows, snapshot_id, top_k):
    if type(top_k) is not int or top_k <= 0:
        raise ValueError('top_k must be a positive integer')
    universe = {row['chunk_id']: row['document_id'] for row in rows}
    if not universe or len(universe) != len(rows):
        raise ValueError('Empty/duplicate chunk universe')
    for method, results in [('R2', bm25), ('R3', dense)]:
        ids = [item.chunk_id for item in results]
        if len(ids) != len(set(ids)) or (method == 'R3' and set(ids) != set(universe)):
            raise ValueError('Duplicate candidates or incomplete full Dense coverage')
        for rank, item in enumerate(results, 1):
            if (item.method_id != method or item.snapshot_id != snapshot_id
                    or universe.get(item.chunk_id) != item.document_id
                    or item.rank != rank or not math.isfinite(item.score)):
                raise ValueError('Invalid component ranking/metadata/score')
        if list(results) != sorted(results, key=lambda item: (-item.score, item.chunk_id)):
            raise ValueError('Component ranking violates deterministic score/ID order')
    # Filter before assigning eligible ranks; absent BM25 candidates contribute zero.
    positive = [item for item in bm25 if item.score > 0]
    bm_ranks = {item.chunk_id: rank for rank, item in enumerate(positive, 1)}
    contributions = {}
    for item in dense:
        bm_rank = bm_ranks.get(item.chunk_id)
        bm_value = 0.0 if bm_rank is None else 1.0 / (60 + bm_rank)
        dense_value = 1.0 / (60 + item.rank)
        contributions[item.chunk_id] = {'bm25_rank': bm_rank, 'dense_rank': item.rank,
                                      'bm25_contribution': bm_value, 'dense_contribution': dense_value,
                                      'rrf_score': bm_value + dense_value}
    order = sorted(contributions, key=lambda chunk: (-contributions[chunk]['rrf_score'], chunk))
    results = [RetrievalResult('R4', chunk, universe[chunk], rank, contributions[chunk]['rrf_score'], snapshot_id)
               for rank, chunk in enumerate(order[:top_k], 1)]
    return results, [{'chunk_id': item.chunk_id, **contributions[item.chunk_id]} for item in results]


class HybridRetriever:
    def __init__(self, bm25, dense, dense_manifest, config):
        validate_policy(config)
        bm_manifest = bm25.manifest
        if (not bm_manifest or bm_manifest.get('completion_status') != 'COMPLETE'
                or dense_manifest.get('completion_status') != 'COMPLETE'):
            raise ValueError('Incomplete component index')
        identity = dense_manifest['identity']
        for key in ['snapshot_id', 'snapshot_sha256', 'snapshot_fingerprint', 'protocol_sha256',
                    'serializer_version', 'serialization_policy_hash']:
            if bm_manifest.get(key) != identity.get(key):
                raise ValueError(f'Component fingerprint mismatch: {key}')
        for key, expected in [('snapshot_id', config['snapshot']['id']),
                              ('snapshot_sha256', config['snapshot']['manifest_sha256']),
                              ('snapshot_fingerprint', config['snapshot']['aggregate_fingerprint'])]:
            if bm_manifest.get(key) != expected:
                raise ValueError(f'Protocol fingerprint mismatch: {key}')
        for key in ['serialized_inputs_hash', 'universe_hash']:
            if bm_manifest['serialization_statistics'][key] != identity[key]:
                raise ValueError(f'Component inputs mismatch: {key}')
        def mapping(rows):
            return [(row['chunk_id'], row['document_id'], row['text_sha256']) for row in rows]
        if (bm25.method != 'R2' or mapping(bm25.rows) != mapping(dense.rows)
                or len(dense.rows) != config['snapshot']['chunks'] or dense.snapshot_id != config['snapshot']['id']):
            raise ValueError('Component chunk universe/mapping mismatch')
        self.bm25, self.dense, self.config = bm25, dense, config

    def retrieve_with_diagnostics(self, query, top_k):
        if type(top_k) is not int or top_k <= 0:
            raise ValueError('top_k must be a positive integer')
        text = normalize(query)
        if not text:
            return [], [], {'R2': [], 'R3': []}
        count = len(self.dense.rows)
        bm25 = self.bm25.retrieve(text, count)
        dense = self.dense.retrieve(text, count)
        results, diagnostics = fuse(bm25, dense, self.dense.rows, self.dense.snapshot_id, top_k)
        return results, diagnostics, {'R2': bm25, 'R3': dense}

    def retrieve(self, query, top_k):
        return self.retrieve_with_diagnostics(query, top_k)[0]


def ready(root: Path):
    # Existing loaders validate checksums/config/code, never repair or rebuild.
    from wo_retrieval.dense.index import DenseRetriever, cache_identity, cache_paths, load_vectors, token_audit
    from wo_retrieval.dense.model import BGEEncoder, model_files, offline_environment
    root = root.resolve()
    offline_environment()
    config = read_protocol(root)
    validate_policy(config)
    bm25 = load(root, 'R2')
    rows = bm25.rows
    local, hashes = model_files(root, config)
    encoder = BGEEncoder(local, config)
    mapping, counts = token_audit(rows, encoder)
    identity = cache_identity(root, config, bm25.manifest['serialization_statistics'], hashes, mapping)
    directory, _ = cache_paths(config, identity)
    vectors, manifest = load_vectors(directory, identity, mapping)
    dense = DenseRetriever(rows, vectors, encoder, config['snapshot']['id'])
    hybrid = HybridRetriever(bm25, dense, manifest, config)
    bm_path = root / 'experiments/indexes/R2'
    identity_r4 = {'snapshot_id': config['snapshot']['id'], 'snapshot_fingerprint': config['snapshot']['aggregate_fingerprint'],
                   'bm25_index_fingerprint': digest(bm25.manifest), 'dense_index_fingerprint': digest(manifest),
                   'bm25_index_path': str(bm_path), 'dense_index_path': str(directory),
                   'rrf_k': 60, 'candidate_policy': config['R4']['candidate_policy'],
                   'zero_negative_bm25': 'excluded before eligible ranks; no contribution or pseudo-rank',
                   'tie_breaking': config['ranking']['sort'], 'serialized_inputs_hash': identity['serialized_inputs_hash'],
                   'universe_hash': identity['universe_hash'], 'model_revision': identity['model_revision'],
                   'dependency_versions': {**bm25.manifest['dependency_versions'], **identity['dependency_versions']},
                   'protocol_sha256': identity['protocol_sha256'], 'config_fingerprint': digest(config['R4']),
                   'code_file_hashes': {p.name: file_hash(p) for p in sorted(Path(__file__).parent.glob('*.py'))},
                   'shared_code_file_hashes': identity['shared_code_file_hashes'],
                   'dense_code_file_hashes': identity['dense_code_file_hashes']}
    metadata = {'status': 'READY_WEIGHTS_NOT_LOADED', 'method_id': 'R4', 'identity': identity_r4,
                'fingerprint': digest(identity_r4), 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
                'chunks': len(rows), 'tokenizer_audit': counts, 'index_rebuild': False,
                'authorization': 'user attachment abf1b34f-b257-4797-ac6d-f13ee1cd8a0f; pilot development only',
                'protocol_status': config['status'], 'effectiveness_evaluation': 'NOT RUN'}
    return hybrid, encoder, metadata
