"""Full V2 cloud exchange; local export/import/scoring never loads a neural model."""
import argparse
from datetime import datetime, timezone
import importlib.metadata as metadata
import io
import json
import os
from pathlib import Path
import platform
import sys
from time import perf_counter
from uuid import uuid4

import numpy as np

if __package__:
    from .portable_embeddings import canonical, digest, file_hash, parse_json, read_zip, write_zip
    from .retrieval.text import normalize
else:
    from exchange import canonical, digest, file_hash, parse_json, read_zip, write_zip
    from shared_text import normalize

SCHEMA = "wo_colab_full_v2_v1"
SNAPSHOT = "WO-CORPUS-V2-AI-CORRECTED-PILOT-001"
FINGERPRINT = "78cd4e407bb9bbad1766d0ec3827931381a469695b995a1acb8bbad1444addc6"
QUERY_CONTRACT = "shared_normalize_v1: NFC, CRLF/CR to LF, outer strip; no prompt"
PINS = {"FlagEmbedding": "1.4.2", "transformers": "4.57.6", "tokenizers": "0.22.2",
        "sentence-transformers": "5.2.0", "peft": "0.18.1"}
INPUT_ENTRIES = {"inputs.json", "runtime.py", "exchange.py", "shared_text.py"}
OUTPUT_ENTRIES = {"manifest.json", "corpus.npy", "queries.npy", "query_encoder_output.npy"}


def unit(values):
    values = np.asarray(values, dtype=np.float32)
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    if not np.isfinite(values).all() or not np.isfinite(norms).all() or np.any(norms <= 0):
        raise ValueError("Nonfinite/zero vectors")
    return values / norms


def matrix(values, count, normalized=True):
    if not isinstance(values, np.ndarray) or values.dtype != np.float32 or values.shape != (count, 1024):
        raise ValueError("Wrong vector count/dimension/dtype")
    unit(values)
    tolerance = 1e-5 if normalized else .002  # Official FP16 normalization before float32 conversion.
    if not np.allclose(np.linalg.norm(values, axis=1), 1, atol=tolerance, rtol=0):
        raise ValueError("Non-normalized vectors")
    return values


def fingerprinted(value, field):
    if value.get(field) != digest({k: v for k, v in value.items() if k != field}):
        raise ValueError("Fingerprint mismatch: " + field)


def validate_input(package):
    fingerprinted(package, "package_fingerprint")
    if (package.get("schema") != SCHEMA or package.get("snapshot_id") != SNAPSHOT
            or package.get("snapshot_fingerprint") != FINGERPRINT
            or package.get("serialization_version") != "wo_operational_context_dedup_v1"
            or package.get("query_input_contract") != QUERY_CONTRACT
            or package.get("dependency_pins") != PINS):
        raise ValueError("Snapshot/serializer/query/dependency contract mismatch")
    expected = {"model_id": "BAAI/bge-m3", "model_revision": "5617a9f61b028005a4858fdac845db406aefb181",
        "device": "cuda:0", "precision": "float16", "batch_size": 1, "max_length": 640, "dimension": 1024,
        "return_dense": True, "return_sparse": False, "return_colbert_vecs": False,
        "pooling_method": "cls", "storage_dtype": "float32", "truncation": False,
        "normalization": "official L2; convert output to float32 and L2-normalize again before score/storage"}
    if package.get("inference") != expected:
        raise ValueError("Model/config mismatch")
    for kind, count, id_key in (("corpus", 371, "chunk_id"), ("queries", 18, "query_id")):
        records = package[kind]
        ids = [r[id_key] for r in records]
        if len(records) != count or len(set(ids)) != count or ids != sorted(ids):
            raise ValueError("Missing/duplicate/unordered " + kind)
        for i, row in enumerate(records):
            text = row["text"]
            if (row["order"] != i or not normalize(text) or row["text_sha256"] != digest_text(text)
                    or row["effective_input_sha256"] != digest_text(normalize(text))
                    or type(row["actual_tokens"]) is not int or not 0 < row["actual_tokens"] <= 640):
                raise ValueError("Input text/hash/order/tokens mismatch")
            if kind == "corpus":
                if row["document_id"] != row["chunk_id"].rsplit("-C", 1)[0] or row["snapshot_fingerprint"] != FINGERPRINT:
                    raise ValueError("Corpus document/snapshot mismatch")
            elif row["validation_status"] != "draft_pending_expert_review":
                raise ValueError("Queries must remain DRAFT")
    if len({r["document_id"] for r in package["corpus"]}) != 50:
        raise ValueError("Expected 50 documents")
    if package.get("counts") != {"documents": 50, "corpus": 371, "queries": 18, "provenance_pointers": 42}:
        raise ValueError("Expected dataset counts mismatch")
    if [q["query_id"] for q in package["queries"]] != [f"WO-DEV-{i:03d}" for i in range(1,19)]:
        raise ValueError("Unexpected query IDs")
    return package


def digest_text(text):
    from hashlib import sha256
    return sha256(text.encode("utf8")).hexdigest()


def read_input(path):
    files = read_zip(path, INPUT_ENTRIES, 4*1024**2)
    package = validate_input(parse_json(files["inputs.json"]))
    if set(package["runtime_files_sha256"]) != INPUT_ENTRIES - {"inputs.json"}:
        raise ValueError("Runtime file set mismatch")
    from hashlib import sha256
    if any(sha256(files[n]).hexdigest() != h for n, h in package["runtime_files_sha256"].items()):
        raise ValueError("Runtime checksum mismatch")
    return package, files


def export_inputs(root, output):
    from .versioned_dense import prepare_v2
    from tokenizers import Tokenizer
    root = Path(root).resolve()
    ctx = prepare_v2(root)
    tokenizer = Tokenizer.from_file(str(ctx["local"] / "tokenizer.json"))
    tokenizer.no_padding(); tokenizer.no_truncation()
    corpus = []
    for i, (row, mapped) in enumerate(zip(ctx["rows"], ctx["mapping"], strict=True)):
        count = len(tokenizer.encode(normalize(row["text"]), add_special_tokens=True).ids)
        if count != mapped["token_length"]:
            raise ValueError("Actual tokenizer/serializer parity mismatch")
        corpus.append({"order": i, "chunk_id": row["chunk_id"], "document_id": row["document_id"],
            "text": row["text"], "text_sha256": row["text_sha256"], "effective_input_sha256": digest_text(normalize(row["text"])),
            "actual_tokens": count, "snapshot_fingerprint": FINGERPRINT})
    query_path = root / "data/benchmark/development_queries_draft.jsonl"
    drafts = sorted([json.loads(line) for line in query_path.read_text(encoding="utf8").splitlines() if line], key=lambda q:q["query_id"])
    queries = [{"order": i, "query_id": q["query_id"], "text": q["text"], "text_sha256": digest_text(q["text"]),
        "effective_input_sha256": digest_text(normalize(q["text"])), "actual_tokens": len(tokenizer.encode(normalize(q["text"]), add_special_tokens=True).ids),
        "validation_status": q["validation_status"]} for i,q in enumerate(drafts)]
    provenance = root / "data/benchmark/development_query_provenance.jsonl"
    pointers = [json.loads(l) for l in provenance.read_text(encoding="utf8").splitlines() if l]
    pointer_count = sum(len(p.get("source_evidence_refs", [])) for p in pointers)
    if pointer_count != 42:
        raise ValueError("Expected 42 provenance pointers")
    from .portable_embeddings import read_input as read_previous_input
    old = read_previous_input(root / "experiments/portable/v2_bge_m3/input_package.zip")
    files = {"runtime.py": Path(__file__).read_bytes(), "exchange.py": (Path(__file__).parent/"portable_embeddings.py").read_bytes(),
             "shared_text.py": (Path(__file__).parent/"retrieval/text.py").read_bytes()}
    sources = [ctx["binding"]["snapshot_manifest"], ctx["config"]["snapshot"]["chunks_path"],
               "data/benchmark/development_queries_draft.jsonl", "data/benchmark/development_query_provenance.jsonl",
               "experiments/configs/retrieval_protocol_v1.toml", "experiments/configs/dense_v2_binding.json"]
    package = {"schema": SCHEMA, "snapshot_id": SNAPSHOT, "snapshot_fingerprint": FINGERPRINT,
        "serialization_version": ctx["identity"]["serializer_version"], "query_input_contract": QUERY_CONTRACT,
        "counts": {"documents":50,"corpus":371,"queries":18,"provenance_pointers":pointer_count},
        "corpus_status":"ai_corrected_pilot_not_human_validated", "corpus":corpus, "queries":queries,
        "inference": old["inference"], "dependency_pins":PINS, "local_dependency_versions":old["dependency_pins"],
        "model_file_hashes":ctx["identity"]["model_file_hashes"], "official_inference_file_hashes":ctx["identity"]["official_inference_file_hashes"],
        "source_artifact_sha256":{n:file_hash(root/n) for n in sources}, "runtime_files_sha256":{n:__import__('hashlib').sha256(v).hexdigest() for n,v in files.items()}}
    package["package_fingerprint"] = digest(package)
    validate_input(package)
    write_zip(output, {"inputs.json":canonical(package), **files})
    read_input(output)
    return package


def validate_environment(env, allow_synthetic=False):
    if env.get("synthetic_fixture") is not False and not allow_synthetic:
        raise ValueError("Synthetic/unknown GPU output rejected")
    if (env.get("platform") != "Linux" or not str(env.get("python", "")).startswith("3.12.")
            or not env.get("gpu_name") or not env.get("cuda_runtime") or env.get("precision") != "float16"
            or not env.get("session_id") or env.get("environment_validation") != "PASS"
            or env.get("pip_check") != "PASS" or env.get("cuda_smoke") != "PASS"):
        raise ValueError("Incomplete GPU/environment verification")
    versions = env["dependency_versions"]
    if any(versions.get(n) != v for n,v in PINS.items()) or not versions.get("torch") or not versions.get("numpy"):
        raise ValueError("Dependency compatibility identity mismatch")
    if not isinstance(env.get("full_environment_lock"), list) or not env["full_environment_lock"]:
        raise ValueError("Missing environment lock")
    lock={line.split("==",1)[0].casefold().replace("_","-"):line.split("==",1)[1]
          for line in env["full_environment_lock"] if isinstance(line,str) and "==" in line}
    if any(lock.get(n.casefold().replace("_","-"))!=v for n,v in versions.items()):
        raise ValueError("Environment lock/version mismatch")
    return env


def npy(vector):
    stream = io.BytesIO(); np.save(stream, vector, allow_pickle=False)
    return stream.getvalue()


def dependency_deviations(package,env):
    actual={line.split("==",1)[0].casefold().replace("_","-"):line.split("==",1)[1]
            for line in env["full_environment_lock"] if "==" in line}
    return {name:{"local":version,"colab":actual.get(name.casefold().replace("_","-"))}
            for name,version in package["local_dependency_versions"].items()
            if version!=actual.get(name.casefold().replace("_","-"))}


def write_output(path, package, corpus, queries, raw_queries, env, timings, tokens):
    validate_input(package); validate_environment(env, allow_synthetic=True)
    matrix(corpus,371); matrix(queries,18); matrix(raw_queries,18,False)
    if not np.array_equal(unit(raw_queries), queries):
        raise ValueError("Query raw/project-normalized stage mismatch")
    if tokens != {k:[r["actual_tokens"] for r in package[k]] for k in ("corpus","queries")}:
        raise ValueError("Actual tokenizer mismatch/truncation")
    artifacts = {"corpus.npy":npy(corpus),"queries.npy":npy(queries),"query_encoder_output.npy":npy(raw_queries)}
    manifest = {"schema":SCHEMA,"completion_status":"COMPLETE","input_package_fingerprint":package["package_fingerprint"],
        "snapshot_id":SNAPSHOT,"snapshot_fingerprint":FINGERPRINT,"inference":package["inference"],
        "corpus_mapping":package["corpus"],"query_mapping":package["queries"],"token_counts":tokens,
        "query_input_contract":QUERY_CONTRACT,"serialization_version":package["serialization_version"],
        "model_file_hashes":package["model_file_hashes"],"official_inference_file_hashes":package["official_inference_file_hashes"],
        "runtime_files_sha256":package["runtime_files_sha256"],"encoding_environment":env,"timings":timings,
        "local_reference_dependency_versions":package["local_dependency_versions"],
        "dependency_deviations_from_local":dependency_deviations(package,env),
        "created_at_utc":datetime.now(timezone.utc).isoformat(),"reused_local_vectors":0,
        "numerical_bitwise_equivalence_with_local_gpu":"NOT TESTED",
        "artifact_sha256":{n:__import__('hashlib').sha256(v).hexdigest() for n,v in artifacts.items()}}
    manifest["manifest_fingerprint"] = digest(manifest)
    write_zip(path, {"manifest.json":canonical(manifest),**artifacts})
    return manifest


def read_output(path, package, allow_synthetic=False):
    validate_input(package)
    files = read_zip(path, OUTPUT_ENTRIES, 4*1024**2)
    manifest = parse_json(files["manifest.json"])
    fingerprinted(manifest,"manifest_fingerprint")
    if manifest.get("completion_status") != "COMPLETE" or manifest.get("schema") != SCHEMA or manifest.get("reused_local_vectors") != 0:
        raise ValueError("Partial/wrong/mixed artifact")
    for key in ("snapshot_id","snapshot_fingerprint","inference","query_input_contract","serialization_version",
                "model_file_hashes","official_inference_file_hashes","runtime_files_sha256"):
        if manifest.get(key) != package[key]:raise ValueError("Output contract mismatch: "+key)
    if (manifest.get("input_package_fingerprint") != package["package_fingerprint"]
            or manifest.get("corpus_mapping") != package["corpus"] or manifest.get("query_mapping") != package["queries"]
            or manifest.get("token_counts") != {k:[r["actual_tokens"] for r in package[k]] for k in ("corpus","queries")}):
        raise ValueError("Input/mapping/token mismatch")
    validate_environment(manifest["encoding_environment"],allow_synthetic)
    if (manifest.get("local_reference_dependency_versions")!=package["local_dependency_versions"]
            or manifest.get("dependency_deviations_from_local")!=dependency_deviations(package,manifest["encoding_environment"])):
        raise ValueError("Dependency deviation provenance mismatch")
    stamp=datetime.fromisoformat(manifest["created_at_utc"])
    if stamp.utcoffset() is None or stamp.utcoffset().total_seconds()!=0:raise ValueError("UTC timestamp required")
    if set(manifest["artifact_sha256"]) != OUTPUT_ENTRIES-{"manifest.json"}:raise ValueError("Checksum set mismatch")
    arrays={}
    for name,expected in manifest["artifact_sha256"].items():
        if __import__('hashlib').sha256(files[name]).hexdigest()!=expected:raise ValueError("Corrupted vector checksum")
        arrays[name]=np.load(io.BytesIO(files[name]),allow_pickle=False)
    matrix(arrays["corpus.npy"],371);matrix(arrays["queries.npy"],18);matrix(arrays["query_encoder_output.npy"],18,False)
    if not np.array_equal(unit(arrays["query_encoder_output.npy"]),arrays["queries.npy"]):raise ValueError("Query stage mismatch")
    return arrays,manifest


def cloud_identity(context, package, env):
    validate_environment(env)
    return {**context["identity"],"dependency_versions":env["dependency_versions"],
        "ml_environment_manifest_sha256":digest(env["full_environment_lock"]),
        "generation_mode":"full_colab_371_plus_18_no_local_reuse",
        "encoding_environment":env,"input_package_fingerprint":package["package_fingerprint"],
        "full_import_code_sha256":file_hash(Path(__file__))}


def import_output(root, input_path, output_path):
    from .versioned_dense import prepare_v2
    from .dense.index import load_vectors
    from .query_vectors.artifacts import contract, publish, load_artifact
    context=prepare_v2(root)
    root=Path(root).resolve(); destination=root/context["binding"]["r3_index"]
    if destination.exists():raise FileExistsError("R3 V2 exists; no automatic overwrite")
    package,_=read_input(input_path);arrays,exchange=read_output(output_path,package)
    output_sha256=file_hash(output_path)
    verify_local(context,package)
    identity=cloud_identity(context,package,exchange["encoding_environment"])
    work=destination.with_name("R3.full-incomplete-"+uuid4().hex);work.mkdir(parents=True)
    # Already project-normalized corpus vectors must not receive an extra L2 pass.
    from .dense.index import atomic_json,atomic_vector
    from .retrieval.lexical import write_json
    staging=work/"index";staging.mkdir()
    atomic_json(staging/"manifest.json",{"completion_status":"INCOMPLETE"})
    atomic_vector(staging/"vectors.npy",arrays["corpus.npy"]);write_json(staging/"rows.json",context["mapping"])
    manifest={"completion_status":"COMPLETE","identity":identity,"indexed_chunks":371,"shape":[371,1024],
        "timestamp_utc":datetime.now(timezone.utc).isoformat(),"missing_chunks":0,"duplicate_chunk_ids":0,"finite":True,
        "reused_verified_vectors":0,"new_vectors":371,"exchange_zip_sha256":output_sha256,
        "exchange_manifest":exchange,"artifact_sha256":{n:file_hash(staging/n) for n in ("vectors.npy","rows.json")}}
    try:
        atomic_json(staging/"manifest.json",manifest)
        load_vectors(staging,identity,context["mapping"])
        expected=contract(manifest)
        for i,q in enumerate(package["queries"]):
            encoding={k:package["inference"][k] for k in ("device","precision","batch_size","max_length")}
            encoding.update(actual_tokens_including_special=q["actual_tokens"],truncation=False,
                environment=exchange["encoding_environment"],input_package_fingerprint=package["package_fingerprint"],
                exchange_manifest_fingerprint=exchange["manifest_fingerprint"],vector_stage="BGEEncoder.encode output before project unit_vectors")
            path=staging/"query_vectors"/q["query_id"]
            publish(path,expected,q["query_id"],q["text"],arrays["query_encoder_output.npy"][i:i+1],encoding)
            load_artifact(path,expected,q["query_id"],q["text"])
        fresh=prepare_v2(root);verify_local(fresh,package)
        _,fresh_exchange=read_output(output_path,read_input(input_path)[0])
        if file_hash(output_path)!=output_sha256 or fresh_exchange!=exchange:raise ValueError("Exchange changed during import")
        if fresh["identity"]!=context["identity"]:raise ValueError("Local identity changed")
        staging.rename(destination)
    except BaseException:
        atomic_json(staging/"manifest.json",{**manifest,"completion_status":"INCOMPLETE"})
        raise
    work.rmdir()
    return {"status":"COMPLETE","index":str(destination),"shape":[371,1024],"queries":18,"local_vector_reuse":0}


def verify_local(context,package):
    root=context["root"]
    allowed={context["binding"]["snapshot_manifest"],context["config"]["snapshot"]["chunks_path"],
        "data/benchmark/development_queries_draft.jsonl","data/benchmark/development_query_provenance.jsonl",
        "experiments/configs/retrieval_protocol_v1.toml","experiments/configs/dense_v2_binding.json"}
    if set(package["source_artifact_sha256"])!=allowed:raise ValueError("Unexpected source artifact paths")
    for name,expected in package["source_artifact_sha256"].items():
        if file_hash(root/name)!=expected:raise ValueError("Source artifact changed: "+name)
    runtime_paths={"runtime.py":Path(__file__),"exchange.py":Path(__file__).parent/"portable_embeddings.py",
                   "shared_text.py":Path(__file__).parent/"retrieval/text.py"}
    if any(package["runtime_files_sha256"][n]!=file_hash(p) for n,p in runtime_paths.items()):
        raise ValueError("Import/shared runtime changed")
    for row,item,mapped in zip(context["rows"],package["corpus"],context["mapping"],strict=True):
        if (row["chunk_id"],row["document_id"],row["text"],row["text_sha256"],mapped["token_length"]) != (
                item["chunk_id"],item["document_id"],item["text"],item["text_sha256"],item["actual_tokens"]):
            raise ValueError("Exact local corpus/serialization mismatch")
    drafts=sorted([json.loads(l) for l in (root/"data/benchmark/development_queries_draft.jsonl").read_text(encoding="utf8").splitlines() if l],key=lambda q:q["query_id"])
    if [(q["query_id"],q["text"],q["validation_status"]) for q in drafts]!=[(q["query_id"],q["text"],q["validation_status"]) for q in package["queries"]]:
        raise ValueError("Exact local query mismatch")
    for name in ("model_file_hashes","official_inference_file_hashes"):
        if package[name]!=context["identity"][name]:raise ValueError("Model/API identity mismatch")


def load_components(root):
    from .versioned_dense import prepare_v2
    from .dense.index import load_vectors
    ctx=prepare_v2(root);directory=Path(root)/ctx["binding"]["r3_index"]
    manifest=parse_json((directory/"manifest.json").read_bytes())
    exchange=manifest["exchange_manifest"]
    package,_=read_input(Path(root)/"experiments/portable/v2_bge_m3/full_input_package.zip")
    verify_local(ctx,package)
    fingerprinted(exchange,"manifest_fingerprint")
    identity=cloud_identity(ctx,package,exchange["encoding_environment"])
    if exchange.get("input_package_fingerprint")!=package["package_fingerprint"] or exchange.get("completion_status")!="COMPLETE":
        raise ValueError("Stale/incomplete exchange")
    for key in ("inference","model_file_hashes","official_inference_file_hashes","runtime_files_sha256","snapshot_id","snapshot_fingerprint"):
        if exchange.get(key)!=package[key]:raise ValueError("Stale exchange configuration")
    if exchange.get("corpus_mapping")!=package["corpus"] or exchange.get("query_mapping")!=package["queries"]:
        raise ValueError("Stale exchange mapping")
    vectors,manifest=load_vectors(directory,identity,ctx["mapping"])
    from .query_vectors.artifacts import contract,load_artifact
    for q in package["queries"]:
        load_artifact(directory/"query_vectors"/q["query_id"],contract(manifest),q["query_id"],q["text"])
    return ctx["bm25"],vectors,manifest,ctx["config"],ctx["local"]


def runtime_environment(session_id):
    import torch
    names=set(PINS)|{"torch","numpy","huggingface-hub","sentencepiece","safetensors","datasets","accelerate"}
    versions={n:metadata.version(n) for n in sorted(names)}
    return {"synthetic_fixture":False,"platform":platform.system(),"python":platform.python_version(),
        "dependency_versions":versions,"full_environment_lock":sorted(d.metadata["Name"]+"=="+d.version for d in metadata.distributions()),
        "gpu_name":torch.cuda.get_device_name(0),"gpu_capability":list(torch.cuda.get_device_capability(0)),
        "cuda_runtime":torch.version.cuda,"precision":"float16","session_id":session_id,
        "environment_validation":"PASS","pip_check":"PASS","cuda_smoke":"PASS"}


def check_environment():
    import subprocess
    if platform.system()!="Linux" or sys.version_info[:2]!=(3,12):raise RuntimeError("Linux Python 3.12 required")
    subprocess.run([sys.executable,"-m","pip","check"],check=True)
    for name,expected in PINS.items():
        if metadata.version(name)!=expected:raise RuntimeError("Pinned dependency mismatch: "+name)
    import torch
    from FlagEmbedding import BGEM3FlagModel
    from transformers import AutoTokenizer
    if not torch.cuda.is_available():raise RuntimeError("CUDA unavailable; no CPU fallback")
    for dtype in (torch.float32,torch.float16):
        a=torch.tensor([[1.,2.],[3.,4.]],device="cuda:0",dtype=dtype)
        result=a@a
        expected=torch.tensor([[7.,10.],[15.,22.]],device="cuda:0",dtype=dtype)
        if not torch.equal(result,expected):raise RuntimeError("CUDA numerical smoke FAIL")
    del a,result,expected
    torch.cuda.synchronize()
    return True


class CloudRun:
    def __init__(self, package, work, session_id):
        if platform.system()!="Linux" or sys.version_info[:2]!=(3,12):raise RuntimeError("Linux Python 3.12 required")
        import torch
        check_environment()
        validate_input(package)
        self.package,self.work,self.session_id=package,Path(work),session_id
        self.env=runtime_environment(session_id);validate_environment(self.env)
        self.work.mkdir(parents=True,exist_ok=True)
        if (self.work/"bge_m3_v2_full_embeddings.zip").exists():raise FileExistsError("COMPLETE output already exists; move/archive explicitly first")
        self.model=None;self.timings={};self.tokens={}

    def tokenize(self):
        from huggingface_hub import HfApi,snapshot_download
        from transformers import AutoTokenizer
        cfg=self.package["inference"]
        if HfApi().model_info(cfg["model_id"],revision=cfg["model_revision"]).sha!=cfg["model_revision"]:
            raise RuntimeError("Pinned repository revision mismatch")
        self.local=Path(snapshot_download(cfg["model_id"],revision=cfg["model_revision"],
            allow_patterns=list(self.package["model_file_hashes"]),cache_dir=str(self.work/"hf_cache")))
        if self.local.name!=cfg["model_revision"]:raise RuntimeError("Wrong checkpoint revision")
        for n,h in self.package["model_file_hashes"].items():
            if file_hash(self.local/n)!=h:raise RuntimeError("Checkpoint/tokenizer checksum mismatch: "+n)
        self.tokenizer=AutoTokenizer.from_pretrained(str(self.local),use_fast=True,local_files_only=True,trust_remote_code=False)
        for kind in ("corpus","queries"):
            lengths=[len(self.tokenizer(normalize(r["text"]),add_special_tokens=True,truncation=False,padding=False)["input_ids"]) for r in self.package[kind]]
            if lengths!=[r["actual_tokens"] for r in self.package[kind]] or max(lengths)>640:
                raise RuntimeError("Actual token audit mismatch/overflow; no truncation")
            self.tokens[kind]=lengths
            print(kind,"count",len(lengths),"min",min(lengths),"median",float(np.median(lengths)),"max",max(lengths),"truncation=0")

    def load(self):
        if self.tokens!={k:[r["actual_tokens"] for r in self.package[k]] for k in ("corpus","queries")}:
            raise RuntimeError("Tokenization audit must PASS before weights loading")
        import torch
        from FlagEmbedding import BGEM3FlagModel
        if self.model is not None:raise RuntimeError("Model already loaded; reuse existing run")
        flag_root=Path(metadata.distribution("FlagEmbedding").locate_file("FlagEmbedding"))
        for name,h in self.package["official_inference_file_hashes"].items():
            if file_hash(flag_root/name)!=h:raise RuntimeError("Official FlagEmbedding API/code mismatch")
        os.environ["HF_HUB_OFFLINE"]="1";os.environ["TRANSFORMERS_OFFLINE"]="1"
        torch.set_num_threads(4);torch.cuda.reset_peak_memory_stats()
        started=perf_counter()
        self.model=BGEM3FlagModel(str(self.local),use_fp16=True,devices=["cuda:0"],batch_size=1,
            query_max_length=640,passage_max_length=640,normalize_embeddings=True,pooling_method="cls",
            return_dense=True,return_sparse=False,return_colbert_vecs=False,trust_remote_code=False)
        self.model.model.eval().to("cuda:0");torch.cuda.synchronize()
        if next(self.model.model.parameters()).dtype!=torch.float16:raise RuntimeError("Expected FP16 weights")
        self.timings["model_loading_seconds"]=perf_counter()-started
        matrix(self.encode("Pemeriksaan kesiapan tim Wedding Organizer."),1,False)
        print("MODEL LOADING AND DENSE DIMENSION SMOKE PASS")

    def encode(self,text):
        import torch
        if self.model is None:raise RuntimeError("Load explicitly before encoding")
        tokens=self.tokenizer(normalize(text),add_special_tokens=True,truncation=False,padding=False)
        if len(tokens["input_ids"])>640:raise RuntimeError("Truncation forbidden")
        features=self.tokenizer.pad([tokens],padding=True,return_tensors="pt").to("cuda:0")
        with torch.inference_mode():out=self.model.model(features,return_dense=True,return_sparse=False,return_colbert_vecs=False)
        torch.cuda.synchronize()
        if set(out)!={"dense_vecs"}:raise RuntimeError("Dense-only output required")
        return matrix(out["dense_vecs"].float().cpu().numpy(),1,False)

    def encode_group(self,kind,resume=False):
        if (self.work/"bge_m3_v2_full_embeddings.zip").exists():raise FileExistsError("COMPLETE output exists; no repeat inference/overwrite")
        # Resume is explicit and bound to this runtime/model environment, not merely file existence.
        directory=self.work/(kind+"_partial");state_path=directory/"progress.json"
        identity={"package_fingerprint":self.package["package_fingerprint"],"environment":self.env,
                  "mapping":self.package[kind],"model_revision":self.package["inference"]["model_revision"]}
        if directory.exists():
            if not resume:raise RuntimeError("Partial artifacts exist; inspect and set RESUME=True explicitly")
            state=parse_json(state_path.read_bytes())
            if state.get("status")!="INCOMPLETE" or state.get("identity")!=identity:raise RuntimeError("Stale partial/session/model/order mismatch")
        else:
            directory.mkdir();state={"status":"INCOMPLETE","identity":identity,"completed":[],"encoding_seconds":0.0}
            self.save_state(state_path,state)
        raw=[]
        if len(state["completed"])>len(self.package[kind]):raise RuntimeError("Extra partial rows")
        for i,item in enumerate(state["completed"]):
            path=directory/f"{i:04d}.npy"
            if item["input"]!=self.package[kind][i] or file_hash(path)!=item["sha256"]:raise RuntimeError("Corrupted partial mapping/hash")
            raw.append(matrix(np.load(path,allow_pickle=False),1,False))
        for i in range(len(raw),len(self.package[kind])):
            started=perf_counter();vector=self.encode(self.package[kind][i]["text"]);elapsed=perf_counter()-started
            path=directory/f"{i:04d}.npy";temporary=path.with_suffix(".tmp")
            temporary.write_bytes(npy(vector));temporary.replace(path)
            state["completed"].append({"input":self.package[kind][i],"sha256":file_hash(path)})
            state["encoding_seconds"]+=elapsed;self.save_state(state_path,state);raw.append(vector)
            print(("Corpus" if kind=="corpus" else "Query")+f" embedding: {i+1}/{len(self.package[kind])}",flush=True)
        result=np.concatenate(raw)
        self.timings[kind+"_encoding_seconds"]=state["encoding_seconds"]
        if kind=="corpus":self.corpus=matrix(unit(result),371)
        else:self.raw_queries=matrix(result,18,False);self.queries=matrix(unit(result),18)

    @staticmethod
    def save_state(path,state):
        temporary=path.with_suffix(".tmp");temporary.write_bytes(canonical(state));temporary.replace(path)

    def validate(self):
        matrix(self.corpus,371);matrix(self.queries,18);matrix(self.raw_queries,18,False)
        if not np.array_equal(unit(self.raw_queries),self.queries):raise ValueError("Query stage mismatch")
        if self.tokens!={k:[r["actual_tokens"] for r in self.package[k]] for k in ("corpus","queries")}:
            raise ValueError("Incomplete token audit")
        print("VECTOR VALIDATION PASS: (371,1024), (18,1024); no truncation")

    def export(self,output):
        import torch
        self.validate()
        env={**self.env,"peak_gpu_allocated_bytes":torch.cuda.max_memory_allocated(),
             "peak_gpu_reserved_bytes":torch.cuda.max_memory_reserved()}
        result=write_output(output,self.package,self.corpus,self.queries,self.raw_queries,env,self.timings,self.tokens)
        read_output(output,self.package)
        print("COMPLETE",output,"SHA256",file_hash(output))
        return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=("export","import","inspect"));parser.add_argument("--root",type=Path,default=Path.cwd())
    parser.add_argument("--input",type=Path);parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    if args.command=="export":
        if not args.output:parser.error("--output required")
        package=export_inputs(args.root,args.output);result={"counts":package["counts"],"package_fingerprint":package["package_fingerprint"],"zip_sha256":file_hash(args.output)}
    elif args.command=="import":
        if not args.input or not args.output:parser.error("--input original package and --output returned ZIP required")
        result=import_output(args.root,args.input,args.output)
    else:
        _,vectors,manifest,_,_=load_components(args.root);result={"status":"PASS","shape":list(vectors.shape),"identity":manifest["identity"]}
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":main()
