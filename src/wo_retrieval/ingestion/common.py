from pathlib import Path
from typing import Protocol

from wo_retrieval.schemas import ParseResult


class Parser(Protocol):
    def __call__(self, path: Path) -> ParseResult: ...


class ParseError(ValueError):
    """Explicit extraction failure; no OCR or fabricated fallback content."""


def require_nonempty(path: Path) -> None:
    if path.stat().st_size == 0:
        raise ParseError(f"Empty source file: {path.name}")


def require_content(result: ParseResult, path: Path) -> ParseResult:
    if not any(b.text.strip() for b in result.content_blocks):
        raise ParseError(f"No readable text: {path.name}")
    return result
