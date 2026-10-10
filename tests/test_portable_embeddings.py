"""Exchange/import fixtures only; no network, neural imports or GPU execution."""
import ast
from copy import deepcopy
from hashlib import sha256
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import numpy as np

from wo_retrieval import portable_embeddings as exchange
from wo_retrieval.dense.index import load_vectors
from wo_retrieval import versioned_dense

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "experiments/portable/v2_bge_m3/input_package.zip"


def unit(axis):
    vector = np.zeros((1, 1024), np.float32)
    vector[0, axis] = 1
    return vector


class ExchangeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = exchange.read_input(INPUT)
        self.vectors = {k: unit(i+1) for i, k in enumerate(exchange.IDS)}
        self.env = {"synthetic_fixture": True, "platform": "Linux", "dependency_versions": exchange.DEPENDENCIES,
                    "gpu_name": "SYNTHETIC_NOT_A_GPU_RUN", "cuda_runtime": "fixture-only", "precision": "float16"}
        self.path = self.root / "synthetic.zip"
        exchange.write_output(self.path, self.package, self.vectors, self.env, {"synthetic_fixture": True})

    def mutate(self, mutation=None, vector=None, missing=None, extra=False):
        with zipfile.ZipFile(self.path) as archive:
            files = {i.filename: archive.read(i) for i in archive.infolist()}
        manifest = json.loads(files["manifest.json"])
        if mutation:
            mutation(manifest)
        if vector is not None:
            raw = io.BytesIO()
            np.save(raw, vector, allow_pickle=False)
            name = exchange.IDS[0] + ".npy"
            files[name] = raw.getvalue()
            manifest["artifact_sha256"][name] = sha256(files[name]).hexdigest()
        manifest["manifest_fingerprint"] = exchange.digest({k:v for k,v in manifest.items() if k != "manifest_fingerprint"})
        files["manifest.json"] = exchange.canonical(manifest)
        if missing:
            files.pop(missing)
        if extra:
            files["../escape"] = b"no extraction allowed"
        target = self.root / ("mutation-" + str(len(list(self.root.iterdir()))) + ".zip")
        exchange.write_zip(target, files)
        return target

    def test_input_exact_hashes_and_runtime(self):
        self.assertEqual([r["actual_tokens"] for r in self.package["inputs"]], [218,169])
        self.assertEqual(self.package["runtime_sha256"], exchange.file_hash(Path(exchange.__file__)))
        audit = json.loads((ROOT / "experiments/indexes/v2_ai_corrected/dense_reuse_eligibility.json").read_text())
        expected = {r["chunk_id"]: r["v2_input_sha256"] for r in audit["rows"] if r["status"] == "REQUIRES_REEMBEDDING"}
        self.assertEqual({r["chunk_id"]:r["input_sha256"] for r in self.package["inputs"]},expected)

    def test_input_corruption_and_duplicates_rejected(self):
        for mutation in (lambda p:p["inputs"][0].update(input_sha256="wrong"),
                         lambda p:p["inputs"][0].update(snapshot_fingerprint="wrong"),
                         lambda p:p["inputs"].append(p["inputs"][0]),
                         lambda p:p["inference"].update(max_length=128)):
            package = deepcopy(self.package)
            mutation(package)
            package["package_fingerprint"] = exchange.digest({k:v for k,v in package.items() if k != "package_fingerprint"})
            with self.assertRaises(ValueError):
                exchange.validate_input(package)

    def test_valid_synthetic_readback_and_production_rejection(self):
        vectors, _ = exchange.read_output(self.path,self.package,allow_synthetic=True)
        for key in exchange.IDS:
            np.testing.assert_array_equal(vectors[key],self.vectors[key])
        with self.assertRaisesRegex(ValueError,"Synthetic"):
            exchange.read_output(self.path,self.package)

    def test_snapshot_model_config_hash_mismatch(self):
        mutations = [lambda m:m.update(snapshot_fingerprint="wrong"),
                     lambda m:m["inference"].update(model_revision="wrong"),
                     lambda m:m["inference"].update(precision="float32"),
                     lambda m:m["rows"][0].update(input_sha256="wrong"),
                     lambda m:m.update(input_package_fingerprint="wrong"),
                     lambda m:m["model_file_hashes"].update({"tokenizer.json":"wrong"}),
                     lambda m:m["encoding_environment"]["dependency_versions"].update(torch="CPU_WRONG")]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                with self.assertRaises(ValueError):
                    exchange.read_output(self.mutate(mutation),self.package,allow_synthetic=True)

    def test_incomplete_duplicate_mapping_rejected(self):
        for mutation in (lambda m:m.update(completion_status="INCOMPLETE"),
                         lambda m:m["rows"].append(m["rows"][0]),
                         lambda m:m["rows"][1].update(chunk_id=exchange.IDS[0])):
            with self.assertRaises(ValueError):
                exchange.read_output(self.mutate(mutation),self.package,allow_synthetic=True)

    def test_missing_corrupt_extra_archive_rejected(self):
        with self.assertRaises(ValueError):
            exchange.read_output(self.mutate(missing=exchange.IDS[0]+".npy"),self.package,True)
        with self.assertRaises(ValueError):
            exchange.read_output(self.mutate(extra=True),self.package,True)
        bad=self.mutate(lambda m:m["artifact_sha256"].update({exchange.IDS[0]+".npy":"wrong"}))
        with self.assertRaisesRegex(ValueError,"checksum"):
            exchange.read_output(bad,self.package,True)
        duplicate=self.root/"duplicate.zip"
        with zipfile.ZipFile(duplicate,"w") as archive:
            archive.writestr("manifest.json",b"{}")
            archive.writestr("manifest.json",b"{}")
        with self.assertRaises(ValueError):
            exchange.read_output(duplicate,self.package,True)

    def test_invalid_dimensions_dtype_finite_normalization(self):
        for vector in (np.zeros((1,1024),np.float32), np.ones((1,1024),np.float32),
                       np.full((1,1024),np.nan,np.float32), np.full((1,1024),np.inf,np.float32),
                       np.ones((1,1000),np.float32), unit(1).astype(np.float64)):
            with self.subTest(shape=vector.shape):
                with self.assertRaises(ValueError):
                    exchange.read_output(self.mutate(vector=vector),self.package,True)

    def test_notebook_json_code_cells_unexecuted(self):
        notebook=json.loads((ROOT/"experiments/portable/v2_bge_m3/bge_m3_v2_colab.ipynb").read_text())
        self.assertEqual(notebook["nbformat"],4)
        for cell in notebook["cells"]:
            if cell["cell_type"]=="code":
                ast.parse("".join(cell["source"]))
                self.assertIsNone(cell["execution_count"])
                self.assertEqual(cell["outputs"],[])

    def test_369_plus_two_import_atomic_isolation(self):
        real_rows=json.loads((ROOT/"experiments/indexes/v2_ai_corrected/R2/documents.json").read_text())
        lengths=json.loads((ROOT/"experiments/indexes/v2_ai_corrected/dense_reuse_eligibility.json").read_text())["target_row_mapping"]
        source=np.repeat(unit(0),371,axis=0)
        receipts=[{"chunk_id":r["chunk_id"],"document_id":r["document_id"],"v1_row_index":i,"v2_row_index":i,
            "v1_input_sha256":r["text_sha256"] if r["chunk_id"] not in exchange.IDS else "synthetic-old",
            "v2_input_sha256":r["text_sha256"],"vector_raw_float32_sha256":sha256(source[i].tobytes()).hexdigest(),
            "status":"REQUIRES_REEMBEDDING" if r["chunk_id"] in exchange.IDS else "REUSABLE_VERIFIED"} for i,r in enumerate(real_rows)]
        identity={k:self.package["inference"][k] for k in ("model_id","model_revision","device","precision","max_length","normalization","dimension")}
        identity.update(row_mapping_hash=exchange.digest(lengths), model_file_hashes=self.package["model_file_hashes"],
                        official_inference_file_hashes=self.package["official_inference_file_hashes"])
        context={"root":self.root,"binding":{"r3_index":"experiments/indexes/v2_ai_corrected/R3","eligibility_manifest_sha256":"SYNTHETIC"},
            "rows":real_rows,"mapping":lengths,"identity":identity,"source_vectors":source,
            "audit":{"rows":receipts,"source_manifest_sha256":"SYNTHETIC_NOT_REAL"},"bm25":None,"config":{"snapshot":{"id":"SYNTHETIC_V2"}},"local":self.root}
        cfg=self.root/"experiments/configs/dense_v2_binding.json"
        cfg.parent.mkdir(parents=True)
        cfg.write_text("SYNTHETIC_FIXTURE")
        v1=self.root/"experiments/indexes/R3/sentinel"
        v1.parent.mkdir(parents=True)
        v1.write_bytes(b"KEEP_V1")
        real_reader=exchange.read_output
        # Test-only allowance; production importer rejects synthetic_fixture=True.
        with patch.object(versioned_dense,"prepare_v2",return_value=context), \
                patch.object(exchange,"read_output",side_effect=lambda path,p:real_reader(path,p,True)):
            manifest=exchange.import_output(self.root,INPUT,self.path)
        matrix,_=load_vectors(self.root/context["binding"]["r3_index"],identity,lengths)
        self.assertEqual(matrix.shape,(371,1024))
        self.assertEqual(manifest["reused_verified_vectors"],369)
        for i,row in enumerate(real_rows):
            if row["chunk_id"] in exchange.IDS:
                np.testing.assert_array_equal(matrix[i],self.vectors[row["chunk_id"]][0])
            else:
                self.assertEqual(matrix[i].tobytes(),source[i].tobytes())
        self.assertEqual(v1.read_bytes(),b"KEEP_V1")
        self.assertTrue(all(m["mixed_hardware"] for m in manifest["new_embedding_metadata"].values()))


if __name__=="__main__":
    unittest.main()
