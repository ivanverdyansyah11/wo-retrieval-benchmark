from dataclasses import dataclass, field
from typing import Any


@dataclass
class Block:
    block_id: str
    kind: str
    text: str
    source_locator: dict[str, Any]
    heading: str | None = None
    level: int | None = None
    data: dict[str, Any] = field(default_factory=dict)
    raw_text: str | None = None
    retrievable: bool = True
    exclusion_rule: str | None = None


@dataclass
class ParseResult:
    content_blocks: list[Block]
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Document:
    document_id: str
    title: str
    category: str
    document_type: str
    source_file: str
    source_type: str
    version: str
    corpus_version: str
    validation_status: str
    metadata: dict[str, Any]
    content_blocks: list[Block]


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    chunk_index: int
    title: str
    category: str
    heading: str | None
    text: str
    source_file: str
    source_type: str
    source_locator: dict[str, Any]
    token_count: int
    token_count_method: str
    corpus_version: str
    validation_status: str
    content_hash: str
    metadata: dict[str, Any] = field(default_factory=dict)
