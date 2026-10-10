"""Audit immutable first assessments and prepare/compare a separate AI review; no grading."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
import tomllib
import zipfile

from wo_retrieval.retrieval.text import serialize

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'experiments/results/milestone_9a13_judgment_pool'
OUTPUT=ROOT/'experiments/results/milestone_9a14_pilot_assessment_audit'
SEED=14042
REQUIRED={'assessment_id','query_id','chunk_id','grade','status','evidence','rationale','uncertainty_reason'}


def file_hash(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def text_hash(text):
    return sha256(text.encode('utf8')).hexdigest()


def jsonl(path):
    return [json.loads(x) for x in Path(path).read_text(encoding='utf8').splitlines() if x.strip()]


def write_json(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')


def jsonl_text(records):
    return ''.join(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n' for r in records)


def validate_records(records,inputs):
    expected={r['assessment_id']:r for r in inputs}
    if len(expected)!=len(inputs) or len(records)!=len(inputs):
        raise ValueError('Missing/duplicate input or assessment count')
    seen=set()
    for r in records:
        if not REQUIRED <= set(r) or r['assessment_id'] in seen or r['assessment_id'] not in expected:
            raise ValueError('Missing fields/duplicate/unknown assessment ID')
        seen.add(r['assessment_id']);source=expected[r['assessment_id']]
        if (r['query_id'],r['chunk_id'])!=(source['query_id'],source['chunk_id']):
            raise ValueError('ID mapping mismatch')
        if r['status']=='RESOLVED':
            if type(r['grade']) is not int or r['grade'] not in (0,1,2) or r['uncertainty_reason'] is not None:
                raise ValueError('Invalid resolved grade or uncertainty schema')
        elif r['status']=='UNRESOLVED':
            if r['grade'] is not None or not isinstance(r['uncertainty_reason'],str) or not r['uncertainty_reason'].strip():
                raise ValueError('Unresolved must retain null grade and reason')
        else:raise ValueError('Invalid status')
        if not isinstance(r['rationale'],str) or not r['rationale'].strip():
            raise ValueError('Missing rationale')
        quote=r['evidence']
        if quote is not None and (not isinstance(quote,str) or not quote.strip() or quote not in source['serialized_chunk_text']):
            raise ValueError('Quote not in exact chunk')
        if r['status']=='RESOLVED' and quote is None:
            raise ValueError('Resolved rubric requires evidence')
    if seen!=set(expected):raise ValueError('Missing assessment IDs')


def compare(records):
    """None stays unknown; matrix/ordinal statistics use common resolved pairs only."""
    matrix=[[0]*3 for _ in range(3)]
    for r in records:
        if r['left_grade'] is not None and r['right_grade'] is not None:
            matrix[r['left_grade']][r['right_grade']]+=1
    n=sum(map(sum,matrix));agree=sum(matrix[i][i] for i in range(3))
    left=Counter(r['left_grade'] for r in records);right=Counter(r['right_grade'] for r in records)
    marginal_left=[sum(row) for row in matrix];marginal_right=[sum(matrix[i][j] for i in range(3)) for j in range(3)]
    kappa=None;reason='Insufficient common-resolved pairs or grade variation; descriptive counts only'
    if n>=2 and sum(x>0 for x in marginal_left)>=2 and sum(x>0 for x in marginal_right)>=2:
        observed=sum(abs(i-j)*matrix[i][j] for i in range(3) for j in range(3))/n
        expected=sum(abs(i-j)*marginal_left[i]*marginal_right[j] for i in range(3) for j in range(3))/(n*n)
        if expected>0:
            kappa=1-observed/expected;reason='DESCRIPTIVE ONLY: linear ordinal weights; common-resolved subset; small purposive dependent pairs, no inference or human validation'
    return {'pairs':len(records),'common_resolved':n,'exact_grade_agreement_count':agree,
        'exact_grade_agreement_fraction':agree/n if n else None,'confusion_matrix_rows_left_columns_right':matrix,
        'grade_distance':dict(Counter(str(abs(r['left_grade']-r['right_grade'])) for r in records if r['left_grade'] is not None and r['right_grade'] is not None)),
        'grade_0_vs_1':matrix[0][1]+matrix[1][0],'grade_1_vs_2':matrix[1][2]+matrix[2][1],
        'left_unresolved':left[None],'right_unresolved':right[None],
        'both_unresolved':sum(r['left_grade'] is None and r['right_grade'] is None for r in records),
        'unresolved_on_one_side':sum((r['left_grade'] is None)!=(r['right_grade'] is None) for r in records),
        'left_distribution':{'UNRESOLVED' if k is None else str(k):v for k,v in left.items()},
        'right_distribution':{'UNRESOLVED' if k is None else str(k):v for k,v in right.items()},
        'mean_right_minus_left_grade_common_resolved':sum(r['right_grade']-r['left_grade'] for r in records if r['left_grade'] is not None and r['right_grade'] is not None)/n if n else None,
        'linear_weighted_cohens_kappa':kappa,'kappa_denominator':n,'kappa_scope':reason}


def second_package(pilot,styles):
    ordered=sorted(pilot,key=lambda r:r['assessment_id'])
    qaliases={q:f'QUERY-{i:03d}' for i,q in enumerate(sorted({r['query_id'] for r in pilot}),1)}
    caliases={c:f'CHUNK-{i:03d}' for i,c in enumerate(sorted({r['chunk_id'] for r in pilot}),1)}
    inputs=[];mapping=[]
    for i,r in enumerate(ordered,1):
        alias=f'PILOT2-{i:03d}'
        inputs.append({'assessment_id':alias,'query_id':qaliases[r['query_id']],
            'chunk_id':caliases[r['chunk_id']],'query_text':r['query_text'],
            'serialized_chunk_text':r['serialized_chunk_text'],
            'query_text_sha256':r['query_text_sha256'],'serialized_text_sha256':r['serialized_text_sha256']})
        mapping.append({'assessment_alias':alias,'query_alias':qaliases[r['query_id']],
            'chunk_alias':caliases[r['chunk_id']],'original_assessment_id':r['assessment_id'],
            'original_query_id':r['query_id'],'original_chunk_id':r['chunk_id'],
            'query_style':styles[r['query_id']],'source_snapshot_id':r['source_snapshot_id'],
            'source_snapshot_fingerprint':r['source_snapshot_fingerprint']})
    random.Random(SEED).shuffle(inputs)
    return inputs,mapping


def preflight():
    persisted=OUTPUT/'protected_integrity.json'
    baseline=(json.loads(persisted.read_text(encoding='utf8'))['hashes'] if persisted.exists()
              else json.loads(Path('D:/ModelCache/tmp/wo-m9a14/baseline.json').read_text(encoding='utf8')))
    for path,h in baseline.items():
        if not Path(path).is_file() or file_hash(path)!=h:raise ValueError(f'Protected input changed: {path}')
    m=json.loads((SOURCE/'manifest.json').read_text(encoding='utf8'))
    for name,h in m['outputs'].items():
        if file_hash(SOURCE/name)!=h:raise ValueError(f'Pool artifact changed: {name}')
    snapshot=json.loads((ROOT/'data/versions/v2_ai_corrected/validation/pilot_snapshot.json').read_text(encoding='utf8'))
    fingerprint=snapshot['aggregate_fingerprint']['value']
    recomputed=text_hash(json.dumps(snapshot['artifact_sha256'],ensure_ascii=False,sort_keys=True,separators=(',',':')))
    if snapshot['snapshot_id']!=m['snapshot']['id'] or fingerprint!=m['snapshot']['aggregate_fingerprint'] or recomputed!=fingerprint:
        raise ValueError('Snapshot identity mismatch')
    for key in ('artifact_sha256','source_file_sha256'):
        for path,h in snapshot[key].items():
            if file_hash(ROOT/path)!=h:raise ValueError(f'Frozen V2 artifact changed: {path}')
    pilot=jsonl(SOURCE/'blind_pilot_30.jsonl');first=jsonl(SOURCE/'blind_pilot_30_assessments.jsonl')
    if len(pilot)!=30 or len({(r['query_id'],r['chunk_id']) for r in pilot})!=30:
        raise ValueError('Pilot does not contain 30 unique pairs')
    validate_records(first,pilot)
    queries={r['query_id']:r for r in jsonl(ROOT/'data/benchmark/development_queries_draft.jsonl')}
    chunks={r['chunk_id']:r for r in jsonl(ROOT/'data/versions/v2_ai_corrected/chunks/chunks.jsonl')}
    policy=tomllib.loads((ROOT/'experiments/configs/retrieval_protocol_v1.toml').read_text(encoding='utf8'))['serialization']
    pmap={r['assessment_id']:r for r in pilot}
    for r in first:
        source=pmap[r['assessment_id']];text,_=serialize(chunks[source['chunk_id']],policy)
        if source['query_text']!=queries[source['query_id']]['text'] or source['serialized_chunk_text']!=text:
            raise ValueError('Frozen corpus/query text mismatch')
        if source['query_text_sha256']!=text_hash(source['query_text']) or source['serialized_text_sha256']!=text_hash(text):
            raise ValueError('Input text hash mismatch')
        expected={k:source[k] for k in ('source_snapshot_id','source_snapshot_fingerprint','document_id','query_text_sha256','serialized_text_sha256')}
        if (r['input_binding']!=expected or source['document_id']!=chunks[source['chunk_id']]['document_id']
                or source['source_snapshot_id']!=snapshot['snapshot_id'] or source['source_snapshot_fingerprint']!=fingerprint):
            raise ValueError('Assessment snapshot/document binding mismatch')
        p=r['assessor_provenance']
        if (p['human_validated'] is not False or p['blindness_status']!='NOT_FULLY_BLIND_PRIOR_CONTEXT_EXPOSED'
                or p['pilot_input_sha256']!=file_hash(SOURCE/'blind_pilot_30.jsonl')
                or p['rubric_sha256']!=file_hash(SOURCE/'rubric_workflow.md')
                or p['label']!='AI SILVER — PROVISIONAL'):
            raise ValueError('Provenance mismatch')
        datetime.fromisoformat(p['recorded_at_utc'])
    grades=Counter('UNRESOLVED' if r['grade'] is None else str(r['grade']) for r in first)
    if grades!={'0':13,'1':11,'2':5,'UNRESOLVED':1}:raise ValueError('Reported grade distribution mismatch')
    return pilot,first,queries,baseline


def prepare():
    if OUTPUT.exists():raise ValueError('Refusing output overwrite')
    pilot,first,queries,baseline=preflight()
    # Old labels are consulted only after the complete first-pass validation above.
    old=jsonl(ROOT/'data/versions/v2_ai_corrected/benchmark/development_qrels_ai_silver_v2.jsonl')
    oldmap={(r['query_id'],r['chunk_id']):r['grade'] for r in old}
    if len(oldmap)!=684 or Counter(oldmap.values())!={0:621,1:32,2:31}:raise ValueError('Old qrels changed')
    rows=[]
    for r in first:
        pair=r['query_id'],r['chunk_id'];grade=oldmap.get(pair)
        rows.append({'assessment_id':r['assessment_id'],'query_id':r['query_id'],'chunk_id':r['chunk_id'],
            'query_style':queries[r['query_id']]['style'],'previously_judged':pair in oldmap,
            'left_grade':grade,'right_grade':r['grade'],
            'comparison_status':'PREVIOUSLY_UNJUDGED' if pair not in oldmap else
                'NEW_UNRESOLVED' if r['grade'] is None else 'AGREEMENT' if grade==r['grade'] else 'GRADE_CONFLICT'})
    overlap=[r for r in rows if r['previously_judged']]
    old_comparison=compare(overlap)
    old_comparison['linear_weighted_cohens_kappa']=None
    old_comparison['kappa_scope']='NOT REPORTED: only three old-silver overlapping pairs, non-independent prior-context exposure; counts only'
    inputs,mapping=second_package(pilot,{q:r['style'] for q,r in queries.items()})
    prompt='''# Penilaian relevansi AI silver

Nilai tepat 30 pasangan pada pilot_second_input.jsonl dalam sesi baru yang tidak
membawa history penelitian dan tidak memiliki akses repository. Baca seluruh
input dan rubric di bawah. IDs adalah aliases; jangan menebak identitas asal.
Jangan membuka ranking, scores, labels lama atau sumber lain. Pertahankan teks.
Nilai substansi query dan chunk; jangan mengisi informasi dengan pengetahuan umum.
Jangan menyeimbangkan distribusi grade. Jika bukti/konteks tidak cukup, UNRESOLVED.
Hasil ini AI SILVER — PROVISIONAL, bukan human/expert validated atau gold standard.

Output hanya pilot_second_assessments.jsonl, satu record per input, mempertahankan
assessment_id/query_id/chunk_id aliases. Fields: grade integer0/1/2 atau null,
status RESOLVED atau UNRESOLVED, evidence satu kutipan verbatim atau null,
rationale spesifik, uncertainty_reason string untuk UNRESOLVED dan null lainnya.
Rubric ASSESSED dipetakan ke RESOLVED, relevance_grade ke grade; evidence list
dipetakan ke satu kutipan yang paling mendukung. RESOLVED memerlukan kutipan,
termasuk grade0 untuk menunjukkan isi yang dibandingkan. UNRESOLVED tidak menjadi0.
Tambahkan assessor_provenance actual model/revision/session, timestamp UTC,
rubric_version, human_validated false dan keterbatasan konteks; gunakan not_exposed
untuk identitas yang tidak diekspos, jangan mengarang. Jangan ubah binding input.

QC semua30: IDs unik/lengkap, evidence substring, grade2 direct answer, grade1
useful support bukan hanya kata sama, unresolved null. Tidak menilai pasangan lain,
menjalankan retrieval/model lain, membandingkan labels atau menggabungkan qrels.
Instruksi task ini membatasi workflow rubric di bawah pada satu batch30 saja;
tahapan pengelola/ekspansi sesudahnya tidak dijalankan oleh assessor. STOP setelah
file hasil dan ringkasan grade/unresolved siap.

## Rubric original (verbatim, tidak diubah)

'''+(SOURCE/'rubric_workflow.md').read_text(encoding='utf8')
    OUTPUT.mkdir(parents=True)
    write_json(OUTPUT/'manifest.json',{'completion_status':'INCOMPLETE'})
    (OUTPUT/'pilot_second_input.jsonl').write_text(jsonl_text(inputs),encoding='utf8')
    marker='## Rubric original (verbatim, tidak diubah)\n\n'
    prefix=prompt.split(marker,1)[0]+marker
    (OUTPUT/'second_assessor_prompt.md').write_bytes(prefix.encode('utf8')+(SOURCE/'rubric_workflow.md').read_bytes())
    (OUTPUT/'alias_mapping_private.jsonl').write_text(jsonl_text(mapping),encoding='utf8')
    (OUTPUT/'old_silver_comparison_private.jsonl').write_text(jsonl_text(rows),encoding='utf8')
    with zipfile.ZipFile(OUTPUT/'second_assessor_package.zip','x',compression=zipfile.ZIP_DEFLATED) as z:
        for name in ('pilot_second_input.jsonl','second_assessor_prompt.md'):
            z.write(OUTPUT/name,arcname=name)
    with zipfile.ZipFile(OUTPUT/'second_assessor_package.zip') as z:
        if z.testzip() is not None or set(z.namelist())!={'pilot_second_input.jsonl','second_assessor_prompt.md'}:
            raise ValueError('Package contents/CRC invalid')
        for name in z.namelist():
            if z.read(name)!=(OUTPUT/name).read_bytes():raise ValueError('ZIP byte mismatch')
    for path,h in baseline.items():
        if file_hash(path)!=h:raise ValueError(f'Protected mutation: {path}')
    write_json(OUTPUT/'protected_integrity.json',{'status':'PASS','files':len(baseline),'hashes':baseline})
    audit={'first_distribution':dict(Counter('UNRESOLVED' if r['grade'] is None else str(r['grade']) for r in first)),
        'pilot_pairs':30,'previously_judged':len(overlap),'previously_unjudged':30-len(overlap),
        'old_vs_first':old_comparison,'conflicts':[r for r in rows if r['comparison_status']=='GRADE_CONFLICT'],
        'semantic_validity':'NOT ESTABLISHED; four flagged cases retained, no regrading',
        'independence':'First pass explicitly not fully blind; second assessment NOT RUN'}
    write_json(OUTPUT/'first_pass_audit.json',audit)
    write_json(OUTPUT/'manifest.json',{'completion_status':'SECOND_PACKAGE_READY_ASSESSMENT_NOT_RUN',
        'created_at':datetime.now(timezone.utc).isoformat(),'seed':SEED,'python':sys.version,
        'shuffle':'random.Random(14042).shuffle after original assessment_id sorting; aliases assigned before shuffle',
        'rubric_sha256':file_hash(SOURCE/'rubric_workflow.md'),'first_assessments_sha256':file_hash(SOURCE/'blind_pilot_30_assessments.jsonl'),
        'private_mapping':'alias_mapping_private.jsonl; do not give to assessor',
        'outputs':{p.name:file_hash(p) for p in sorted(OUTPUT.iterdir()) if p.name!='manifest.json'},
        'source_hashes':{str(p):file_hash(p) for p in [SOURCE/'blind_pilot_30.jsonl',SOURCE/'rubric_workflow.md']},
        'driver_sha256':file_hash(Path(__file__)),'protected_files':len(baseline)})
    print(json.dumps(audit,ensure_ascii=False,indent=2))


def compare_second(second_path,output):
    pilot,first,queries,_=preflight()
    manifest=json.loads((OUTPUT/'manifest.json').read_text(encoding='utf8'))
    for name,h in manifest['outputs'].items():
        if file_hash(OUTPUT/name)!=h:raise ValueError('Second package/mapping tampered')
    inputs=jsonl(OUTPUT/'pilot_second_input.jsonl');mapping=jsonl(OUTPUT/'alias_mapping_private.jsonl')
    second=jsonl(second_path);validate_records(second,inputs)
    aliases={r['assessment_alias']:r for r in mapping};firstmap={r['assessment_id']:r for r in first}
    rows=[]
    for r in second:
        alias=aliases[r['assessment_id']];left=firstmap[alias['original_assessment_id']]
        rows.append({'assessment_id':left['assessment_id'],'second_alias':r['assessment_id'],
            'query_style':alias['query_style'],'left_grade':left['grade'],'right_grade':r['grade'],
            'left_status':left['status'],'right_status':r['status'],
            'left_rationale':left['rationale'],'right_rationale':r['rationale'],
            'left_evidence':left['evidence'],'right_evidence':r['evidence'],
            'left_uncertainty_reason':left['uncertainty_reason'],'right_uncertainty_reason':r['uncertainty_reason'],
            'adjudication_needed':left['grade']!=r['grade'] or left['grade'] is None or r['grade'] is None})
    summary={'overall':compare(rows),'by_query_style':{s:compare([r for r in rows if r['query_style']==s]) for s in sorted({r['query_style'] for r in rows})},
        'first_sha256':file_hash(SOURCE/'blind_pilot_30_assessments.jsonl'),'second_sha256':file_hash(second_path),
        'second_provenance_available':sum(isinstance(r.get('assessor_provenance'),dict) for r in second),
        'limitation':'AI-to-AI descriptive comparison; session isolation requires actual operator evidence, not inferred from agreement; no majority vote or qrels merge'}
    output=Path(output)
    if output.exists():raise ValueError('Refusing comparison output overwrite')
    if output.resolve().is_relative_to(SOURCE.resolve()) or output.resolve().is_relative_to(OUTPUT.resolve()):
        raise ValueError('Use a separate comparison directory')
    output.mkdir(parents=True);write_json(output/'comparison.json',summary)
    (output/'adjudication_candidates.jsonl').write_text(jsonl_text([r for r in rows if r['adjudication_needed']]),encoding='utf8')
    (output/'all_pair_comparisons.jsonl').write_text(jsonl_text(rows),encoding='utf8')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','compare'])
    parser.add_argument('--second',type=Path);parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    if args.action=='prepare':prepare()
    elif not args.second or not args.out:parser.error('compare requires --second and --out')
    else:compare_second(args.second,args.out)
