"""Controlled researcher review import; immutable input, preserved history, atomic batch."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import shutil

from . import human_judgments as h

FIELDS = ('status', 'grade', 'notes', 'evidence')


def preflight(package, source, audit_path):
    source, audit_path = Path(source).resolve(), Path(audit_path).resolve()
    audit = h.read_json(audit_path); rows = h.read_jsonl(source)
    manifest = package['manifest']
    for key, target in [('expected_package_id','package_id'), ('expected_input_sha256','input_sha256'),
                        ('snapshot_id','snapshot_id'), ('snapshot_fingerprint','snapshot_fingerprint')]:
        if audit[key] != manifest[target]:
            raise ValueError('Import audit/package mismatch: ' + key)
    if h.file_hash(source) != audit['input_jsonl_sha256']:
        raise ValueError('Import checksum mismatch')
    incoming = {key[0]: row for key, row in h.unique(rows, ('assessment_id',)).items()}
    h.unique([r['binding'] for r in rows], ('query_id','chunk_id'))
    if set(incoming) != set(package['pairs']) or len(rows) != audit['input_record_count']:
        raise ValueError('Missing/extra import identifiers')
    for row in rows:
        pair = package['pairs'][row['assessment_id']]
        if set(row) != {'assessment_id','binding',*FIELDS} or row['binding'] != h.binding(package, pair):
            raise ValueError('Noncanonical import fields/binding')
        h.validate_decision(*(row[k] for k in FIELDS), pair)
    counts = dict(Counter(str(r['grade']) for r in rows))
    if (counts != audit['grade_counts'] or dict(Counter(r['status'] for r in rows)) != audit['status_counts']
            or sum(bool(r['notes']) for r in rows) != audit['notes_count']
            or sum(bool(r['evidence']) for r in rows) != audit['evidence_quote_count']
            or audit['binding_and_evidence_verified'] is not True
            or any(r['status'] != 'RESOLVED' for r in rows)):
        raise ValueError('Import counts/schema disagree with audit')
    queries = sorted({r['binding']['query_id'] for r in rows if r['grade'] >= 1})
    if set(queries) != {q['query_id'] for q in manifest['query_metadata']}:
        raise ValueError('Some queries lack pooled relevance; review without forcing labels')
    events, latest = h.load_history(package)
    missing, identical, conflicts = [], [], []
    for aid, row in sorted(incoming.items()):
        if aid not in latest:
            missing.append(aid); continue
        differences = [k for k in FIELDS if latest[aid][k] != row[k]]
        if differences:
            conflicts.append(dict(assessment_id=aid, different_fields=differences,
                existing={k:latest[aid][k] for k in differences}, incoming={k:row[k] for k in differences}))
        else:
            identical.append(aid)
    locked = any((package['workspace']/p).exists() for p in ('.server.lock','.write.lock'))
    plan = dict(status='CONFLICT' if conflicts else 'BLOCKED_WORKSPACE_ACTIVE' if locked else 'PASS',
        package_id=manifest['package_id'], input_sha256=manifest['input_sha256'],
        annotation_manifest_sha256=h.file_hash(package['workspace']/'annotation_manifest.json'),
        history_sha256=h.file_hash(package['workspace']/'human_judgment_history.jsonl'),
        source_path=str(source), source_sha256=h.file_hash(source), audit_path=str(audit_path), audit_sha256=h.file_hash(audit_path),
        source_count=len(rows), grade_distribution=counts, queries_with_relevance=queries,
        history_events=len(events), imported=0, to_import=missing, skipped=identical, conflicts=conflicts)
    return plan, incoming


def apply_import(package, source, audit_path, approved_plan, out):
    fresh, incoming = preflight(package, source, audit_path)
    if fresh != approved_plan or fresh['status'] != 'PASS':
        raise ValueError('Dry-run stale, blocked or conflicting; run dry-run again')
    out = Path(out).resolve()
    if out.exists() or out.is_relative_to(package['workspace']):
        raise ValueError('Use a new receipt/backup directory outside annotation workspace')
    if not fresh['to_import']:
        out.mkdir(parents=True)
        receipt = {**fresh, 'imported':0, 'import_status':'SKIPPED_IDENTICAL', 'backup':None}
        h.write_json(out/'import_receipt.json', receipt)
        return receipt
    # The same server lock prevents a new annotation server from opening during import.
    with h.exclusive(package['workspace']/'.server.lock'), h.exclusive(package['workspace']/'.write.lock'):
        h.load_package(package['root'], package['workspace'])
        if h.file_hash(package['workspace']/'human_judgment_history.jsonl') != fresh['history_sha256']:
            raise ValueError('History changed after dry-run')
        if h.file_hash(source) != fresh['source_sha256'] or h.file_hash(audit_path) != fresh['audit_sha256']:
            raise ValueError('Import source changed after dry-run')
        out.mkdir(parents=True)
        backup = out/'workspace_backup'
        shutil.copytree(package['workspace'], backup, ignore=shutil.ignore_patterns('.server.lock','.write.lock'))
        backups = {str(p.relative_to(backup)):h.file_hash(p) for p in backup.rglob('*') if p.is_file()}
        for name, checksum in backups.items():
            if h.file_hash(package['workspace']/name) != checksum:
                raise ValueError('Workspace changed during backup')
        h.write_json(out/'backup_manifest.json', dict(files=backups, runtime_locks_excluded=True))
        history = package['workspace']/'human_judgment_history.jsonl'
        original = history.read_bytes(); events, latest = h.load_history(package)
        timestamp = datetime.now(timezone.utc).isoformat()
        origin = {k:fresh[k] for k in ('source_path','source_sha256','audit_path','audit_sha256')}
        origin.update(imported_at_utc=timestamp, original_assessed_at_utc=None)
        staged = list(events)
        for aid in fresh['to_import']:
            row = incoming[aid]
            staged.append(h.decision_event(package, staged, package['pairs'][aid], 1,
                *(row[k] for k in FIELDS), import_source=origin))
        h.load_history(package, staged)
        published = False
        try:
            # One replacement publishes the entire batch; no partial progress becomes visible.
            h.atomic_text(history, h.jsonl_text(staged)); published = True
            verified, decisions = h.load_history(package)
            if verified != staged or any(any(decisions[aid][k] != row[k] for k in FIELDS) for aid,row in incoming.items()):
                raise ValueError('Post-import verification failed')
            receipt = {**fresh, 'imported':len(fresh['to_import']), 'import_status':'IMPORTED',
                'imported_at_utc':timestamp, 'backup':str(backup), 'history_sha256_after':h.file_hash(history),
                'preserved_events':len(events), 'events_after':len(staged),
                'label':h.LABEL, 'assessor_id':package['manifest']['assessor_id'],
                'expert_validated':False, 'independently_validated':False}
            h.write_json(out/'import_receipt.json', receipt)
        except BaseException:
            if published:
                h.atomic_text(history, original.decode('utf-8'))
                if history.read_bytes() != original:
                    raise RuntimeError('Rollback verification failed; restore history from verified backup')
            raise
    return receipt
