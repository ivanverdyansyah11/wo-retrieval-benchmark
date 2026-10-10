from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from repository_integrity import research_baseline, HISTORICAL_ROOT


class ResearchIntegrityTests(unittest.TestCase):
    def test_relocation_docs_and_generated_are_not_frozen_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data').mkdir();(root/'data/chunks.jsonl').write_bytes(b'frozen')
            historical={str(HISTORICAL_ROOT/'data/chunks.jsonl'):sha256(b'frozen').hexdigest()}
            for name in ('README.md','.gitignore','tests/test_old.py','src/pkg.egg-info/PKG-INFO'):
                historical[str(HISTORICAL_ROOT/name)]=sha256(b'old').hexdigest()
            historical['D:/ModelCache/wo-retrieval-benchmark/R3/vectors.npy']='unavailable-runtime'
            result=research_baseline(root,historical)
            self.assertEqual(len(result['hashes']),1);self.assertEqual(len(result['excluded']),5)
            self.assertIn(str(root/'data/chunks.jsonl'),result['hashes'])

    def test_missing_and_mutated_research_and_source_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name in ('data/chunks.jsonl','experiments/configs/protocol.toml',
                         'experiments/results/ranking.jsonl','src/retrieval.py','scripts/audit.py'):
                with self.subTest(path=name):
                    p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
                    baseline={str(HISTORICAL_ROOT/name):sha256(b'frozen').hexdigest()}
                    with self.assertRaises(ValueError):research_baseline(root,baseline)
                    p.write_bytes(b'mutated')
                    with self.assertRaises(ValueError):research_baseline(root,baseline)
                    p.write_bytes(b'frozen');self.assertEqual(len(research_baseline(root,baseline)['hashes']),1)

    def test_unknown_external_root_and_traversal_are_rejected(self):
        for path in ('D:/Other/data/x','D:/Project/wo-retrieval-benchmark/../outside','README.md'):
            with self.subTest(path=path),self.assertRaises(ValueError):research_baseline(Path.cwd(),{path:'bad'})

    def test_empty_research_scope_is_rejected(self):
        with self.assertRaises(ValueError):research_baseline(Path.cwd(),{str(HISTORICAL_ROOT/'README.md'):'old'})
