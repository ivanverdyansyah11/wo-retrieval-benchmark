"""Cached V2 development diagnostics; no encoding, fitting or effectiveness metrics."""
import csv
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
from itertools import combinations
import json
import math
from pathlib import Path
import platform
import statistics
import sys
from time import perf_counter

from wo_retrieval import full_colab, versioned_dense
from wo_retrieval.hybrid.retrieval import fuse
from wo_retrieval.query_vectors.offline import retrievers
from wo_retrieval.retrieval.text import normalize

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'experiments/results/milestone_9a12_development_pilot'
KS = (1, 3, 5, 10, 20)


def read_jsonl(path):
    return [json.loads(s) for s in path.read_text(encoding='utf8').splitlines() if s.strip()]


def text_hash(text):
    return sha256(text.encode('utf8')).hexdigest()


def coverage(ranking, judgments, query_id, k):
    window = ranking[:k]
    counts = Counter(judgments.get((query_id, r.chunk_id)) for r in window)
    judged = sum(counts[g] for g in (0, 1, 2))
    returned = len(window)
    return dict(top_k=k, returned=returned, missing_slots=k-returned,
                grade_0=counts[0], grade_1=counts[1], grade_2=counts[2],
                judged=judged, unjudged=counts[None],
                judged_pct=100*judged/returned if returned else None,
                unjudged_pct=100*counts[None]/returned if returned else None,
                judged_pct_requested=100*judged/k,
                query_has_judged_relevant=any(q == query_id and g >= 1 for (q, _), g in judgments.items()),
                complete_returned_window=bool(returned) and counts[None] == 0)


def validate_ranking(results, method, universe, snapshot):
    ids = [r.chunk_id for r in results]
    if len(set(ids)) != len(ids) or (method in ('R3', 'R4') and set(ids) != set(universe)):
        raise ValueError('Duplicate/incomplete ranking')
    for rank, r in enumerate(results, 1):
        if (r.rank != rank or r.method_id != method or r.snapshot_id != snapshot
                or universe.get(r.chunk_id) != r.document_id or not math.isfinite(r.score)
                or (method in ('R1', 'R2') and r.score <= 0)):
            raise ValueError('Invalid ranking metadata/score')
    if results != sorted(results, key=lambda r: (-r.score, r.chunk_id)):
        raise ValueError('Non-deterministic tie order')


def verify_rrf(bm, dense, hybrid, breakdown):
    bm_ranks = {r.chunk_id: i for i, r in enumerate((r for r in bm if r.score > 0), 1)}
    dense_ranks = {r.chunk_id: r.rank for r in dense}
    expected = {c: (1/(60+b) if (b := bm_ranks.get(c)) else 0) + 1/(60+d)
                for c, d in dense_ranks.items()}
    assert [r.chunk_id for r in hybrid] == sorted(expected, key=lambda c: (-expected[c], c))
    for r, b in zip(hybrid, breakdown, strict=True):
        assert r.score == expected[r.chunk_id] == b['rrf_score']
        assert b['bm25_rank'] == bm_ranks.get(r.chunk_id)
        assert b['dense_rank'] == dense_ranks[r.chunk_id]
        assert b['dense_contribution'] == 1/(60+b['dense_rank'])
        assert b['bm25_contribution'] == (0 if b['bm25_rank'] is None else 1/(60+b['bm25_rank']))


def summarize(rows, scope, group):
    result = dict(scope=scope, group=group, method=rows[0]['method'], top_k=rows[0]['top_k'], query_count=len(rows))
    for key in ('returned', 'missing_slots', 'grade_0', 'grade_1', 'grade_2', 'judged', 'unjudged'):
        result[key] = sum(r[key] for r in rows)
    result['judged_pct'] = 100*result['judged']/result['returned'] if result['returned'] else None
    result['unjudged_pct'] = 100*result['unjudged']/result['returned'] if result['returned'] else None
    values = [r['judged_pct'] for r in rows if r['judged_pct'] is not None]
    result['macro_judged_pct'] = statistics.mean(values) if values else None
    result['empty_windows'] = sum(r['returned'] == 0 for r in rows)
    return result


def write_csv(path, rows):
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf8')


def verify_baseline(baseline):
    failures = [p for p, h in baseline.items() if not Path(p).is_file() or full_colab.file_hash(Path(p)) != h]
    if failures:
        raise ValueError(f'Protected artifact mutation: {failures}')
    return dict(status='PASS', files=len(baseline), hashes=baseline)


def run():
    if OUTPUT.exists():
        raise ValueError('Output target exists; refusing overwrite')
    baseline = json.loads(Path('D:/ModelCache/tmp/wo-m9a12/baseline.json').read_text())
    verify_baseline(baseline)
    components = full_colab.load_components(ROOT)
    bm, vectors, dense_manifest, config, _ = components
    binding, prep = versioned_dense.read_binding(ROOT)
    cfg, rows, stats = prep.bind_v2(ROOT)
    r1 = prep.verify_index(ROOT / binding['r1_index'], rows, cfg, prep.identity(ROOT, cfg, 'R1'), stats)
    assert rows == r1.rows == bm.rows and vectors.shape == (371, 1024)
    queries = read_jsonl(ROOT/'data/benchmark/development_queries_draft.jsonl')
    qmap = {q['query_id']: q for q in queries}
    assert len(qmap) == len(queries) == 18
    assert Counter(q['style'] for q in queries) == {'lexical_oriented': 6, 'semantic_paraphrase': 6, 'mixed_natural': 6}
    raw = {r['chunk_id']: r for r in read_jsonl(ROOT/'data/versions/v2_ai_corrected/chunks/chunks.jsonl')}
    rowmap = {r['chunk_id']: r for r in rows}
    universe = {r['chunk_id']: r['document_id'] for r in rows}
    qrels_path = ROOT/'data/versions/v2_ai_corrected/benchmark/development_qrels_ai_silver_v2.jsonl'
    judgments = {}
    for j in read_jsonl(qrels_path):
        pair = (j['query_id'], j['chunk_id'])
        assert pair not in judgments and pair[0] in qmap and pair[1] in raw
        assert type(j['grade']) is int and j['grade'] in (0, 1, 2) and j['human_validated'] is False
        assert j['query_text'] == qmap[pair[0]]['text'] and j['query_text_sha256'] == text_hash(j['query_text'])
        assert j['chunk_text_sha256'] == text_hash(raw[pair[1]]['text'])
        assert j['serialized_text_sha256'] == rowmap[pair[1]]['text_sha256']
        assert j['document_id'] == universe[pair[1]]
        assert j['snapshot_id'] == config['snapshot']['id'] and j['snapshot_fingerprint'] == config['snapshot']['aggregate_fingerprint']
        judgments[pair] = j['grade']
    assert Counter(judgments.values()) == {0: 621, 1: 32, 2: 31} and len(judgments) == 684
    OUTPUT.mkdir(parents=True)
    manifest = dict(completion_status='INCOMPLETE', started_at=datetime.now(timezone.utc).isoformat(),
                    research_status='NOT FINAL EVALUATION', snapshot=config['snapshot'],
                    configuration=config, query_count=18, corpus_chunks=371,
                    local_query_encoding='NOT RUN', effectiveness_metrics='NOT COMPUTED: partial, nonhuman silver qrels',
                    timing_protocol='One warm-up and three measured full-ranking calls per component/query; no encoding or index loading.',
                    environment={'python':sys.version, 'platform':platform.platform(),
                                 'dependencies':{p:version(p) for p in ('numpy','scipy','scikit-learn','rank-bm25','psutil')}},
                    inputs={'qrels_sha256':full_colab.file_hash(qrels_path),
                            'query_sha256':full_colab.file_hash(ROOT/'data/benchmark/development_queries_draft.jsonl'),
                            'dense_manifest_sha256':full_colab.file_hash(ROOT/'experiments/indexes/v2_ai_corrected/R3/manifest.json')},
                    driver_sha256=full_colab.file_hash(Path(__file__)))
    import psutil
    manifest['environment']['resources'] = {'logical_cpus':psutil.cpu_count(), 'physical_cpus':psutil.cpu_count(logical=False),
        'ram_total_bytes':psutil.virtual_memory().total, 'ram_available_bytes':psutil.virtual_memory().available}
    write_json(OUTPUT/'run_manifest.json', manifest)
    rankings, audits, top10, timings, overlaps, examples = [], [], [], [], [], []
    display = ['# Development pilot top-10', '', 'NOT FINAL EVALUATION. UNJUDGED is unknown, not grade 0.', '']
    for q in queries:
        qid, text = q['query_id'], q['text']
        dense, hybrid = retrievers(components, ROOT/'experiments/indexes/v2_ai_corrected/R3/query_vectors'/qid, qid, text)
        results = {}
        for method, scorer in (('R1',r1),('R2',bm),('R3',dense)):
            results[method] = scorer.retrieve(text, 371)
            for repeat in range(3):
                start = perf_counter(); again = scorer.retrieve(text,371); elapsed = perf_counter()-start
                assert again == results[method]
                timings.append(dict(query_id=qid, component=method, repeat=repeat+1, seconds=elapsed))
        results['R4'], breakdown = fuse(results['R2'], results['R3'], rows, config['snapshot']['id'], 371)
        for repeat in range(3):
            start = perf_counter(); again, detail = fuse(results['R2'], results['R3'], rows, config['snapshot']['id'],371); elapsed=perf_counter()-start
            assert again == results['R4'] and detail == breakdown
            timings.append(dict(query_id=qid, component='RRF', repeat=repeat+1, seconds=elapsed))
        live, details, parts = hybrid.retrieve_with_diagnostics(text,371)
        assert live == results['R4'] and details == breakdown and parts == {'R2':results['R2'],'R3':results['R3']}
        verify_rrf(results['R2'],results['R3'],live,details)
        display += [f'## {qid} — {q["style"]}', '', text, '']
        for method, ranking in results.items():
            validate_ranking(ranking, method, universe, config['snapshot']['id'])
            rankings.append(dict(query_id=qid, query_text=text, query_text_sha256=text_hash(text), normalized_text_sha256=text_hash(normalize(text)),
                style=q['style'], category=q['primary_category'], method=method,
                results=[{**asdict(r),'silver_grade':judgments.get((qid,r.chunk_id)),
                          'judgment_status':'UNJUDGED' if (qid,r.chunk_id) not in judgments else 'AI_SILVER_PROVISIONAL'} for r in ranking],
                rrf_breakdown=breakdown if method == 'R4' else None))
            for k in KS:
                audits.append(dict(query_id=qid, method=method, style=q['style'], category=q['primary_category'], **coverage(ranking,judgments,qid,k)))
            display += [f'### {method}', '', '| Rank | Chunk | Score | Silver grade |', '|---:|---|---:|---|']
            for r in ranking[:10]:
                grade = judgments.get((qid,r.chunk_id),'UNJUDGED')
                top10.append(dict(query_id=qid, method=method, rank=r.rank, chunk_id=r.chunk_id,
                    document_id=r.document_id, score=r.score, silver_grade=grade, title=raw[r.chunk_id]['title'], heading=raw[r.chunk_id]['heading']))
                display.append(f'| {r.rank} | {r.chunk_id} | {r.score:.9g} | {grade} |')
            display.append('')
        for a,b in combinations(results,2):
            sa,sb = ({r.chunk_id for r in results[m][:10]} for m in (a,b))
            overlaps.append(dict(query_id=qid, style=q['style'], method_a=a, method_b=b,
                intersection=len(sa&sb), union=len(sa|sb), jaccard=len(sa&sb)/len(sa|sb) if sa|sb else None))
        ranks = {m:{r.chunk_id:r.rank for r in rr} for m,rr in results.items()}
        candidates = dict.fromkeys([results[m][0].chunk_id for m in results if results[m]])
        promoted = sorted(results['R4'][:10], key=lambda r: ranks['R3'][r.chunk_id]-r.rank, reverse=True)[0]
        candidates[promoted.chunk_id] = None
        demoted = sorted(results['R3'][:10], key=lambda r:ranks['R4'][r.chunk_id]-r.rank, reverse=True)[0]
        candidates[demoted.chunk_id] = None
        for c in candidates:
            examples.append(dict(query_id=qid, query_text=text, style=q['style'], chunk_id=c,
                ranks={m:r.get(c) for m,r in ranks.items()}, silver_grade=judgments.get((qid,c)),
                judgment_status='UNJUDGED' if (qid,c) not in judgments else 'AI_SILVER_PROVISIONAL',
                title=raw[c]['title'], heading=raw[c]['heading'], source_locator=raw[c]['source_locator'],
                raw_chunk_excerpt=raw[c]['text'][:800], excerpt_truncated=len(raw[c]['text'])>800,
                note='Ranking observation only; no new relevance judgment'))
        print(qid+' R1/R2/R3/R4 PASS',flush=True)
    summaries = []
    for scope, field in (('overall',None),('style','style'),('category','category')):
        groups = ['all'] if field is None else sorted({r[field] for r in audits})
        for group in groups:
            for method in ('R1','R2','R3','R4'):
                for k in KS:
                    subset=[r for r in audits if r['method']==method and r['top_k']==k and (field is None or r[field]==group)]
                    summaries.append(summarize(subset,scope,group))
    for name, content in (('rankings.jsonl',rankings),('diagnostic_examples.jsonl',examples)):
        (OUTPUT/name).write_text(''.join(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n' for r in content),encoding='utf8')
    for name, content in (('coverage.csv',audits),('coverage_summary.csv',summaries),('top10.csv',top10),('timing.csv',timings),('overlap.csv',overlaps)):
        write_csv(OUTPUT/name,content)
    (OUTPUT/'top10.md').write_text('\n'.join(display)+'\n',encoding='utf8')
    write_json(OUTPUT/'protected_integrity.json',verify_baseline(baseline))
    assert 'torch' not in sys.modules
    manifest.update(completion_status='COMPLETE', completed_at=datetime.now(timezone.utc).isoformat(),
        checks={'same_inputs': 'PASS','determinism':'PASS','rrf_independent_math':'PASS','ranking_metadata':'PASS','protected_files':len(baseline),'torch_imported':False},
        counts={'rankings':len(rankings),'coverage_rows':len(audits),'top10_rows':len(top10),'diagnostic_examples':len(examples)},
        outputs={p.name:full_colab.file_hash(p) for p in sorted(OUTPUT.iterdir()) if p.name!='run_manifest.json'})
    write_json(OUTPUT/'run_manifest.json',manifest)
    print(json.dumps({'status':'COMPLETE','output':str(OUTPUT),'checks':manifest['checks']},indent=2))


if __name__ == '__main__':
    run()
