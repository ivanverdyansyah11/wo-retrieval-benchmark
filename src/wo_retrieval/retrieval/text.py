"""Shared, allowlisted retrieval text and lexical tokens."""

import re
import unicodedata


def normalize(text: str) -> str:
    if not isinstance(text, str):
        raise ValueError("Text must be a string")
    return unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n")).strip()


def comparison(text: str) -> str:
    return " ".join(normalize(text).casefold().split())


def contains(haystack: str, needle: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(comparison(needle)) + r"(?!\w)", comparison(haystack)) is not None


def serialize(chunk: dict, policy: dict) -> tuple[str, list[str]]:
    values = {field: normalize(chunk[field]) for field in policy["required_fields"]}
    if not all(values.values()):
        raise ValueError("Required serialization fields must be nonempty")
    selected = {}
    for field in policy["selection_order"]:
        value = values[field]
        if not contains(values["text"], value) and not any(contains(other, value) for other in selected.values()):
            selected[field] = value
    labels = dict(zip(policy["emission_order"], policy["labels"], strict=True))
    lines = [f"{labels[field]}: {selected[field]}" for field in policy["emission_order"] if field in selected]
    prefix = policy["prefix_line_separator"].join(lines)
    return (prefix + policy["prefix_body_separator"] if prefix else "") + values["text"], list(selected)


class LexicalTokenizer:
    version = "wo_lexical_unicode_unigram_v1"

    def __init__(self, config: dict):
        self.pattern = re.compile(config["token_pattern"])

    def __call__(self, text: str) -> list[str]:
        return self.pattern.findall(normalize(text).casefold().replace("\u2019", "'"))
