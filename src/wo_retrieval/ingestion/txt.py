import re
from pathlib import Path

from wo_retrieval.schemas import Block, ParseResult
from .common import require_content, require_nonempty


LIST = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+")


def parse(path: Path) -> ParseResult:
    require_nonempty(path)
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    blocks = []
    heading = None
    first = True
    index = 0
    while index < len(lines):
        if not lines[index].strip():
            index += 1
            continue
        start = index
        line = lines[index]
        markdown = re.match(r"^(#{1,6})\s+(.+)$", line)
        # Corpus convention: short unpunctuated line starts a stanza, followed by prose.
        # This is a syntactic heuristic, not a semantic classification.
        stanza_heading = (not first and (index == 0 or not lines[index - 1].strip())
                          and len(line) <= 120 and not re.search(r"[.!?;:]$", line)
                          and not LIST.match(line) and index + 1 < len(lines)
                          and bool(lines[index + 1].strip()))
        kind = "title" if first else "heading" if markdown or stanza_heading else "list_item" if LIST.match(line) else "paragraph"
        first = False
        index += 1
        if kind == "paragraph":
            while index < len(lines) and lines[index].strip() and not LIST.match(lines[index]) and not lines[index].startswith("#"):
                # Administrative lines remain separate for conservative classification.
                if lines[start].startswith(("WO-DOC-", "Draft ", "Konteks:", "Dokumen terkait:")):
                    break
                index += 1
        text = "\n".join(lines[start:index])
        if kind == "heading":
            heading = markdown[2] if markdown else text
        blocks.append(Block(f"l{start + 1:04}-{index:04}", kind, text,
                            {"line_start": start + 1, "line_end": index, "section": heading},
                            heading, len(markdown[1]) if markdown else 1 if kind == "heading" else None))
    return require_content(ParseResult(blocks, metadata={
        "txt_heading_rule": "Markdown, or stanza-leading line <=120 chars without terminal punctuation followed by text"
    }), path)
