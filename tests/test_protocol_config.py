"""Contract checks for protocol text/config only; no retrieval or model execution."""

import hashlib
import json
import re
import tomllib
import unicodedata
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProtocolConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_bytes = (ROOT / 'experiments/configs/retrieval_protocol_v1.toml').read_bytes()
        cls.config = tomllib.loads(cls.config_bytes.decode('utf-8'))
        cls.markdown = (ROOT / 'experiments/reports/benchmark_protocol_v1.md').read_text(encoding='utf-8')

    def test_intended_lexical_character_policy(self):
        self.assertEqual(self.config['lexical']['token_pattern'], r"(?u)\b\w+(?:[-'’]\w+)*\b")
        self.assertNotIn('\u00e2\u20ac\u2122', self.config['lexical']['token_pattern'])
        self.assertEqual(self.config['lexical']['normalization'],
                         'serialization normalization, then casefold and U+2019 apostrophe to ASCII apostrophe')

    def test_documented_regex_examples_without_retrieval(self):
        # This validates the declared policy; it is not a production tokenizer implementation.
        examples = [
            ("WO H-1 drop-off PIC_VENDOR 280 x", ['wo', 'h-1', 'drop-off', 'pic_vendor', '280', 'x']),
            ("CLIENT’S client's", ["client's", "client's"]),
            ('H–1 MC—AV', ['h', '1', 'mc', 'av']),
            ("-MC- 'AV'", ['mc', 'av']),
            ('a€b catering™vendor', ['a', 'b', 'catering', 'vendor']),
            ('pengantin pengantin café cafe\u0301', ['pengantin', 'pengantin', 'café', 'café']),
            ('   \r\n ', []),
        ]
        for text, expected in examples:
            with self.subTest(text=text):
                normalized = unicodedata.normalize('NFC', text).replace('\r\n', '\n').replace('\r', '\n').strip()
                normalized = normalized.casefold().replace('\u2019', "'")
                self.assertEqual(re.findall(self.config['lexical']['token_pattern'], normalized), expected)

    def test_pending_status_is_explicitly_unvalidated(self):
        queries = self.config['queries']
        self.assertEqual(queries['validation_status_values'],
                         ['draft', 'draft_pending_expert_review', 'expert_reviewed', 'frozen'])
        self.assertIn('not validated or frozen', queries['validation_status_policy'])
        self.assertFalse(self.config['implementation_authorized'])
        self.assertFalse(self.config['main_evaluation_authorized'])

    def test_existing_drafts_use_allowed_pending_status(self):
        queries = [json.loads(line) for line in
                   (ROOT / 'data/benchmark/development_queries_draft.jsonl').read_text(encoding='utf-8').splitlines()]
        self.assertEqual(len(queries), 18)
        for query in queries:
            self.assertIn(query['validation_status'], self.config['queries']['validation_status_values'])
            self.assertEqual(query['validation_status'], 'draft_pending_expert_review')

    def test_markdown_config_binding(self):
        self.assertIn(hashlib.sha256(self.config_bytes).hexdigest(), self.markdown)
        self.assertIn(self.config['lexical']['token_pattern'], self.markdown)
        self.assertIn('draft_pending_expert_review', self.markdown)
        self.assertIn(self.config['queries']['status'], self.markdown)


if __name__ == '__main__':
    unittest.main()
