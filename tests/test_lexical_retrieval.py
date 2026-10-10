import copy
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np

from wo_retrieval.retrieval.lexical import (
    LexicalRetriever, audit, build, load, prepare,
    read_protocol, verify_snapshot,
)
from wo_retrieval.retrieval.text import LexicalTokenizer, contains, normalize, serialize


ROOT = Path(__file__).resolve().parents[1]
CONFIG = read_protocol(ROOT)


def fixture_rows():
    texts = ["vendor vendor katering", "vendor dekorasi", "rundown prosesi", "tamu registrasi", "biaya kontrak"]
    tokenizer = LexicalTokenizer(CONFIG["lexical"])
    return [{"chunk_id": f"C{i}", "document_id": f"D{i}", "text": text, "tokens": tokenizer(text)} for i, text in enumerate(texts)]


class TextTests(unittest.TestCase):
    def test_normalization_and_unicode_tokens(self):
        tokenize = LexicalTokenizer(CONFIG["lexical"])
        self.assertEqual(normalize("  cafe\u0301\r\nWO\rX "), "café\nWO\nX")
        self.assertEqual(tokenize("WO’S WO's gladi-resik PIC_1 A 08 akad, katering"),
                         ["wo's", "wo's", "gladi-resik", "pic_1", "a", "08", "akad", "katering"])

    def test_serialize_all_formats_allowlist_body_and_dedup(self):
        for source_format in ("DOCX", "PDF", "TXT", "XLSX"):
            body = "Rundown\n\nSheet: Operasional\nHeader: Tugas | PIC\nRow: 4\nTugas: Akad | PIC: Tim WO\nulang ulang"
            chunk = {"title": "Panduan WO", "heading": "Rundown", "category": "Koordinasi", "text": body,
                     "metadata": {"format": source_format, "guide_context": ["ADMIN SECRET"]},
                     "validation_status": "ADMIN SECRET", "source_file": "ADMIN SECRET"}
            text, selected = serialize(chunk, CONFIG["serialization"])
            self.assertEqual(text, "Judul: Panduan WO\nKonteks kategori: Koordinasi\n\n" + body)
            self.assertEqual(selected, ["title", "category"])
            self.assertNotIn("ADMIN SECRET", text)
            self.assertEqual(serialize(copy.deepcopy(chunk), CONFIG["serialization"])[0], text)

    def test_selection_order_and_word_boundaries(self):
        chunk = {"title": "Matriks RACI", "heading": "Matriks RACI / Operasional", "category": "Tim", "text": "Isi"}
        text, fields = serialize(chunk, CONFIG["serialization"])
        self.assertNotIn("title", fields)
        self.assertEqual(text.count("Matriks RACI"), 1)
        self.assertFalse(contains("rundownX", "rundown"))
        self.assertTrue(contains("RUNDOWN\n  AKAD", "rundown akad"))

    def test_required_fields(self):
        with self.assertRaises(ValueError):
            serialize({"title": "", "heading": "x", "category": "x", "text": "x"}, CONFIG["serialization"])


class ScoringTests(unittest.TestCase):
    def test_tfidf_mathematical_cosine_and_corpus_only_idf(self):
        rows = fixture_rows()
        retriever = LexicalRetriever("R1", rows, CONFIG).fit()
        vendor_idf = math.log(6 / 3) + 1
        rare_idf = math.log(6 / 2) + 1
        expected = 2 * vendor_idf / math.sqrt((2 * vendor_idf) ** 2 + rare_idf ** 2)
        results = retriever.retrieve("vendor", 10)
        self.assertEqual([result.chunk_id for result in results], ["C0", "C1"])
        self.assertAlmostEqual(results[0].score, expected, places=14)
        before = retriever.model.idf_.copy()
        retriever.retrieve("kataasing", 5)
        np.testing.assert_array_equal(before, retriever.model.idf_)

    def test_bm25_mathematical_formula_and_repeated_query(self):
        retriever = LexicalRetriever("R2", fixture_rows(), CONFIG).fit()
        avgdl = 11 / 5
        idf = math.log(3.5 / 2.5)
        expected = idf * 2 * 2.5 / (2 + 1.5 * (1 - .75 + .75 * 3 / avgdl))
        results = retriever.retrieve("vendor", 5)
        self.assertEqual([result.chunk_id for result in results], ["C0", "C1"])
        self.assertAlmostEqual(results[0].score, expected, places=14)
        self.assertAlmostEqual(retriever.retrieve("vendor vendor", 1)[0].score, 2 * expected, places=14)

    def test_bm25_negative_idf_floor(self):
        rows = fixture_rows()
        for row in rows:
            row["text"] += " wo"
            row["tokens"].append("wo")
        retriever = LexicalRetriever("R2", rows, CONFIG).fit()
        self.assertGreater(retriever.model.average_idf, 0)
        self.assertAlmostEqual(retriever.model.idf["wo"], .25 * retriever.model.average_idf)
        bad = [{"chunk_id": str(i), "text": "wo", "tokens": ["wo"]} for i in range(3)]
        with self.assertRaisesRegex(ValueError, "IDF is unsafe"):
            LexicalRetriever("R2", bad, CONFIG).fit()

    def test_empty_oov_topk_duplicates_and_metadata(self):
        for method in ("R1", "R2"):
            retriever = LexicalRetriever(method, fixture_rows(), CONFIG).fit()
            for query in ("", " \r\n ", "!!!", "zzzzunknown"):
                self.assertEqual(retriever.retrieve(query, 5), [])
            for top_k in (0, -1, True, 1.5, "5"):
                with self.assertRaises(ValueError):
                    retriever.retrieve("vendor", top_k)
            for query in (None, 123, []):
                with self.assertRaises(ValueError):
                    retriever.retrieve(query, 5)
            self.assertEqual(len(retriever.retrieve("vendor", 1)), 1)
            results = retriever.retrieve("vendor", 999)
            self.assertEqual([r.rank for r in results], [1, 2])
            self.assertEqual(len({r.chunk_id for r in results}), len(results))
            self.assertTrue(all(r.method_id == method and r.snapshot_id == CONFIG["snapshot"]["id"] and math.isfinite(r.score) for r in results))
        with self.assertRaises(ValueError):
            LexicalRetriever("R1", fixture_rows() * 2, CONFIG)

    def test_rank_ties_positive_eligibility_nonfinite(self):
        retriever = LexicalRetriever("R1", list(reversed(fixture_rows())), CONFIG).fit()
        self.assertEqual([r.chunk_id for r in retriever.rank([1, 1, 0, -1, 1], 10)], ["C0", "C3", "C4"])
        for scores in ([1, 2], [1, 1, float("nan"), 1, 1], [1, 1, float("inf"), 1, 1]):
            with self.assertRaises(ValueError):
                retriever.rank(scores, 5)


class IndexTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        paths = list(CONFIG["snapshot"]["artifact_sha256"]) + [CONFIG["snapshot"]["manifest_path"], "experiments/configs/retrieval_protocol_v1.toml", "experiments/configs/lexical_environment.lock.txt"]
        for relative in paths:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)

    def tearDown(self):
        self.temporary.cleanup()

    def test_real_corpus_snapshot_and_serialization(self):
        verify_snapshot(self.root, CONFIG)
        rows, statistics = prepare(self.root, CONFIG)
        self.assertEqual(statistics["chunks"], 371)
        self.assertEqual(statistics["emitted_fields"], {"title": 318, "heading": 63, "category": 371})
        self.assertEqual(statistics["format_distribution"], {"DOCX": 187, "PDF": 79, "TXT": 42, "XLSX": 63})
        self.assertEqual(statistics["empty_documents"], 0)
        self.assertEqual(statistics["duplicate_serialized_documents"], 0)
        for row in rows:
            if row["format"] == "XLSX":
                for marker in ("Sheet:", "Header:", "Row:"):
                    self.assertIn(marker, row["text"])

    def test_roundtrip_repeat_shared_universe_and_tamper(self):
        manifests = {method: build(self.root, method) for method in ("R1", "R2")}
        self.assertEqual(audit(self.root)["status"], "PASS")
        for method in ("R1", "R2"):
            loaded = load(self.root, method)
            rebuilt = LexicalRetriever(method, loaded.rows, CONFIG).fit()
            self.assertEqual(loaded.retrieve("koordinasi vendor akad", 5), rebuilt.retrieve("koordinasi vendor akad", 5))
            self.assertTrue(build(self.root, method)["reused_verified_index"])
            second = build(self.root, method, method + "-repeat")
            self.assertEqual(second["artifact_sha256_derived"], manifests[method]["artifact_sha256_derived"])
        target = self.root / "experiments/indexes/R1/model.json"
        target.write_bytes(target.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            load(self.root, "R1")

    def test_protected_changes_and_output_path_rejected(self):
        path = self.root / CONFIG["snapshot"]["chunks_path"]
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "Protected artifact"):
            build(self.root, "R1")
        with self.assertRaises(ValueError):
            build(self.root, "R1", "../../data")

    def test_stale_protocol_or_incomplete_index_rejected(self):
        build(self.root, "R2")
        manifest = self.root / "experiments/indexes/R2/manifest.json"
        state = json.loads(manifest.read_text(encoding="utf-8"))
        state["completion_status"] = "INCOMPLETE"
        manifest.write_text(json.dumps(state), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Stale/incompatible"):
            load(self.root, "R2")
        state["completion_status"] = "COMPLETE"
        manifest.write_text(json.dumps(state), encoding="utf-8")
        protocol = self.root / "experiments/configs/retrieval_protocol_v1.toml"
        protocol.write_bytes(protocol.read_bytes() + b"\n# changed\n")
        with self.assertRaisesRegex(ValueError, "Stale/incompatible"):
            load(self.root, "R2")

    def test_cli_build_retrieve_inspect_audit_and_errors(self):
        def command(*args):
            return subprocess.run([sys.executable, "-B", "-m", "wo_retrieval.retrieval.cli", *args, "--root", str(self.root)], capture_output=True, encoding="utf-8")
        for method in ("R1", "R2"):
            result = command("build", "--method", method)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = command("retrieve", "--method", method, "--query", "vendor", "--top-k", "5")
            self.assertEqual(result.returncode, 0, result.stderr)
            ranking = json.loads(result.stdout)
            self.assertEqual(len(ranking), 5)
            inspection = command("inspect", "--method", method, "--chunk-id", ranking[0]["chunk_id"])
            self.assertEqual(json.loads(inspection.stdout)["document_id"], ranking[0]["document_id"])
        self.assertEqual(json.loads(command("audit").stdout)["status"], "PASS")
        self.assertNotEqual(command("retrieve", "--method", "R1", "--query", "vendor", "--top-k", "0").returncode, 0)
        self.assertNotEqual(command("inspect", "--method", "R1", "--chunk-id", "UNKNOWN").returncode, 0)


if __name__ == "__main__":
    unittest.main()
