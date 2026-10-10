"""Synthetic importer tests; never write into the research workspace."""
from pathlib import Path
import sys,tempfile,unittest
from copy import deepcopy
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from test_human_annotation import fixture
from wo_retrieval import human_judgments as h
from wo_retrieval import human_import as imp


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.package,_=fixture(self.root)
        self.source=self.package['workspace']/'review.jsonl';self.audit=self.package['workspace']/'audit.json'
        self.rows=[dict(assessment_id=r['assessment_id'],binding=h.binding(self.package,r),
            status='RESOLVED',grade=1,notes='SYNTHETIC NOT RESEARCH',evidence=r['chunk_text']) for r in self.package['rows']]
        self.refresh()
        self.out=self.root/'import_output'

    def refresh(self):
        from collections import Counter
        h.atomic_text(self.source,h.jsonl_text(self.rows));m=self.package['manifest']
        h.write_json(self.audit,dict(expected_package_id=m['package_id'],expected_input_sha256=m['input_sha256'],
            snapshot_id=m['snapshot_id'],snapshot_fingerprint=m['snapshot_fingerprint'],
            input_jsonl_sha256=h.file_hash(self.source),input_record_count=len(self.rows),
            grade_counts=dict(Counter(str(r['grade']) for r in self.rows)),status_counts=dict(Counter(r['status'] for r in self.rows)),
            notes_count=sum(bool(r['notes']) for r in self.rows),evidence_quote_count=sum(bool(r['evidence']) for r in self.rows),
            binding_and_evidence_verified=True))

    def plan(self):return imp.preflight(self.package,self.source,self.audit)[0]
    def apply(self,plan=None):return imp.apply_import(self.package,self.source,self.audit,plan or self.plan(),self.out)

    def test_dry_run_readonly_import_preserves_history_and_idempotence(self):
        row=self.rows[0];h.save_decision(self.package,row['assessment_id'],*(row[k] for k in imp.FIELDS))
        before=h.load_history(self.package)[0];inputbytes=(self.package['workspace']/'annotation_input.jsonl').read_bytes()
        plan=self.plan();self.assertEqual(plan['status'],'PASS');self.assertEqual(len(plan['skipped']),1)
        self.assertEqual(h.load_history(self.package)[0],before)
        receipt=self.apply(plan);events,latest=h.load_history(self.package)
        self.assertEqual(receipt['imported'],35);self.assertEqual(events[:1],before);self.assertEqual(len(events),36)
        self.assertEqual((self.package['workspace']/'annotation_input.jsonl').read_bytes(),inputbytes)
        self.assertEqual((self.out/'workspace_backup/human_judgment_history.jsonl').read_bytes(),h.jsonl_text(before).encode())
        provenance=events[-1]['provenance'];self.assertIsNone(provenance['import_source']['original_assessed_at_utc'])
        self.assertEqual(provenance['import_source']['source_sha256'],h.file_hash(self.source))
        other=imp.apply_import(self.package,self.source,self.audit,self.plan(),self.root/'rerun')
        self.assertEqual(other['imported'],0);self.assertEqual(other['import_status'],'SKIPPED_IDENTICAL')
        self.assertEqual(h.load_history(self.package)[0],events)

    def test_each_conflicting_field_blocks_without_overwrite(self):
        row=self.rows[0]
        for field,value in [('grade',2),('notes','different'),('evidence',''),('status','UNRESOLVED')]:
            with self.subTest(field=field):
                event=dict(row);event[field]=value
                if field=='status':event['grade']=None
                history=self.package['workspace']/'human_judgment_history.jsonl';h.atomic_text(history,'')
                h.save_decision(self.package,row['assessment_id'],*(event[k] for k in imp.FIELDS))
                old=history.read_bytes();plan=self.plan()
                self.assertEqual(plan['status'],'CONFLICT');self.assertIn(field,plan['conflicts'][0]['different_fields'])
                with self.assertRaises(ValueError):self.apply(plan)
                self.assertEqual(history.read_bytes(),old);self.assertFalse(self.out.exists())

    def test_server_lock_blocks(self):
        with h.exclusive(self.package['workspace']/'.server.lock'):
            plan=self.plan();self.assertEqual(plan['status'],'BLOCKED_WORKSPACE_ACTIVE')
            with self.assertRaises(ValueError):self.apply(plan)

    def test_stale_plan_blocks(self):
        plan=self.plan();row=self.rows[0]
        h.save_decision(self.package,row['assessment_id'],*(row[k] for k in imp.FIELDS))
        with self.assertRaises(ValueError):self.apply(plan)
        self.assertFalse(self.out.exists())

    def test_source_checksums_duplicates_binding_evidence_and_counts(self):
        original=deepcopy(self.rows)
        for kind in ('duplicate','binding','evidence','count','checksum'):
            with self.subTest(kind=kind):
                self.rows=deepcopy(original)
                if kind=='duplicate':self.rows.append(self.rows[0])
                if kind=='binding':self.rows[0]['binding']['snapshot_fingerprint']='WRONG'
                if kind=='evidence':self.rows[0]['evidence']='fabricated evidence'
                self.refresh()
                if kind=='checksum':h.atomic_text(self.source,h.jsonl_text(self.rows)+'\n')
                if kind=='count':
                    audit=h.read_json(self.audit);audit['grade_counts']={'0':36};h.write_json(self.audit,audit)
                with self.assertRaises(ValueError):self.plan()

    def test_atomic_failure_and_postpublication_rollback(self):
        history=self.package['workspace']/'human_judgment_history.jsonl';old=history.read_bytes()
        replace=h.os.replace
        def fail_history_replace(source,destination):
            if Path(destination)==history:raise OSError('synthetic history publication failure')
            return replace(source,destination)
        with patch.object(h.os,'replace',side_effect=fail_history_replace):
            with self.assertRaises(OSError):self.apply()
        self.assertEqual(history.read_bytes(),old)
        self.assertFalse((self.package['workspace']/'.write.lock').exists())
        # A failure while publishing the receipt occurs after the batch was published.
        self.out=self.root/'rollback_output';real=h.write_json
        def fail_receipt(path,value):
            if Path(path).name=='import_receipt.json':raise OSError('synthetic post-publication failure')
            real(path,value)
        with patch.object(h,'write_json',side_effect=fail_receipt):
            with self.assertRaises(OSError):self.apply()
        self.assertEqual(history.read_bytes(),old)
        self.assertFalse((self.package['workspace']/'.server.lock').exists())
        self.assertFalse((self.out/'import_receipt.json').exists())

    def test_import_provenance_cannot_fake_original_time(self):
        self.apply();events,_=h.load_history(self.package)
        events[-1]['provenance']['import_source']['original_assessed_at_utc']='2020-01-01T00:00:00+00:00'
        events[-1]['event_sha256']=h.digest({k:v for k,v in events[-1].items() if k!='event_sha256'})
        with self.assertRaises(ValueError):h.load_history(self.package,events)


if __name__=='__main__':unittest.main()
