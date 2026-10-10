"""Supplement the existing compare CLI with binding QC, nominal kappa and review artifacts.

Run after audit_pilot_assessments.py compare; never grades or runs retrieval.
"""
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
import csv
import json
import sys
import zipfile

from audit_pilot_assessments import (
    ROOT, SOURCE, OUTPUT, compare, file_hash, jsonl, preflight,
    second_package, text_hash, validate_records, write_json, jsonl_text,
)

RESULT = ROOT / 'experiments/results/milestone_9a15_second_assessor_agreement_audit'
SECOND = ROOT / 'pilot_second_assessments.jsonl'
PILOT = ROOT / 'experiments/results/milestone_9a12_development_pilot'


def nominal_statistics(rows):
    common = [r for r in rows if r['left_grade'] is not None and r['right_grade'] is not None]
    n = len(common)
    same = sum(r['left_grade'] == r['right_grade'] for r in common)
    left = Counter(r['left_grade'] for r in common)
    right = Counter(r['right_grade'] for r in common)
    po = Fraction(same, n) if n else None
    pe = sum((Fraction(left[g] * right[g], n * n) for g in (0, 1, 2)), Fraction()) if n else None
    kappa = (po - pe) / (1 - pe) if pe is not None and pe != 1 else None
    # Unknown grades are excluded from kappa, never treated as grade zero or a fourth ordinal class.
    return {'pairs': len(rows), 'common_resolved': n, 'exact_resolved_count': same,
            'exact_agreement_all_pairs': same / len(rows) if rows else None,
            'exact_agreement_common_resolved': float(po) if po is not None else None,
            'observed_agreement_fraction': str(po), 'expected_agreement_fraction': str(pe),
            'unweighted_cohens_kappa': float(kappa) if kappa is not None else None,
            'unweighted_cohens_kappa_exact_fraction': str(kappa), 'kappa_denominator': n,
            'scope': 'DESCRIPTIVE ONLY; common-resolved purposive AI pairs, clustered queries, no human validation'}


REVIEWS = {
    'WO-POOL-V2-0003': {
        'issue': 'Useful role context versus explicit A/R assignment',
        'substantive_audit': 'Kutipan menerangkan pelaporan jumlah datang dan seating. Tidak menetapkan pengesah A atau pelaksana R untuk daftar registrasi. First menilai hubungan pelaporan tidak mendukung kebutuhan penugasan spesifik; second menganggap alur peran sebagai dukungan sebagian. Keduanya mengakui A/R tidak dapat disimpulkan. Titik sengketa adalah ambang useful support, bukan fakta A/R yang berbeda.',
        'adjudication_question': 'Apakah alur pelaporan ini membantu pembagian A/R secara substantif, atau hanya memberi konteks peran yang belum menjawab kebutuhan? Jangan mengubah relasi pelaporan menjadi mandat RACI.'},
    'WO-POOL-V2-0107': {
        'issue': 'Missing C03 mapping versus general readiness support; unresolved/resolved mismatch',
        'substantive_audit': 'Query meminta cue C03 entrance. Chunk memuat handover EVT-01 saat hujan, status area/rute/vendor dan cue pengganti, tanpa kode C03. First menahan keputusan karena mapping hilang; second memberi dukungan umum grade1 sambil mengakui C03 tidak teridentifikasi. Tidak sah menyamakan cue pengganti atau pembukaan area dengan C03. Perbedaan mencakup kebijakan kecukupan konteks, bukan jarak grade.',
        'adjudication_question': 'Apakah kebutuhan cue C03 cukup jelas untuk menilai kontribusi umum chunk tanpa mapping, atau konteks yang hilang mewajibkan UNRESOLVED? Jika diminta, pengelola memberi mapping tanpa label/rank; konteks dicatat dengan hash dan locator, tidak dipakai untuk mengatribusikan jawaban baru ke chunk ini.'},
    'WO-POOL-V2-0246': {
        'issue': 'Earlier planning versus H-7 outstanding tracking',
        'substantive_audit': 'Chunk membahas H-20 sampai H-17. Pernyataan WC membawa opsi, batas waktu dan dampak biaya merupakan koordinasi keputusan biaya, bukan ledger seluruh pekerjaan belum tuntas sampai hari acara. First menolak karena pencatatan/tindak lanjut yang diminta tidak tersedia; second memberi dukungan terbatas untuk pekerjaan terbuka. Perlu menilai manfaat nyata aspek batas waktu tanpa menganggapnya sistem pemantauan H-7 atau memperluas mandat WC ke seluruh outstanding.',
        'adjudication_question': 'Apakah koordinasi keputusan biaya beserta batas waktu cukup berguna untuk kebutuhan mencatat dan memantau outstanding H-7, meskipun tahap dan cakupan berbeda? Tidak mengarang kolom ledger, cadence, atau bukti penyelesaian.'},
    'WO-POOL-V2-0325': {
        'issue': 'Vendor readiness versus access inspection at a beach',
        'substantive_audit': 'Chunk memberi daftar final confirmation vendor: lingkup, kuantitas, kedatangan, setup, area, fasilitas dan pengganti. Tidak memuat pemeriksaan jalur tamu atau perpindahan perlengkapan di pantai. First menganggap daftar umum tidak membantu kebutuhan akses; second menganggap area/fasilitas/waktu memberi sebagian dukungan. Tidak boleh menambahkan kondisi permukaan, kendaraan, pasang-surut atau izin pantai yang tidak tertulis.',
        'adjudication_question': 'Apakah pemeriksaan area kerja/fasilitas memberi dukungan konkret bagi akses ke lokasi, atau hanya kedekatan operasional vendor dengan query peninjauan akses?'}
}


def main():
    # Small arithmetic self-checks independent of the actual observed distribution.
    assert nominal_statistics([{'left_grade': g, 'right_grade': g} for g in (0, 2)])['unweighted_cohens_kappa'] == 1
    assert nominal_statistics([{'left_grade': g, 'right_grade': 2-g} for g in (0, 2)])['unweighted_cohens_kappa'] == -1
    assert nominal_statistics([{'left_grade': None, 'right_grade': 0}])['common_resolved'] == 0
    assert nominal_statistics([{'left_grade': 1, 'right_grade': 1}])['unweighted_cohens_kappa'] is None
    pilot, first, queries, historical = preflight()
    expected, mapping = second_package(pilot, {q: r['style'] for q, r in queries.items()})
    assert jsonl(OUTPUT / 'pilot_second_input.jsonl') == expected
    assert jsonl(OUTPUT / 'alias_mapping_private.jsonl') == mapping
    with zipfile.ZipFile(OUTPUT / 'second_assessor_package.zip') as z:
        assert z.testzip() is None
        assert set(z.namelist()) == {'pilot_second_input.jsonl', 'second_assessor_prompt.md'}
        for name in z.namelist():
            assert z.read(name) == (OUTPUT / name).read_bytes()
        assert (SOURCE / 'rubric_workflow.md').read_bytes() in z.read('second_assessor_prompt.md')
    second = jsonl(SECOND)
    validate_records(second, expected)
    inputs = {r['assessment_id']: r for r in expected}
    aliases = {r['assessment_alias']: r for r in mapping}
    firstmap = {r['assessment_id']: r for r in first}
    pmap = {r['assessment_id']: r for r in pilot}
    assert len(aliases) == len({r['original_assessment_id'] for r in mapping}) == 30
    for r in second:
        source = inputs[r['assessment_id']]
        assert all(r[k] == v for k, v in source.items())
        assert text_hash(r['query_text']) == r['query_text_sha256']
        assert text_hash(r['serialized_chunk_text']) == r['serialized_text_sha256']
        prov = r['assessor_provenance']
        assert prov['human_validated'] is False and prov['label'] == 'AI SILVER — PROVISIONAL'
        assert prov['rubric_version'] == 'wo_pooled_silver_rubric_v1'
        assert all(isinstance(prov[k], str) and prov[k].strip() for k in ('model_id', 'model_revision', 'session_id'))
        assert datetime.fromisoformat(prov['assessed_at']).utcoffset().total_seconds() == 0
        assert prov['context_limitations'] and all(isinstance(x, str) and x.strip() for x in prov['context_limitations'])
    pairs = jsonl(RESULT / 'all_pair_comparisons.jsonl')
    comparison = json.loads((RESULT / 'comparison.json').read_text(encoding='utf8'))
    assert comparison['first_sha256'] == file_hash(SOURCE / 'blind_pilot_30_assessments.jsonl')
    assert comparison['second_sha256'] == file_hash(SECOND)
    assert comparison['overall'] == compare(pairs)
    secondmap = {r['assessment_id']: r for r in second}
    assert len(pairs) == 30 and len({r['assessment_id'] for r in pairs}) == 30
    for r in pairs:
        alias = aliases[r['second_alias']]
        assert r['assessment_id'] == alias['original_assessment_id']
        assert r['query_style'] == queries[alias['original_query_id']]['style'] == alias['query_style']
        for side, original in (('left', firstmap[r['assessment_id']]), ('right', secondmap[r['second_alias']])):
            for field in ('grade', 'status', 'rationale', 'evidence', 'uncertainty_reason'):
                assert r[f'{side}_{field}'] == original[field]
    flagged = [r for r in pairs if r['adjudication_needed']]
    assert {r['assessment_id'] for r in flagged} == set(REVIEWS)
    assert jsonl(RESULT / 'adjudication_candidates.jsonl') == flagged
    names = ('agreement_statistics.json', 'second_input_qc.json', 'disagreement_ledger.jsonl', 'supervisor_top10_example.csv', 'protected_integrity.json')
    assert all(not (RESULT / n).exists() for n in names), 'Refusing supplemental output overwrite'
    protected = dict(historical)
    for folder in (SOURCE, OUTPUT, PILOT):
        for path in folder.iterdir():
            if path.is_file():
                protected[str(path)] = file_hash(path)
    for path in (SECOND, ROOT / 'scripts/audit_pilot_assessments.py', ROOT / 'tests/test_pilot_assessment_audit.py', ROOT / 'experiments/reports/milestone_9a14_pilot_assessment_audit.md'):
        protected[str(path)] = file_hash(path)
    pm = json.loads((PILOT / 'run_manifest.json').read_text(encoding='utf8'))
    for name, digest in pm['outputs'].items():
        assert file_hash(PILOT / name) == digest
    rankings = jsonl(PILOT / 'rankings.jsonl')
    qrels = jsonl(ROOT / 'data/versions/v2_ai_corrected/benchmark/development_qrels_ai_silver_v2.jsonl')
    assert len(rankings) == len({(r['query_id'], r['method']) for r in rankings}) == 72
    assert Counter(r['method'] for r in rankings) == {m: 18 for m in ('R1', 'R2', 'R3', 'R4')}
    assert len(qrels) == 684 and Counter(r['grade'] for r in qrels) == {0: 621, 1: 32, 2: 31}
    qmap = {(r['query_id'], r['chunk_id']): r['grade'] for r in qrels}
    pool = {(r['query_id'], c['chunk_id']) for r in rankings for c in r['results'][:20]}
    coverage = {}
    for m in ('R1', 'R2', 'R3', 'R4'):
        top = [(r['query_id'], c['chunk_id']) for r in rankings if r['method'] == m for c in r['results'][:10]]
        assert len(top) == 180
        judged = sum(pair in qmap for pair in top)
        coverage[m] = {'returned': len(top), 'judged': judged, 'unjudged': len(top)-judged}
    stats = {'overall': nominal_statistics(pairs),
             'by_query_style': {s: nominal_statistics([r for r in pairs if r['query_style'] == s]) for s in sorted(comparison['by_query_style'])},
             'linear_weighted_cohens_kappa': comparison['overall']['linear_weighted_cohens_kappa'],
             'grade_disagreements': sum(r['left_grade'] is not None and r['right_grade'] is not None and r['left_grade'] != r['right_grade'] for r in pairs),
             'status_disagreements': sum(r['left_status'] != r['right_status'] for r in pairs),
             'retrieval_readback': {'rankings': len(rankings), 'queries': len(queries), 'top10_rows': sum(v['returned'] for v in coverage.values()),
                                   'top10_coverage': coverage, 'pool20_unique': len(pool), 'pool20_existing_judged': sum(p in qmap for p in pool)},
             'assessed_label': 'AI SILVER — PROVISIONAL', 'human_validated': False}
    write_json(RESULT / names[0], stats)
    write_json(RESULT / names[1], {'status': 'PASS', 'records': 30, 'binding_and_hashes': 'PASS', 'zip_and_rubric_bytes': 'PASS',
        'unique_alias_roundtrip': 'PASS', 'evidence_exact_substrings': 'PASS', 'provenance_schema_and_disclosure': 'PASS',
        'model_revision_session_independently_verified': False, 'semantic_validity': 'NOT ESTABLISHED',
        'first_isolation': 'NOT_FULLY_BLIND_PRIOR_CONTEXT_EXPOSED', 'second_isolation': 'NOT_FULLY_ISOLATED_WORKSPACE_ACCESS_AND_CONTEXT',
        'first_provenance': first[0]['assessor_provenance'], 'second_provenance': second[0]['assessor_provenance'],
        'input_hashes': {str(p.relative_to(ROOT)): file_hash(p) for p in (SECOND, SOURCE/'blind_pilot_30.jsonl', SOURCE/'blind_pilot_30_assessments.jsonl', OUTPUT/'pilot_second_input.jsonl', OUTPUT/'alias_mapping_private.jsonl', OUTPUT/'second_assessor_prompt.md', OUTPUT/'second_assessor_package.zip')}})
    ledger = []
    for r in sorted(flagged, key=lambda x: x['assessment_id']):
        source = pmap[r['assessment_id']]
        ledger.append({**r, **REVIEWS[r['assessment_id']],
            'input_binding': source, 'first_assessment': firstmap[r['assessment_id']], 'second_assessment': secondmap[r['second_alias']],
            'adjudication_status': 'PENDING_HUMAN_EXPERT_REVIEW', 'adjudicated_grade': None, 'adjudicated_status': None,
            'adjudicator_provenance': None, 'adjudication_rationale': None, 'additional_context_opened': [],
            'audit_label': 'AI AUDIT OBSERVATION; NOT A NEW RELEVANCE JUDGMENT', 'human_validated': False})
    (RESULT / names[2]).write_text(jsonl_text(ledger), encoding='utf8')
    with (RESULT / names[3]).open('w', encoding='utf8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['query_id', 'query_text', 'rank', 'R1', 'R2', 'R3', 'R4'])
        writer.writeheader()
        selected = {r['method']: r for r in rankings if r['query_id'] == 'WO-DEV-006'}
        for i in range(10):
            writer.writerow({'query_id': 'WO-DEV-006', 'query_text': selected['R1']['query_text'], 'rank': i+1,
                             **{m: selected[m]['results'][i]['chunk_id'] for m in selected}})
    assert len(jsonl(RESULT / names[2])) == 4
    for path, digest in protected.items():
        assert file_hash(path) == digest, f'Protected input changed: {path}'
    assert 'torch' not in sys.modules
    write_json(RESULT / names[4], {'status': 'PASS', 'files': len(protected), 'historical_baseline_files': len(historical), 'hashes': protected})
    print(json.dumps({'overall': stats['overall'], 'by_style': stats['by_query_style'], 'coverage': coverage,
                      'protected_files': len(protected), 'torch_imported': False}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
