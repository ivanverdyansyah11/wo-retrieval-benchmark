"""Prepare a blinded pool from saved rankings; never infer relevance or rerun retrieval."""
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import sys

from run_development_pilot import (ROOT, read_jsonl, text_hash, validate_ranking,
                                  coverage, write_csv, write_json, verify_baseline)
from wo_retrieval import full_colab
from wo_retrieval.retrieval.lexical import RetrievalResult

OUTPUT = ROOT/'experiments/results/milestone_9a13_judgment_pool'
PREVIOUS = ROOT/'experiments/results/milestone_9a12_development_pilot'
SEED = 42
BLIND_FIELDS = {'assessment_id', 'query_id', 'chunk_id', 'query_text', 'serialized_chunk_text',
                'source_snapshot_id', 'source_snapshot_fingerprint', 'document_id',
                'query_text_sha256', 'serialized_text_sha256', 'assessment_status',
                'relevance_grade', 'evidence', 'rationale', 'ambiguity_flag',
                'uncertainty_notes', 'context_opened', 'assessor_provenance'}


def build_pool(rankings):
    pool, seen = {}, set()
    for run in rankings:
        key = run['query_id'], run['method']
        if key in seen or len({r['chunk_id'] for r in run['results']}) != len(run['results']):
            raise ValueError('Duplicate run or candidate')
        seen.add(key)
        for result in run['results'][:20]:
            pair = run['query_id'], result['chunk_id']
            pool.setdefault(pair, []).append({'method':run['method'], 'rank':result['rank'], 'score':result['score']})
    return {pair:sorted(origins,key=lambda x:x['method']) for pair,origins in sorted(pool.items())}


def blind_ledger(pool, queries, rows, snapshot_id, fingerprint):
    records = []
    for i, (qid,cid) in enumerate(sorted(pool),1):
        query, chunk = queries[qid]['text'], rows[cid]['text']
        records.append(dict(assessment_id=f'WO-POOL-V2-{i:04d}', query_id=qid, chunk_id=cid,
            query_text=query, serialized_chunk_text=chunk, source_snapshot_id=snapshot_id,
            source_snapshot_fingerprint=fingerprint, document_id=rows[cid]['document_id'],
            query_text_sha256=text_hash(query), serialized_text_sha256=text_hash(chunk),
            assessment_status='PENDING', relevance_grade=None, evidence=[], rationale=None,
            ambiguity_flag=None, uncertainty_notes=None, context_opened=[], assessor_provenance=None))
    random.Random(SEED).shuffle(records)
    return records


def select_pilot(ledger, queries):
    # Select before labels: every query once, then fill each style to ten in shuffled order.
    selected, seen, counts = set(), set(), Counter()
    for r in ledger:
        if r['query_id'] not in seen:
            selected.add(r['assessment_id']); seen.add(r['query_id'])
            counts[queries[r['query_id']]['style']] += 1
    for r in ledger:
        style = queries[r['query_id']]['style']
        if counts[style] < 10 and r['assessment_id'] not in selected:
            selected.add(r['assessment_id']); counts[style] += 1
    if len(selected) != 30 or set(counts.values()) != {10}:
        raise ValueError('Insufficient pilot strata')
    return [r for r in ledger if r['assessment_id'] in selected]


def validate_assessment(r):
    if set(r) != BLIND_FIELDS:
        raise ValueError('Blind field allowlist violated')
    if (text_hash(r['query_text']) != r['query_text_sha256'] or
            text_hash(r['serialized_chunk_text']) != r['serialized_text_sha256']):
        raise ValueError('Text hash mismatch')
    status, grade = r['assessment_status'], r['relevance_grade']
    if status == 'PENDING':
        if any(r[k] is not None for k in ('relevance_grade','rationale','ambiguity_flag','uncertainty_notes','assessor_provenance')) or r['evidence'] or r['context_opened']:
            raise ValueError('Pending record must not contain judgments')
        return
    if status not in ('ASSESSED','UNRESOLVED'):
        raise ValueError('Invalid assessment status')
    if status == 'UNRESOLVED':
        if grade is not None or r['ambiguity_flag'] is not True:
            raise ValueError('Unresolved is never grade 0')
    elif type(grade) is not int or grade not in (0,1,2) or type(r['ambiguity_flag']) is not bool:
        raise ValueError('Invalid assessed grade/ambiguity')
    if any(not isinstance(r[k],str) or not r[k].strip() for k in ('rationale','uncertainty_notes')):
        raise ValueError('Missing rationale/uncertainty')
    if (not isinstance(r['evidence'],list) or (status == 'ASSESSED' and not r['evidence']) or
            any(not isinstance(e,str) or not e.strip() or e not in r['serialized_chunk_text'] for e in r['evidence'])):
        raise ValueError('Evidence must quote the exact assessed chunk')
    if not isinstance(r['context_opened'],list):
        raise ValueError('Additional context must be recorded')
    provenance=r['assessor_provenance']
    if (not isinstance(provenance,dict) or provenance.get('label')!='AI SILVER — PROVISIONAL'
            or provenance.get('human_validated') is not False or
            any(not provenance.get(k) for k in ('model_id','model_revision','assessed_at','rubric_version','session_id'))):
        raise ValueError('Missing actual assessor provenance')


def run():
    if OUTPUT.exists():
        raise ValueError('Output exists; refusing overwrite')
    baseline=json.loads(Path('D:/ModelCache/tmp/wo-m9a13/baseline.json').read_text(encoding='utf8'))
    verify_baseline(baseline)
    previous=json.loads((PREVIOUS/'run_manifest.json').read_text(encoding='utf8'))
    if previous['completion_status']!='COMPLETE':
        raise ValueError('Previous pilot incomplete')
    for name,h in previous['outputs'].items():
        if full_colab.file_hash(PREVIOUS/name)!=h:
            raise ValueError(f'Previous pilot output mismatch: {name}')
    if full_colab.file_hash(ROOT/'scripts/run_development_pilot.py')!=previous['driver_sha256']:
        raise ValueError('Previous driver changed')
    bm, _, manifest, config, _ = full_colab.load_components(ROOT)
    if config != previous['configuration']:
        raise ValueError('Configuration mismatch')
    qpath=ROOT/'data/benchmark/development_queries_draft.jsonl'
    jpath=ROOT/'data/versions/v2_ai_corrected/benchmark/development_qrels_ai_silver_v2.jsonl'
    for path,key in ((qpath,'query_sha256'),(jpath,'qrels_sha256'),
                     (ROOT/'experiments/indexes/v2_ai_corrected/R3/manifest.json','dense_manifest_sha256')):
        if full_colab.file_hash(path)!=previous['inputs'][key]:
            raise ValueError(f'Previous input changed: {key}')
    queries=read_jsonl(qpath); qmap={q['query_id']:q for q in queries}
    rows={r['chunk_id']:r for r in bm.rows}; universe={c:r['document_id'] for c,r in rows.items()}
    snapshot=config['snapshot']; judgments={}
    for j in read_jsonl(jpath):
        pair=j['query_id'],j['chunk_id']
        if pair in judgments or pair[0] not in qmap or pair[1] not in rows:
            raise ValueError('Invalid existing judgment pair')
        if (type(j['grade']) is not int or j['grade'] not in (0,1,2) or j['human_validated'] is not False
                or j['query_text']!=qmap[pair[0]]['text'] or j['query_text_sha256']!=text_hash(j['query_text'])
                or j['serialized_text_sha256']!=rows[pair[1]]['text_sha256'] or j['document_id']!=universe[pair[1]]
                or j['snapshot_id']!=snapshot['id'] or j['snapshot_fingerprint']!=snapshot['aggregate_fingerprint']):
            raise ValueError('Existing judgment binding mismatch')
        judgments[pair]=j['grade']
    if len(judgments)!=684 or Counter(judgments.values())!={0:621,1:32,2:31}:
        raise ValueError('Existing qrels counts changed')
    rankings=read_jsonl(PREVIOUS/'rankings.jsonl')
    if {(r['query_id'],r['method']) for r in rankings}!={(q,m) for q in qmap for m in ('R1','R2','R3','R4')} or len(rankings)!=72:
        raise ValueError('Missing/extra method-query runs')
    result_objects={}
    for r in rankings:
        if (r['query_text']!=qmap[r['query_id']]['text'] or r['query_text_sha256']!=text_hash(r['query_text'])
                or r['style']!=qmap[r['query_id']]['style']):
            raise ValueError('Ranking query binding mismatch')
        objects=[RetrievalResult(**{k:v for k,v in x.items() if k in
            ('method_id','chunk_id','document_id','rank','score','snapshot_id')}) for x in r['results']]
        validate_ranking(objects,r['method'],universe,snapshot['id'])
        for x in r['results']:
            if x['silver_grade']!=judgments.get((r['query_id'],x['chunk_id'])):
                raise ValueError('Saved ranking judgment mismatch')
        result_objects[r['query_id'],r['method']]=objects
    pool=build_pool(rankings)
    if len(pool)!=654 or sum(pair in judgments for pair in pool)!=90:
        raise ValueError('Unexpected top-20 pool; stop before publication')
    ledger=blind_ledger(pool,qmap,rows,snapshot['id'],snapshot['aggregate_fingerprint'])
    if ledger!=blind_ledger(build_pool(list(reversed(rankings))),qmap,rows,snapshot['id'],snapshot['aggregate_fingerprint']):
        raise ValueError('Non-deterministic reconstruction')
    pilot=select_pilot(ledger,qmap)
    for r in ledger:validate_assessment(r)
    origins=[dict(assessment_id=r['assessment_id'],query_id=r['query_id'],chunk_id=r['chunk_id'],
        style=qmap[r['query_id']]['style'], category=qmap[r['query_id']]['primary_category'],
        source_candidates=pool[r['query_id'],r['chunk_id']],
        existing_grade=judgments.get((r['query_id'],r['chunk_id'])),
        existing_status='AI_SILVER_PROVISIONAL' if (r['query_id'],r['chunk_id']) in judgments else 'UNJUDGED',
        in_pilot=r in pilot) for r in sorted(ledger,key=lambda r:r['assessment_id'])]
    summary=[]
    for q in queries:
        candidates=[r for r in origins if r['query_id']==q['query_id']]
        grades=Counter(r['existing_grade'] for r in candidates)
        summary.append(dict(query_id=q['query_id'],style=q['style'],category=q['primary_category'],
            pooled=len(candidates),existing_judged=sum(grades[g] for g in (0,1,2)),unjudged=grades[None],
            grade_0=grades[0],grade_1=grades[1],grade_2=grades[2],
            multiple_methods=sum(len(r['source_candidates'])>1 for r in candidates),
            **{f'{m}_candidates':sum(any(x['method']==m for x in r['source_candidates']) for r in candidates) for m in ('R1','R2','R3','R4')}))
    audit=[]
    for q in queries:
        for method in ('R1','R2','R3','R4'):
            for k in (1,3,5,10,20):
                audit.append(dict(query_id=q['query_id'],method=method,style=q['style'],
                    **coverage(result_objects[q['query_id'],method],judgments,q['query_id'],k)))
    OUTPUT.mkdir(parents=True)
    run_manifest=dict(completion_status='INCOMPLETE',assessment_status='PENDING',
        created_at=datetime.now(timezone.utc).isoformat(),snapshot=snapshot,
        authorization='User attachment c5cac422-4d4a-4986-bb1c-f46f261fbc46; development AI silver only, not final methodology approval',
        seed=SEED,shuffle='Python random.Random(42).shuffle after query_id/chunk_id lexical sorting; stored order is authoritative',
        python=sys.version,rubric_version='wo_pooled_silver_rubric_v1',
        pilot_selection='Every query once in shuffled order; fill each existing style to ten; no grades/ranks used',
        assessor_status='NOT RUN: no configured isolated structured assessor used; current conversation has seen rankings/old grades',
        proposed_assessments=0,unresolved_count=None,disagreements=None,projected_coverage='NOT COMPUTED: no proposed assessments',
        counts={'pool':654,'existing_judged':90,'unjudged':564,'pending_assessment':654,'pilot':30},
        input_hashes={str(p.relative_to(ROOT)):full_colab.file_hash(p) for p in
            [qpath,jpath,PREVIOUS/'run_manifest.json',PREVIOUS/'rankings.jsonl',
             ROOT/'experiments/reports/milestone_9a11_full_colab_import_r3v2.md',
             ROOT/'experiments/reports/milestone_9a12_offline_retrieval_development_pilot.md']},
        driver_sha256=full_colab.file_hash(Path(__file__)))
    write_json(OUTPUT/'manifest.json',run_manifest)
    for name,records in [('blind_assessment_ledger.jsonl',ledger),('blind_pilot_30.jsonl',pilot),('pool_origin_audit.jsonl',origins)]:
        (OUTPUT/name).write_text(''.join(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n' for r in records),encoding='utf8')
    write_csv(OUTPUT/'pool_summary.csv',summary)
    write_csv(OUTPUT/'coverage_existing.csv',audit)
    for r in read_jsonl(OUTPUT/'blind_assessment_ledger.jsonl'):validate_assessment(r)
    write_json(OUTPUT/'protected_integrity.json',verify_baseline(baseline))
    if 'torch' in sys.modules:raise ValueError('Unexpected Torch import')
    run_manifest.update(completion_status='POOL_PREPARED_ASSESSMENT_PENDING',checks={'bindings':'PASS','blind_fields':'PASS',
        'deterministic_pool':'PASS','protected_files':len(baseline),'torch_imported':False},
        outputs={p.name:full_colab.file_hash(p) for p in sorted(OUTPUT.iterdir()) if p.name!='manifest.json'})
    write_json(OUTPUT/'manifest.json',run_manifest)
    print(json.dumps({'status':run_manifest['completion_status'],'counts':run_manifest['counts'],'checks':run_manifest['checks']},indent=2))


if __name__=='__main__':
    run()
