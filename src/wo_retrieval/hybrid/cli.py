"""Audit R4 readiness or query existing R2/R3 indexes; no build command."""

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from time import perf_counter
import traceback

from wo_retrieval.dense.index import atomic_json
from wo_retrieval.dense.resources import Monitor, gate, gpu_resource, resource, unsafe
from wo_retrieval.retrieval.lexical import read_protocol, verify_snapshot
from wo_retrieval.retrieval.text import normalize
from .retrieval import fuse, ready


def run(root, command, query=None, top_k=5, approved_low_memory=False, approval_note=None):
    if type(top_k) is not int or top_k <= 0:
        raise ValueError('top_k must be a positive integer')
    if command not in ('audit', 'retrieve', 'smoke'):
        raise ValueError('Unsupported R4 command')
    if approved_low_memory and (not isinstance(approval_note, str) or not approval_note.strip()):
        raise ValueError('Explicit human approval note is required for low-memory mode')
    if command == 'retrieve' and not normalize(query):
        return {'results': [], 'diagnostics': []}
    root = root.resolve()
    config = read_protocol(root)
    policy = dict(config['hardware'])
    if approved_low_memory:
        policy.update(stop_available_ram_mib=2048, stop_sustained_seconds=0)
    directory = Path(config['R3']['cache']['root']) / 'runs' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-R4')
    directory.mkdir(parents=True)
    path = directory / 'run.json'
    report = {'method_id': 'R4', 'command': command, 'status': 'RUNNING', 'loading': 'NOT RUN',
              'smoke': 'NOT RUN', 'preflight': resource(), 'gpu_preflight': gpu_resource(),
              'approved_low_memory': approved_low_memory, 'approval_note': approval_note,
              'model_loading_gate_gib': 5 if approved_low_memory else policy['recommended_available_ram_gib'],
              'effective_resource_policy': policy}
    encoder = None
    monitor = Monitor(policy, directory)
    try:
        with monitor:
            hybrid, encoder, metadata = ready(root)
            report['readiness'] = metadata
            if command == 'audit':
                report['status'] = 'PASS_READINESS_WEIGHTS_NOT_LOADED'
                return report
            if command == 'smoke':
                queries = [json.loads(line) for line in (root / 'data/benchmark/development_queries_draft.jsonl').read_text(encoding='utf-8').splitlines()]
                selected = [next(q for q in queries if q['style'] == style) for style in config['queries']['styles']]
                report['selection'] = 'first existing query per style; independent of ranking'
                if approved_low_memory and [q['query_id'] for q in selected] != ['WO-DEV-001', 'WO-DEV-007', 'WO-DEV-013']:
                    raise ValueError('Controlled smoke query IDs differ from approval')
            else:
                selected = [{'text': query, 'query_id': None}]
            for item in selected:
                encoder.tokens(item['text'])
            report['pre_model_loading'] = resource()
            report['gpu_pre_model_loading'] = gpu_resource()
            atomic_json(path, report)
            gate(report['pre_model_loading'], report['gpu_pre_model_loading'], policy, approved_low_memory)
            report['loading'] = 'RUNNING'
            encoder.load(Path(config['R3']['cache']['root']) / 'gpu-inference.lock')
            report['loading'] = 'PASS'
            report['queries'] = []
            for item in selected:
                if unsafe(resource(), policy):
                    raise RuntimeError('Critical memory; no query inference')
                started = perf_counter()
                results, diagnostics, components = hybrid.retrieve_with_diagnostics(item['text'], top_k)
                elapsed = perf_counter() - started
                if unsafe(resource(), policy):
                    raise RuntimeError('Memory safety limit after query inference')
                repeated, repeated_diagnostics = fuse(components['R2'], components['R3'], hybrid.dense.rows,
                                                       config['snapshot']['id'], top_k)
                if results != repeated or diagnostics != repeated_diagnostics:
                    raise ValueError('Nondeterministic fusion for identical component rankings')
                if len(results) != min(top_k, len(hybrid.dense.rows)):
                    raise ValueError('Missing full Dense candidates')
                by_id = {row['chunk_id']: row for row in hybrid.dense.rows}
                # Independently recompute from component ID positions, not diagnostics.
                bm_ids = [r.chunk_id for r in components['R2'] if r.score > 0]
                dense_ids = [r.chunk_id for r in components['R3']]
                for result in results:
                    expected = 1 / (60 + dense_ids.index(result.chunk_id) + 1)
                    if result.chunk_id in bm_ids:
                        expected += 1 / (60 + bm_ids.index(result.chunk_id) + 1)
                    if result.score != expected or result.document_id != by_id[result.chunk_id]['document_id']:
                        raise ValueError('Independent formula/source verification failed')
                report['queries'].append({'query_id': item['query_id'], 'text': item['text'],
                    'query_status': item.get('validation_status'), 'pipeline_seconds_excluding_loading': elapsed,
                    'component_counts': {k: len(v) for k, v in components.items()},
                    'component_top5': {k: [asdict(r) for r in v[:5]] for k, v in components.items()},
                    'results': [asdict(r) for r in results], 'diagnostics': diagnostics,
                    'independent_formula_check': 'PASS', 'repeat_fusion_same_rankings': 'PASS'})
            report['model_metrics'] = encoder.metrics()
            report['smoke'] = 'PASS' if command == 'smoke' else 'NOT RUN'
            report['status'] = 'PASS'
            verify_snapshot(root, config)
            return report
    except BaseException as error:
        report['status'] = 'STOPPED'
        report['error'] = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
        if report['loading'] == 'RUNNING':
            report['loading'] = 'FAIL'
        raise
    finally:
        # Audit never imports torch for cleanup or loads neural weights.
        if encoder is not None and (encoder.model is not None or encoder.lock is not None):
            encoder.close()
        report['resource_monitor'] = monitor.summary
        report['resource_after_cleanup'] = resource()
        report['effectiveness_evaluation'] = 'NOT RUN'
        report['evidence_path'] = str(path)
        atomic_json(path, report)
        print(json.dumps({'event': 'R4_run_evidence', 'path': str(path), 'status': report['status']}), file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['audit', 'retrieve', 'smoke'])
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--query')
    parser.add_argument('--top-k', type=int, default=5)
    parser.add_argument('--approved-low-memory', action='store_true', help='Only with explicit human approval; 5 GiB loading gate and immediate 2 GiB RAM stop')
    parser.add_argument('--approval-note', help='Recorded human authorization reference; required with --approved-low-memory')
    args = parser.parse_args()
    if args.command == 'retrieve' and args.query is None:
        parser.error('--query is required')
    if args.approved_low_memory and not (args.approval_note and args.approval_note.strip()):
        parser.error('--approval-note is required with --approved-low-memory')
    try:
        print(json.dumps(run(args.root, args.command, args.query, args.top_k,
                             args.approved_low_memory, args.approval_note), ensure_ascii=False, indent=2, allow_nan=False))
    except (ValueError, OSError, KeyError, TypeError, RuntimeError) as error:
        parser.exit(1, f'Hybrid retrieval stopped: {error}\n')


if __name__ == '__main__':
    main()
