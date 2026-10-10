"""Read-only verification of frozen development artifacts, using cached vectors only."""
import argparse
from collections import Counter
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))


def verify(root, query_id=None):
    from wo_retrieval import human_judgments as h, human_metrics as metrics
    from wo_retrieval.pipeline import audit, load_config
    from wo_retrieval.dense.index import load_vectors
    from wo_retrieval.query_vectors.offline import retrievers
    from wo_retrieval.retrieval.lexical import file_hash, digest

    package = h.load_package(root, root / h.WORKSPACE)
    sources = h.audit_sources(root)
    records = h.current_records(package)
    events, latest = h.load_history(package)
    completeness = h.completeness(package, records)
    if completeness['status'] != 'COMPLETE_RESOLVED':
        raise ValueError('Development judgments are incomplete')
    audits = {}
    for name in ('pilot.toml', 'pilot_v2.toml'):
        _, report = audit(root, load_config(root, root / 'experiments/configs' / name))
        if report['errors']:
            raise ValueError('Corpus audit failed: ' + '; '.join(report['errors']))
        audits[name] = {k: report[k] for k in ('source_documents', 'formats', 'errors', 'notices')}

    # Frozen package hashes anchor the manifests before reusing their stored identity.
    binding = h.read_json(root / 'experiments/configs/dense_v2_binding.json')
    builder = root / binding['preparation_script']
    if file_hash(builder) != binding['preparation_script_sha256']:
        raise ValueError('Preparation code checksum mismatch')
    spec = importlib.util.spec_from_file_location('verified_v2_preparation', builder)
    preparation = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(preparation)
    config, rows, statistics = preparation.bind_v2(root)
    lexical = {method: preparation.verify_index(root / binding[key], rows, config,
                preparation.identity(root, config, method), statistics)
               for method, key in (('R1', 'r1_index'), ('R2', 'r2_index'))}
    directory = root / binding['r3_index']
    manifest = h.read_json(directory / 'manifest.json')
    mapping = h.read_json(directory / 'rows.json')
    identity = manifest['identity']
    if [(r['chunk_id'], r['document_id'], r['text_sha256']) for r in rows] != [
            (r['chunk_id'], r['document_id'], r['serialized_text_sha256']) for r in mapping]:
        raise ValueError('Dense serialization mapping mismatch')
    if identity['config_fingerprint'] != digest({k: config[k] for k in ('R3', 'serialization', 'ranking')}):
        raise ValueError('Dense configuration mismatch')
    vectors, manifest = load_vectors(directory, identity, mapping)
    components = lexical['R2'], vectors, manifest, config, None
    examples = []
    fields = tuple(asdict(lexical['R1'].retrieve(sources['rankings'][0]['query_text'], 1)[0]))
    for run in sources['rankings']:
        qid, text, method = run['query_id'], run['query_text'], run['method']
        if method in lexical:
            actual = lexical[method].retrieve(text, len(rows))
        else:
            dense, hybrid = retrievers(components, directory / 'query_vectors' / qid, qid, text)
            actual = {'R3': dense, 'R4': hybrid}[method].retrieve(text, len(rows))
        if [asdict(r) for r in actual] != [{k: r[k] for k in fields} for r in run['results']]:
            raise ValueError('Exact saved ranking parity failed: ' + qid + '/' + method)
        if qid == query_id:
            examples.append(dict(query_id=qid, query_text=text, method=method,
                                 results=[asdict(r) for r in actual[:10]]))
    if query_id and not examples:
        raise ValueError('Only existing development query IDs are accepted')

    result = metrics.evaluate(package, records, sources['rankings'])
    saved = h.read_json(root / 'experiments/results/human_development_evaluation/milestone_9a18_20261010/evaluation.json')
    if result != saved:
        raise ValueError('Saved development metrics/provenance parity failed')
    if 'torch' in sys.modules:
        raise ValueError('Unexpected neural runtime import')
    return dict(status='PASS', root=str(root), corpus_audits=audits, chunks=len(rows),
                queries=len(package['manifest']['query_metadata']), exact_rankings=len(sources['rankings']),
                history_events=len(events), latest_records=len(latest), completeness=completeness,
                grade_counts=dict(Counter(str(r['grade']) for r in records)),
                frozen_source_files=len(package['manifest']['frozen_source_hashes']),
                metrics_exact_saved_parity=True, torch_imported=False, examples=examples)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--query-id', help='Display Top-10 for one existing development query')
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.root.resolve(), args.query_id), ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError) as error:
        parser.exit(2, str(error) + '\n')


if __name__ == '__main__':
    main()
