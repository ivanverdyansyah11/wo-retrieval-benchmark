"""Cloud preparation tests: no Torch import, tokenizer/model loading or inference."""
import ast
from copy import deepcopy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import numpy as np

from wo_retrieval import full_colab as full
from wo_retrieval.dense.index import load_vectors
from wo_retrieval.query_vectors.artifacts import contract, load_artifact
from wo_retrieval.query_vectors.offline import retrievers
from wo_retrieval.versioned_dense import prepare_v2
from wo_retrieval.versioned_dense import read_binding
from importlib.metadata import version, PackageNotFoundError

ROOT=Path(__file__).resolve().parents[1]
PACKAGE_PATH=ROOT/"experiments/portable/v2_bge_m3/full_input_package.zip"


def reseal(value,key="package_fingerprint"):
    value.pop(key,None);value[key]=full.digest(value);return value


class FullColabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package,_=full.read_input(PACKAGE_PATH)
        # CPU exchange fixtures use the frozen V2 artifacts, not a local encoding installation.
        binding,preparation=read_binding(ROOT)
        config,rows,statistics=preparation.bind_v2(ROOT)
        bm25=preparation.verify_index(ROOT/binding['r2_index'],rows,config,
                                     preparation.identity(ROOT,config,'R2'),statistics)
        directory=ROOT/binding['r3_index']
        manifest=json.loads((directory/'manifest.json').read_text(encoding='utf8'))
        mapping=json.loads((directory/'rows.json').read_text(encoding='utf8'))
        load_vectors(directory,manifest['identity'],mapping)
        cls.context=dict(root=ROOT,binding=binding,config=config,rows=rows,mapping=mapping,
                         bm25=bm25,identity=manifest['identity'],local=None)
        full.verify_local(cls.context,cls.package)
        versions={**full.PINS,"torch":"fixture+cu126","numpy":"fixture"}
        cls.environment={"synthetic_fixture":True,"platform":"Linux","python":"3.12.14",
            "gpu_name":"SYNTHETIC_NOT_REAL_GPU","cuda_runtime":"12.6","precision":"float16",
            "session_id":"synthetic-only","environment_validation":"PASS","pip_check":"PASS","cuda_smoke":"PASS",
            "dependency_versions":versions,"full_environment_lock":[n+"=="+v for n,v in versions.items()]}
        cls.corpus=np.zeros((371,1024),dtype=np.float32)
        cls.corpus[np.arange(371),np.arange(371)]=1
        cls.raw=np.zeros((18,1024),dtype=np.float32);cls.raw[:,0]=np.float32(.9998)
        cls.queries=full.unit(cls.raw)
        cls.tokens={k:[r["actual_tokens"] for r in cls.package[k]] for k in ("corpus","queries")}

    def output(self,path):
        return full.write_output(path,self.package,self.corpus,self.queries,self.raw,self.environment,{},self.tokens)

    def mutate_zip(self,source,target,change):
        with zipfile.ZipFile(source) as archive:items={n:archive.read(n) for n in archive.namelist()}
        change(items)
        full.write_zip(target,items)

    def test_input_counts_hashes_serialization_and_exclusions(self):
        full.verify_local(self.context,self.package)
        self.assertEqual(self.package["counts"],{"documents":50,"corpus":371,"queries":18,"provenance_pointers":42})
        self.assertEqual([r["text"] for r in self.context["rows"]],[r["text"] for r in self.package["corpus"]])
        _,files=full.read_input(PACKAGE_PATH)
        self.assertEqual(set(files),full.INPUT_ENTRIES)
        self.assertNotIn("qrels",str(self.package["source_artifact_sha256"]))
        for kind,key in (("corpus","chunk_id"),("queries","query_id")):
            for mutation in ("missing","duplicate","hash","order"):
                with self.subTest(kind=kind,mutation=mutation):
                    p=deepcopy(self.package)
                    if mutation=="missing":p[kind].pop()
                    elif mutation=="duplicate":p[kind][1]=p[kind][0]
                    elif mutation=="hash":p[kind][0]["text_sha256"]="0"*64
                    else:p[kind][0]["order"]=7
                    with self.assertRaises(ValueError):full.validate_input(reseal(p))

    def test_valid_exchange_preserves_raw_query_stage_and_no_local_reuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"good.zip";manifest=self.output(path)
            arrays,readback=full.read_output(path,self.package,allow_synthetic=True)
            np.testing.assert_array_equal(arrays["corpus.npy"],self.corpus)
            np.testing.assert_array_equal(arrays["query_encoder_output.npy"],self.raw)
            np.testing.assert_array_equal(arrays["queries.npy"],full.unit(self.raw))
            self.assertEqual(manifest,readback);self.assertEqual(manifest["reused_local_vectors"],0)
            with self.assertRaises(ValueError):full.read_output(path,self.package)
            with self.assertRaises(FileExistsError):self.output(path)

    def test_contract_and_mapping_rejections(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"good.zip";self.output(source)
            cases=[("completion_status","INCOMPLETE"),("snapshot_fingerprint","bad"),("inference",{"model_revision":"main"}),
                ("input_package_fingerprint","stale"),("reused_local_vectors",369),
                ("corpus_mapping",self.package["corpus"][:-1]),("query_mapping",self.package["queries"][:-1])]
            cases += [("query_mapping",[self.package["queries"][0]]*18)]
            changed=deepcopy(self.package["queries"]);changed[0]["text_sha256"]="bad"
            cases.append(("query_mapping",changed))
            changed=deepcopy(self.package["corpus"]);changed[0]["text_sha256"]="bad"
            cases.append(("corpus_mapping",changed))
            for i,(key,value) in enumerate(cases):
                with self.subTest(key=key):
                    def change(items):
                        m=full.parse_json(items["manifest.json"]);m[key]=value
                        items["manifest.json"]=full.canonical(reseal(m,"manifest_fingerprint"))
                    target=Path(tmp)/f"bad{i}.zip";self.mutate_zip(source,target,change)
                    with self.assertRaises(ValueError):full.read_output(target,self.package,True)

    def test_invalid_vectors_corruption_and_archive_rejections(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/"good.zip";self.output(source)
            bad=[np.zeros((371,1024),dtype=np.float32),self.corpus.astype(np.float64),self.corpus[:,:1000],self.corpus*2]
            for number in (np.nan,np.inf):
                v=self.corpus.copy();v[0,0]=number;bad.append(v)
            for i,value in enumerate(bad):
                def change(items):
                    items["corpus.npy"]=full.npy(value)
                    m=full.parse_json(items["manifest.json"])
                    m["artifact_sha256"]["corpus.npy"]=__import__('hashlib').sha256(items["corpus.npy"]).hexdigest()
                    items["manifest.json"]=full.canonical(reseal(m,"manifest_fingerprint"))
                target=Path(tmp)/f"vectors{i}.zip";self.mutate_zip(source,target,change)
                with self.subTest(i=i),self.assertRaises(ValueError):full.read_output(target,self.package,True)
            for i,change in enumerate((lambda items:items.pop("queries.npy"),lambda items:items.update({"../escape":"bad"}),
                                      lambda items:items.update({"corpus.npy":b"bad"}))):
                target=Path(tmp)/f"zip{i}.zip";self.mutate_zip(source,target,change)
                with self.assertRaises(ValueError):full.read_output(target,self.package,True)
            duplicate=Path(tmp)/"duplicate.zip"
            with zipfile.ZipFile(source) as a,zipfile.ZipFile(duplicate,"w") as b:
                for n in a.namelist():b.writestr(n,a.read(n))
                b.writestr("manifest.json",a.read("manifest.json"))
            with self.assertRaises(ValueError):full.read_output(duplicate,self.package,True)

    def test_notebook_unexecuted_ast_and_native_runtime(self):
        nb=json.loads((ROOT/"experiments/portable/v2_bge_m3/bge_m3_v2_full_colab.ipynb").read_text(encoding="utf8"))
        code=[c for c in nb["cells"] if c["cell_type"]=="code"]
        self.assertEqual(len(code),9)
        source="\n".join("".join(c["source"]) for c in code)
        for c in code:
            ast.parse("".join(c["source"]));self.assertIsNone(c["execution_count"]);self.assertEqual(c["outputs"],[])
        for forbidden in ("EnvBuilder","ensurepip","exist_ok=False","apt-get","--force-reinstall","--no-deps"):
            self.assertNotIn(forbidden,source)
        self.assertIn(full.file_hash(PACKAGE_PATH),source)
        self.assertIn(self.package["package_fingerprint"],source)

    def fixture_root(self,tmp):
        root=Path(tmp)
        for name in self.package["source_artifact_sha256"]:
            target=root/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes())
        package=root/"experiments/portable/v2_bge_m3/full_input_package.zip"
        package.parent.mkdir(parents=True,exist_ok=True);package.write_bytes(PACKAGE_PATH.read_bytes())
        for method in ("R1","R2"):
            path=root/"experiments/indexes/v2_ai_corrected"/method;path.mkdir(parents=True,exist_ok=True)
            (path/"sentinel").write_text("DO NOT CHANGE")
        (root/"v1_sentinel").write_text("V1 UNCHANGED")
        return root,package,{**self.context,"root":root}

    def test_atomic_full_import_and_shared_r3_r4_compatibility(self):
        original=full.validate_environment
        with tempfile.TemporaryDirectory() as tmp:
            root,package,ctx=self.fixture_root(tmp);cloud=root/"cloud.zip";self.output(cloud)
            with patch("wo_retrieval.versioned_dense.prepare_v2",return_value=ctx),patch.object(full,"validate_environment",side_effect=lambda e,allow_synthetic=False:original(e,True)):
                result=full.import_output(root,package,cloud)
                self.assertEqual(result["local_vector_reuse"],0)
                components=full.load_components(root);bm,vectors,manifest,config,_=components
                np.testing.assert_array_equal(vectors,self.corpus)
                self.assertEqual(manifest["new_vectors"],371);self.assertEqual(manifest["reused_verified_vectors"],0)
                for i,q in enumerate(self.package["queries"]):
                    directory=root/ctx["binding"]["r3_index"]/"query_vectors"/q["query_id"]
                    raw,_=load_artifact(directory,contract(manifest),q["query_id"],q["text"])
                    np.testing.assert_array_equal(raw,self.raw[i:i+1])
                    dense,hybrid=retrievers(components,directory,q["query_id"],q["text"])
                    results,breakdown,parts=hybrid.retrieve_with_diagnostics(q["text"],5)
                    self.assertEqual(dense.retrieve(q["text"],371),parts["R3"])
                    self.assertEqual(len(parts["R3"]),371)
                    self.assertEqual(bm.retrieve(q["text"],371),parts["R2"])
                    for b in breakdown:self.assertAlmostEqual(b["rrf_score"],b["bm25_contribution"]+b["dense_contribution"])
                    with self.assertRaises(ValueError):load_artifact(directory,contract(manifest),q["query_id"],q["text"]+" changed")
                with self.assertRaises(FileExistsError):full.import_output(root,package,cloud)
            self.assertEqual((root/"v1_sentinel").read_text(),"V1 UNCHANGED")
            for method in ("R1","R2"):self.assertEqual((root/"experiments/indexes/v2_ai_corrected"/method/"sentinel").read_text(),"DO NOT CHANGE")

    def test_failed_import_remains_unpublished_incomplete(self):
        original=full.validate_environment
        with tempfile.TemporaryDirectory() as tmp:
            root,package,ctx=self.fixture_root(tmp);cloud=root/"cloud.zip";self.output(cloud)
            with patch("wo_retrieval.versioned_dense.prepare_v2",return_value=ctx),patch.object(full,"validate_environment",side_effect=lambda e,allow_synthetic=False:original(e,True)),patch("wo_retrieval.query_vectors.artifacts.load_artifact",side_effect=ValueError("fixture failure")):
                with self.assertRaises(ValueError):full.import_output(root,package,cloud)
            self.assertFalse((root/ctx["binding"]["r3_index"]).exists())
            partial=list((root/"experiments/indexes/v2_ai_corrected").glob("R3.full-incomplete-*/index/manifest.json"))
            self.assertEqual(len(partial),1)
            self.assertEqual(json.loads(partial[0].read_text())["completion_status"],"INCOMPLETE")

    def test_checkpoint_resume_without_model_and_stale_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            run=object.__new__(full.CloudRun);run.work=Path(tmp);run.package=self.package;run.env=self.environment;run.timings={}
            run.tokens={}
            with self.assertRaises(RuntimeError):run.load()  # Stops before Torch import/weights.
            run.encode=lambda text:self.raw[:1]
            run.encode_group("queries")
            np.testing.assert_array_equal(run.queries,self.queries)
            with self.assertRaises(RuntimeError):run.encode_group("queries")
            run.encode=lambda text:(_ for _ in ()).throw(AssertionError("Resume must not encode complete rows"))
            run.encode_group("queries",resume=True)
            state=run.work/"queries_partial/progress.json"
            original=json.loads(state.read_text())
            for key in ("model_revision","environment","mapping"):
                value=deepcopy(original);value["identity"][key]="stale";state.write_bytes(full.canonical(value))
                with self.subTest(key=key),self.assertRaises(RuntimeError):run.encode_group("queries",True)
            value=deepcopy(original);value["completed"][0]["input"]=self.package["queries"][1]
            state.write_bytes(full.canonical(value))
            with self.assertRaises(RuntimeError):run.encode_group("queries",True)
            value=deepcopy(original);vector=run.work/"queries_partial/0000.npy"
            vector.write_bytes(full.npy(np.zeros((1,1000),dtype=np.float32)))
            value["completed"][0]["sha256"]=full.file_hash(vector);state.write_bytes(full.canonical(value))
            with self.assertRaises(ValueError):run.encode_group("queries",True)


class LocalEncodingEnvironmentTests(unittest.TestCase):
    def test_pinned_local_encoding_provenance(self):
        for name in ('torch','FlagEmbedding','transformers'):
            try:version(name)
            except PackageNotFoundError:self.skipTest('Local encoding provenance requires '+name+' metadata; CPU quick start excludes it')
        binding=json.loads((ROOT/'experiments/configs/dense_v2_binding.json').read_text(encoding='utf8'))
        lock=json.loads((ROOT/'experiments/configs/ml_environment.lock.json').read_text(encoding='utf8'))['model']
        if not Path(binding['v1_dense_index']).is_dir() or not Path(lock['snapshot_path']).is_dir():
            self.skipTest('Local encoding provenance requires the historical V1 cache and checkpoint files')
        flag=ROOT/'.venv-ml/Lib/site-packages/FlagEmbedding'
        if not flag.is_dir():self.skipTest('Historical official FlagEmbedding implementation files unavailable')
        context=prepare_v2(ROOT)
        package,_=full.read_input(PACKAGE_PATH)
        full.verify_local(context,package)
        self.assertEqual(len(context['rows']),371)


if __name__=="__main__":unittest.main()
