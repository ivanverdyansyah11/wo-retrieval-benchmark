import csv
import json
import shutil
import tempfile
import unittest
import importlib.util
from pathlib import Path

from wo_retrieval.pipeline import (audit, build_chunks, ingest, jsonl_text, load_config,
                                   sha256, snapshot, verify_canonical, write_chunks,
                                   write_ingestion)


ROOT = Path(__file__).resolve().parents[1]
STATUS = "ai_corrected_pilot_not_human_validated"


class VersionedPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        source = cls.root / "data/corpus_candidates/v2_ai_corrected/documents"
        shutil.copytree(ROOT / "data/corpus_candidates/v2_ai_corrected/documents", source)
        config = cls.root / "pilot_v2.toml"
        shutil.copy(ROOT / "experiments/configs/pilot_v2.toml", config)
        cls.config = load_config(cls.root, config)
        metadata = cls.root / cls.config["manifest"]
        metadata.parent.mkdir(parents=True)
        manifest = json.loads((ROOT / "data/source_corpus/corpus_manifest.json").read_text())
        for m in manifest:
            m.update(file_sha256=sha256(source / m["filename"]), validation_status=STATUS,
                     dataset_version="v2-ai-corrected")
        metadata.write_text(json.dumps(manifest), encoding="utf8")
        with (cls.root / cls.config["inventory"]).open("w", newline="", encoding="utf8") as stream:
            writer = csv.DictWriter(stream, fieldnames=["relative_path", "filename", "sha256", "file_size_bytes", "file_role"])
            writer.writeheader()
            for m in manifest:
                writer.writerow(dict(relative_path=f"documents/{m['filename']}", filename=m["filename"],
                                     sha256=m["file_sha256"], file_size_bytes=(source / m["filename"]).stat().st_size,
                                     file_role="corpus_document"))
        for name in ["data/processed/documents.jsonl", "data/chunks/chunks.jsonl",
                     "data/validation/source_integrity.json", "data/validation/pilot_snapshot.json"]:
            p = cls.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("V1 sentinel", encoding="utf8")

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_v2_paths_cannot_target_v1_or_candidate(self):
        original = (ROOT / "experiments/configs/pilot_v2.toml").read_text()
        for key, value in [("documents_output", "data/processed/documents.jsonl"),
                           ("chunks_output", "data/chunks/chunks.jsonl"),
                           ("reports_dir", "experiments/reports"),
                           ("source_integrity_output", "data/validation/source_integrity.json"),
                           ("manifest", "data/source_corpus/corpus_manifest.json"),
                           ("inventory", "data/source_corpus/FILE_INVENTORY.csv"),
                           ("source_documents", "data/source_corpus/documents")]:
            with self.subTest(key=key):
                p = self.root / "invalid.toml"
                p.write_text(original.replace(f'{key} = "{self.config[key]}"', f'{key} = "{value}"'))
                with self.assertRaises(ValueError):
                    load_config(self.root, p)

    def test_v2_pipeline_repeatability_and_isolated_writes(self):
        before = snapshot(self.root / "data/corpus_candidates")
        documents, report, source_audit = ingest(self.root, self.config)
        chunks, chunk_report = build_chunks(documents, self.config)
        other, _, _ = ingest(self.root, self.config)
        other_chunks, _ = build_chunks(other, self.config)
        self.assertEqual(jsonl_text(documents), jsonl_text(other))
        self.assertEqual(jsonl_text(chunks), jsonl_text(other_chunks))
        verify_canonical(self.root, self.config, documents)
        self.assertEqual(len(documents), 50)
        self.assertTrue(all(c.validation_status == STATUS for c in chunks))
        write_ingestion(self.root, self.config, documents, report, source_audit)
        write_chunks(self.root, self.config, documents, chunks, chunk_report)
        self.assertEqual(snapshot(self.root / "data/corpus_candidates"), before)
        for name in ["data/processed/documents.jsonl", "data/chunks/chunks.jsonl",
                     "data/validation/source_integrity.json", "data/validation/pilot_snapshot.json"]:
            self.assertEqual((self.root / name).read_text(), "V1 sentinel")
        self.assertTrue((self.root / "data/versions/v2_ai_corrected/validation/source_integrity.json").is_file())

    def test_v2_inventory_escape_and_status_rejected(self):
        path = self.root / self.config["inventory"]
        original = path.read_bytes()
        try:
            path.write_text(original.decode().replace("documents/WO-DOC-001.docx", "../WO-DOC-001.docx"))
            _, result = audit(self.root, self.config)
            self.assertTrue(any("Invalid inventory path" in e for e in result["errors"]))
        finally:
            path.write_bytes(original)
        path = self.root / self.config["manifest"]
        original = path.read_bytes()
        try:
            rows = json.loads(original)
            rows[0]["validation_status"] = "human_validated"
            path.write_text(json.dumps(rows))
            _, result = audit(self.root, self.config)
            self.assertTrue(any("Unexpected validation status" in e for e in result["errors"]))
        finally:
            path.write_bytes(original)


class CrossVersionMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("build_v2_pilot", ROOT / "scripts/build_v2_pilot.py")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        import tomllib
        cls.policy = tomllib.loads((ROOT / "experiments/configs/retrieval_protocol_v1.toml").read_text())["serialization"]

    def fixture(self):
        return {"chunk_id": "old", "document_id": "WO-DOC-999", "text": "Operasional lengkap.",
                "title": "Fixture", "heading": "Langkah", "category": "Test", "content_hash": "fixture",
                "source_locator": {"blocks": [{"block_id": "b1", "body_position": 5, "serialized_char_start": 0, "serialized_char_end": 19}]}}

    def test_mapping_uses_content_and_locator_not_chunk_id(self):
        old = self.fixture()
        new = {**old, "chunk_id": "different"}
        self.assertEqual(self.module.compare_chunk(old, [new], self.policy)[0], "EXACT_CONTENT_MATCH_CANDIDATE")
        new = {**old, "text": "Isi berubah.", "content_hash": "changed"}
        self.assertEqual(self.module.compare_chunk(old, [new], self.policy)[0], "CHANGED_CONTENT_REQUIRES_REJUDGMENT")
        new = {**old, "title": "Changed context"}
        self.assertEqual(self.module.compare_chunk(old, [new], self.policy)[0], "CHANGED_CONTENT_REQUIRES_REJUDGMENT")
        new = {**old, "source_locator": {"blocks": [{"block_id": "other", "body_position": 6}]}}
        self.assertEqual(self.module.compare_chunk(old, [new], self.policy)[0], "MISSING_OR_INVALID")
        self.assertEqual(self.module.compare_chunk(old, [old, old], self.policy)[0], "CHUNK_MAPPING_AMBIGUOUS")


if __name__ == "__main__":
    unittest.main()
