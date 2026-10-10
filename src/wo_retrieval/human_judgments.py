"""Frozen development annotation package and versioned human-only judgments; stdlib only."""
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import random
import tempfile
import tomllib

from wo_retrieval.retrieval.text import comparison, serialize

LABEL = 'Researcher-annotated relevance judgments'
SEED = 17042
METHODS = ('R1', 'R2', 'R3', 'R4')
WORKSPACE = 'experiments/human_judgments/development_v2'
PAIR_FIELDS = {'assessment_id', 'query_id', 'chunk_id', 'document_id', 'query_text',
               'chunk_text', 'title', 'heading', 'source_locator', 'query_text_sha256',
               'chunk_text_sha256', 'snapshot_id', 'snapshot_fingerprint'}
PROTOCOL = {
    'version': 'wo_researcher_pooled_development_v1', 'scope': 'development',
    'binary_threshold': 1, 'ndcg_gain': '2^grade - 1', 'ndcg_discount': 'log2(rank+1)',
    'ndcg_ideal_scope': 'all human-resolved pairs in the union Top-20 pool for this query',
    'completeness_policy': 'block entire run-set until every pool pair is RESOLVED',
    'zero_ideal_policy': 'block pooled evaluation; no known relevance does not prove no answer',
    'short_ranking_policy': 'missing result slots have zero hit/gain; no dummy qrels',
    'aggregation': 'macro mean over all 18 fixed queries; same IDs for all methods',
    'ties': 'preserve score-descending, chunk-ID-ascending saved ranking',
    'recall': 'NOT COMPUTED: corpus-wide relevant set unknown',
    'main_evaluation': 'NOT ENABLED; independent queries and approved frozen scope required',
}


def file_hash(path):
    with Path(path).open('rb') as stream:
        digest = sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def digest(value):
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()


def text_hash(value):
    return sha256(value.encode('utf-8')).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]


def jsonl_text(rows):
    return ''.join(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n' for row in rows)


def atomic_text(path, text):
    path = Path(path)
    fd, name = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if Path(name).exists():
            Path(name).unlink()


def write_json(path, value):
    atomic_text(path, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def verify_hashes(root, hashes):
    root = Path(root).resolve()
    for name, expected in hashes.items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file() or file_hash(path) != expected:
            raise ValueError(f'Frozen input changed or path escaped root: {name}')


def unique(rows, fields):
    result = {}
    for row in rows:
        key = tuple(row[field] for field in fields)
        if key in result:
            raise ValueError('Duplicate identifier/pair')
        result[key] = row
    return result


def validate_rankings(rankings, queries, chunks, snapshot_id):
    runs = unique(rankings, ('query_id', 'method'))
    if set(runs) != {(q, m) for q in queries for m in METHODS}:
        raise ValueError('Missing/extra method-query runs')
    for run in rankings:
        if run['query_text'] != queries[run['query_id']]['text']:
            raise ValueError('Ranking query text mismatch')
        rows = run['results']
        unique(rows, ('chunk_id',))
        if rows != sorted(rows, key=lambda r: (-r['score'], r['chunk_id'])):
            raise ValueError('Ranking tie/order policy violated')
        for rank, row in enumerate(rows, 1):
            if (type(row['rank']) is not int or row['rank'] != rank
                    or type(row['score']) not in (int, float) or not math.isfinite(row['score'])
                    or row['method_id'] != run['method'] or row['snapshot_id'] != snapshot_id
                    or row['chunk_id'] not in chunks
                    or row['document_id'] != chunks[row['chunk_id']]['document_id']):
                raise ValueError('Invalid ranking metadata/score/binding')
        if run['method'] in ('R3', 'R4') and {r['chunk_id'] for r in rows} != set(chunks):
            raise ValueError('Dense/hybrid full universe incomplete')
        if run['method'] in ('R1', 'R2') and any(r['score'] <= 0 for r in rows):
            raise ValueError('Lexical candidate policy changed')
    return runs


def validate_split(development, evaluation, semantic_review_confirmed=False):
    """Automated overlap checks cannot certify semantic separation of differently named families."""
    unique(development, ('query_id',)); unique(evaluation, ('query_id',))
    for rows in (development, evaluation):
        if any(not r.get('information_need_family_id') for r in rows):
            raise ValueError('Information-need family missing')
    for key, transform in [('query_id', str), ('information_need_family_id', str), ('text', comparison)]:
        if {transform(r[key]) for r in development} & {transform(r[key]) for r in evaluation}:
            raise ValueError('Development/evaluation overlap: ' + key)
    if any(r.get('purpose') != 'development' for r in development):
        raise ValueError('Invalid development purpose')
    if evaluation and (not semantic_review_confirmed or any(r.get('purpose') != 'evaluation' for r in evaluation)):
        raise ValueError('Independent evaluation requires documented human semantic split review')


def audit_sources(root):
    """Validate saved artifacts without importing a retriever, numerical runtime or model."""
    root = Path(root).resolve()
    snapshot_path = root / 'data/versions/v2_ai_corrected/validation/pilot_snapshot.json'
    snapshot = read_json(snapshot_path)
    fingerprint = snapshot['aggregate_fingerprint']['value']
    if digest(snapshot['artifact_sha256']) != fingerprint:
        raise ValueError('Snapshot aggregate fingerprint invalid')
    hashes = {**snapshot['artifact_sha256'], **snapshot['source_file_sha256']}
    for folder, manifest_name in [
        ('experiments/results/milestone_9a12_development_pilot', 'run_manifest.json'),
        ('experiments/results/milestone_9a13_judgment_pool', 'manifest.json'),
        ('experiments/results/milestone_9a14_pilot_assessment_audit', 'manifest.json'),
        ('experiments/results/milestone_9a15_second_assessor_agreement_audit', 'manifest.json')]:
        manifest = read_json(root / folder / manifest_name)
        hashes[folder + '/' + manifest_name] = file_hash(root / folder / manifest_name)
        for name, value in manifest['outputs'].items():
            hashes[folder + '/' + name] = value
    for method in ('R1', 'R2', 'R3'):
        folder = 'experiments/indexes/v2_ai_corrected/' + method
        manifest = read_json(root / folder / 'manifest.json')
        identity = manifest.get('identity', manifest)
        if (manifest['completion_status'] != 'COMPLETE' or manifest['indexed_chunks'] != 371
                or identity['snapshot_fingerprint'] != fingerprint):
            raise ValueError('V2 index identity incomplete/mismatched')
        hashes[folder + '/manifest.json'] = file_hash(root / folder / 'manifest.json')
        for name, value in manifest.get('artifact_sha256_derived', manifest['artifact_sha256']).items():
            hashes[folder + '/' + name] = value
    hashes[str(snapshot_path.relative_to(root))] = file_hash(snapshot_path)
    qpath = 'data/benchmark/development_queries_draft.jsonl'
    rpath = 'experiments/results/milestone_9a12_development_pilot/rankings.jsonl'
    inputs = read_json(root / 'experiments/results/milestone_9a12_development_pilot/run_manifest.json')['inputs']
    hashes[qpath] = inputs['query_sha256']
    hashes['data/versions/v2_ai_corrected/benchmark/development_qrels_ai_silver_v2.jsonl'] = inputs['qrels_sha256']
    hashes['experiments/indexes/v2_ai_corrected/R3/manifest.json'] = inputs['dense_manifest_sha256']
    verify_hashes(root, hashes)
    queries = {q['query_id']: q for q in unique(read_jsonl(root / qpath), ('query_id',)).values()}
    validate_split(list(queries.values()), [])
    chunks = {c['chunk_id']: c for c in unique(read_jsonl(root / 'data/versions/v2_ai_corrected/chunks/chunks.jsonl'), ('chunk_id',)).values()}
    rankings = read_jsonl(root / rpath)
    validate_rankings(rankings, queries, chunks, snapshot['snapshot_id'])
    pool = {(r['query_id'], c['chunk_id']) for r in rankings for c in r['results'][:20]}
    ledger = read_jsonl(root / 'experiments/results/milestone_9a13_judgment_pool/blind_assessment_ledger.jsonl')
    unique(ledger, ('assessment_id',)); unique(ledger, ('query_id', 'chunk_id'))
    if (len(pool) != 654 or pool != {(r['query_id'], r['chunk_id']) for r in ledger}
            or len(queries) != 18 or len(chunks) != 371 or len(rankings) != 72):
        raise ValueError('Development/pool counts or mapping changed')
    policy = tomllib.loads((root / 'experiments/configs/retrieval_protocol_v1.toml').read_text(encoding='utf-8'))['serialization']
    serialized = {cid: serialize(c, policy)[0] for cid, c in chunks.items()}
    for method in ('R1', 'R2'):
        indexed = read_json(root / f'experiments/indexes/v2_ai_corrected/{method}/documents.json')
        if {r['chunk_id']: r['text'] for r in indexed} != serialized or len(indexed) != 371:
            raise ValueError('Lexical index serialized corpus mismatch')
    dense = read_json(root / 'experiments/indexes/v2_ai_corrected/R3/manifest.json')
    for query in dense['exchange_manifest']['query_mapping']:
        qid = query['query_id']
        if query['text'] != queries[qid]['text'] or query['text_sha256'] != text_hash(query['text']):
            raise ValueError('Dense query cache text binding mismatch')
        folder = f'experiments/indexes/v2_ai_corrected/R3/query_vectors/{qid}'
        cache = read_json(root / folder / 'manifest.json')
        if cache['completion_status'] != 'COMPLETE':
            raise ValueError('Query vector cache incomplete')
        hashes[folder + '/manifest.json'] = file_hash(root / folder / 'manifest.json')
        for name, value in cache['artifact_sha256'].items():
            hashes[folder + '/' + name] = value
    verify_hashes(root, hashes)
    for row in ledger:
        if (row['query_text'] != queries[row['query_id']]['text'] or row['serialized_chunk_text'] != serialized[row['chunk_id']]
                or row['serialized_text_sha256'] != text_hash(row['serialized_chunk_text'])
                or row['query_text_sha256'] != text_hash(row['query_text'])
                or row['document_id'] != chunks[row['chunk_id']]['document_id']
                or row['source_snapshot_id'] != snapshot['snapshot_id']
                or row['source_snapshot_fingerprint'] != fingerprint):
            raise ValueError('Pool text/snapshot binding mismatch')
    qrels = read_jsonl(root / 'data/versions/v2_ai_corrected/benchmark/development_qrels_ai_silver_v2.jsonl')
    silver = unique(qrels, ('query_id', 'chunk_id'))
    if len(silver) != 684 or sum(pair in silver for pair in pool) != 90:
        raise ValueError('Existing qrels/pool counts changed')
    for run in rankings:
        for row in run['results']:
            old = silver.get((run['query_id'], row['chunk_id']))
            if row['silver_grade'] != (old['grade'] if old else None):
                raise ValueError('Saved silver binding changed')
    for row in qrels:
        if (row['query_text'] != queries[row['query_id']]['text']
                or row['query_text_sha256'] != text_hash(row['query_text'])
                or row['chunk_text_sha256'] != text_hash(chunks[row['chunk_id']]['text'])
                or row['serialized_text_sha256'] != text_hash(serialized[row['chunk_id']])
                or row['snapshot_id'] != snapshot['snapshot_id'] or row['snapshot_fingerprint'] != fingerprint
                or type(row['grade']) is not int or row['grade'] not in (0, 1, 2)):
            raise ValueError('Silver qrel binding invalid')
    return dict(snapshot_id=snapshot['snapshot_id'], snapshot_fingerprint=fingerprint, hashes=hashes,
                queries=queries, chunks=chunks, serialized=serialized, pool=pool, rankings=rankings,
                existing_silver_pairs_in_pool=90)


def prepare(root, workspace):
    root, workspace = Path(root).resolve(), Path(workspace).resolve()
    if workspace.exists() or not workspace.is_relative_to(root / 'experiments/human_judgments'):
        raise ValueError('Workspace exists or outside dedicated human storage')
    audit = audit_sources(root)
    rows = []
    for i, (qid, cid) in enumerate(sorted(audit['pool']), 1):
        chunk = audit['chunks'][cid]; query = audit['queries'][qid]['text']
        rows.append(dict(assessment_id=f'HUMAN-DEV-{i:04d}', query_id=qid, chunk_id=cid,
            document_id=chunk['document_id'], query_text=query, chunk_text=audit['serialized'][cid],
            title=chunk['title'], heading=chunk['heading'], source_locator=chunk['source_locator'],
            query_text_sha256=text_hash(query), chunk_text_sha256=text_hash(audit['serialized'][cid]),
            snapshot_id=audit['snapshot_id'], snapshot_fingerprint=audit['snapshot_fingerprint']))
    random.Random(SEED).shuffle(rows)
    workspace.mkdir(parents=True)
    atomic_text(workspace / 'annotation_input.jsonl', jsonl_text(rows))
    manifest = dict(schema_version=1, package_id='wo-human-development-v2-17042', scope='development',
        research_status='Development pooled evaluation — Not Final Evaluation', label=LABEL,
        assessor_id='Muhammad Ivan Verdyansyah', expert_validated=False, independently_validated=False,
        exposure_disclosure='Researcher owns project and may have seen rankings/AI assessments; interface hides these fields, isolation not claimed.',
        created_at_utc=datetime.now(timezone.utc).isoformat(), seed=SEED,
        ordering='sorted query_id/chunk_id, random.Random(17042).shuffle; stored order authoritative',
        pair_count=654, snapshot_id=audit['snapshot_id'], snapshot_fingerprint=audit['snapshot_fingerprint'],
        input_sha256=file_hash(workspace / 'annotation_input.jsonl'), frozen_source_hashes=audit['hashes'],
        query_metadata=[{k: q[k] for k in ('query_id', 'text', 'style', 'information_need_family_id', 'purpose')}
                        for q in sorted(audit['queries'].values(), key=lambda q: q['query_id'])],
        protocol=PROTOCOL, protocol_sha256=digest(PROTOCOL), ranking_path='experiments/results/milestone_9a12_development_pilot/rankings.jsonl')
    write_json(workspace / 'annotation_manifest.json', manifest)
    atomic_text(workspace / 'human_judgment_history.jsonl', '')
    write_json(workspace / 'storage_manifest.json', dict(schema_version=1, package_id=manifest['package_id'],
        input_sha256=manifest['input_sha256'], annotation_manifest_sha256=file_hash(workspace / 'annotation_manifest.json'),
        label=LABEL, assessor_id=manifest['assessor_id'], scope='development', expert_validated=False,
        independently_validated=False, storage='atomic versioned JSONL history; latest revision is current judgment',
        initialized_at_utc=datetime.now(timezone.utc).isoformat()))
    return load_package(root, workspace)


def load_package(root, workspace):
    root, workspace = Path(root).resolve(), Path(workspace).resolve()
    manifest = read_json(workspace / 'annotation_manifest.json')
    if (manifest['scope'] != 'development' or manifest['protocol'] != PROTOCOL
            or manifest['protocol_sha256'] != digest(PROTOCOL) or manifest['label'] != LABEL
            or manifest['expert_validated'] is not False or manifest['independently_validated'] is not False):
        raise ValueError('Main scope/AI labels/changed protocol not accepted')
    if file_hash(workspace / 'annotation_input.jsonl') != manifest['input_sha256']:
        raise ValueError('Annotation input checksum mismatch')
    verify_hashes(root, manifest['frozen_source_hashes'])
    rows = read_jsonl(workspace / 'annotation_input.jsonl')
    unique(rows, ('assessment_id',)); unique(rows, ('query_id', 'chunk_id'))
    if len(rows) != manifest['pair_count']:
        raise ValueError('Annotation count mismatch')
    queries = {q['query_id']: q for q in manifest['query_metadata']}
    validate_split(list(queries.values()), [])
    for row in rows:
        if (set(row) != PAIR_FIELDS or row['query_id'] not in queries
                or row['query_text'] != queries[row['query_id']]['text']
                or row['query_text_sha256'] != text_hash(row['query_text'])
                or row['chunk_text_sha256'] != text_hash(row['chunk_text'])
                or row['snapshot_id'] != manifest['snapshot_id']
                or row['snapshot_fingerprint'] != manifest['snapshot_fingerprint']):
            raise ValueError('Annotation allowlist/binding mismatch')
    storage = read_json(workspace / 'storage_manifest.json')
    if (storage['annotation_manifest_sha256'] != file_hash(workspace / 'annotation_manifest.json')
            or storage['input_sha256'] != manifest['input_sha256'] or storage['package_id'] != manifest['package_id']
            or storage['assessor_id'] != manifest['assessor_id'] or storage['label'] != LABEL
            or storage['scope'] != manifest['scope'] or storage['expert_validated'] is not False
            or storage['independently_validated'] is not False):
        raise ValueError('Storage provenance mismatch')
    return dict(root=root, workspace=workspace, manifest=manifest, rows=rows,
                pairs={r['assessment_id']: r for r in rows})


def binding(package, row):
    return {**{k: row[k] for k in ('query_id', 'chunk_id', 'document_id', 'query_text_sha256',
            'chunk_text_sha256', 'snapshot_id', 'snapshot_fingerprint')},
            'input_sha256': package['manifest']['input_sha256']}


def validate_decision(status, grade, notes, evidence, row):
    if (status == 'RESOLVED' and (type(grade) is not int or grade not in (0, 1, 2))
            or status in ('PENDING', 'UNRESOLVED') and grade is not None
            or status not in ('PENDING', 'UNRESOLVED', 'RESOLVED')):
        raise ValueError('Invalid grade/status; unknown is never Grade 0')
    if any(not isinstance(s, str) or len(s) > 10000 for s in (notes, evidence)):
        raise ValueError('Notes/evidence must be text, maximum 10000 characters')
    if evidence and evidence not in row['chunk_text']:
        raise ValueError('Evidence must be an exact substring of the displayed chunk')


def load_history(package, events=None):
    events = read_jsonl(package['workspace'] / 'human_judgment_history.jsonl') if events is None else events
    latest = {}
    for sequence, event in enumerate(events, 1):
        row = package['pairs'].get(event.get('assessment_id'))
        if row is None or set(event) != {'sequence','assessment_id','revision','status','grade','notes','evidence',
                                         'binding','provenance','previous_event_sha256','event_sha256'}:
            raise ValueError('Unknown human event/fields')
        old = latest.get(row['assessment_id'])
        expected_revision = old['revision'] + 1 if old else 1
        if (event['sequence'] != sequence or event['revision'] != expected_revision
                or event['binding'] != binding(package, row)
                or event['previous_event_sha256'] != (events[sequence-2]['event_sha256'] if sequence > 1 else None)
                or event['event_sha256'] != digest({k: v for k, v in event.items() if k != 'event_sha256'})):
            raise ValueError('History revision/hash/binding invalid')
        validate_decision(event['status'], event['grade'], event['notes'], event['evidence'], row)
        provenance = event['provenance']
        if (set(provenance) - {'import_source'} != {'label','assessor_id','recorded_at_utc','protocol_sha256','scope',
                               'expert_validated','independently_validated'}
                or provenance['label'] != LABEL or provenance['assessor_id'] != package['manifest']['assessor_id']
                or provenance['protocol_sha256'] != package['manifest']['protocol_sha256']
                or provenance['scope'] != 'development' or provenance['expert_validated'] is not False
                or provenance['independently_validated'] is not False
                or datetime.fromisoformat(provenance['recorded_at_utc']).utcoffset() is None):
            raise ValueError('Human judgment provenance invalid')
        if 'import_source' in provenance:
            origin = provenance['import_source']
            if (set(origin) != {'source_path','source_sha256','audit_path','audit_sha256',
                                'imported_at_utc','original_assessed_at_utc'}
                    or origin['imported_at_utc'] != provenance['recorded_at_utc']
                    or origin['original_assessed_at_utc'] is not None
                    or any(not isinstance(origin[k], str) or not Path(origin[k]).is_absolute()
                           for k in ('source_path','audit_path'))
                    or any(not isinstance(origin[k], str) or len(origin[k]) != 64
                           or any(c not in '0123456789abcdef' for c in origin[k])
                           for k in ('source_sha256','audit_sha256'))):
                raise ValueError('Invalid import provenance; original assessment time is unknown')
        latest[row['assessment_id']] = event
    return events, latest


@contextmanager
def exclusive(path):
    path = Path(path)
    try:
        with path.open('x', encoding='utf-8') as stream:
            stream.write(str(os.getpid()))
    except FileExistsError as error:
        raise ValueError('Workspace locked by another operation. See recovery instructions.') from error
    try:
        yield
    finally:
        path.unlink()


def decision_event(package, events, row, revision, status, grade, notes, evidence, import_source=None):
    event = dict(sequence=len(events)+1, assessment_id=row['assessment_id'], revision=revision,
        status=status, grade=grade, notes=notes, evidence=evidence, binding=binding(package, row),
        provenance=dict(label=LABEL, assessor_id=package['manifest']['assessor_id'], scope='development',
            recorded_at_utc=import_source['imported_at_utc'] if import_source else datetime.now(timezone.utc).isoformat(),
            protocol_sha256=package['manifest']['protocol_sha256'], expert_validated=False, independently_validated=False),
        previous_event_sha256=events[-1]['event_sha256'] if events else None)
    if import_source:
        event['provenance']['import_source'] = import_source
    event['event_sha256'] = digest(event)
    return event


def save_decision(package, assessment_id, status, grade, notes='', evidence='', expected_revision=0):
    row = package['pairs'].get(assessment_id)
    if row is None or type(expected_revision) is not int or expected_revision < 0:
        raise ValueError('Unknown pair/revision')
    validate_decision(status, grade, notes, evidence, row)
    with exclusive(package['workspace'] / '.write.lock'):
        events, latest = load_history(package)
        old = latest.get(assessment_id)
        if expected_revision != (old['revision'] if old else 0):
            raise ValueError('Stale browser revision; reload before editing')
        event = decision_event(package, events, row, expected_revision+1, status, grade, notes, evidence)
        # Preserve all revisions; atomic replacement avoids a partially appended last record after a crash.
        atomic_text(package['workspace'] / 'human_judgment_history.jsonl', jsonl_text(events + [event]))
    return event


def current_records(package):
    _, latest = load_history(package)
    rows = []
    for pair in package['rows']:
        event = latest.get(pair['assessment_id'])
        rows.append(dict(assessment_id=pair['assessment_id'], binding=binding(package, pair),
            status=event['status'] if event else 'PENDING', grade=event['grade'] if event else None,
            notes=event['notes'] if event else '', evidence=event['evidence'] if event else '',
            revision=event['revision'] if event else 0, provenance=event['provenance'] if event else None))
    return rows


def completeness(package, records):
    counts = Counter(r['status'] for r in records)
    by_query = []
    for qid in sorted({r['query_id'] for r in package['rows']}):
        subset = [r for r in records if r['binding']['query_id'] == qid]
        c = Counter(r['status'] for r in subset)
        by_query.append(dict(query_id=qid, total=len(subset), resolved=c['RESOLVED'],
                             pending=c['PENDING'], unresolved=c['UNRESOLVED']))
    return dict(total=len(records), resolved=counts['RESOLVED'], missing=counts['PENDING'],
        unresolved=counts['UNRESOLVED'], resolved_fraction=counts['RESOLVED']/len(records) if records else None,
        status='COMPLETE_RESOLVED' if records and counts['RESOLVED'] == len(records) else 'INCOMPLETE',
        by_query=by_query)
