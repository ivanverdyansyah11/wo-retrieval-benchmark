import hashlib
import math
import re
from dataclasses import dataclass

from wo_retrieval.schemas import Block, Chunk, Document


TOKEN_METHOD = "approx_unicode_chars_div4_v1"


def token_count(text: str) -> int:
    """Pilot proxy only: ceil(Unicode code points / 4), including labels/newlines."""
    return math.ceil(len(text) / 4)


@dataclass
class Piece:
    text: str
    block: Block
    start: int
    end: int


def recursive_spans(text: str, limit: int, base: int = 0, depth: int = 0):
    """Split on paragraphs, rows, sentences, words, then Unicode characters."""
    if len(text) <= limit:
        return [(base, base + len(text))]
    separators = [r"\n\n", r"\n", r"(?<=[.!?])\s+", r"\s+"]
    if depth == len(separators):
        return [(base + i, base + min(i + limit, len(text))) for i in range(0, len(text), limit)]
    cuts = [0] + [m.end() for m in re.finditer(separators[depth], text)] + [len(text)]
    spans = []
    for start, end in zip(cuts, cuts[1:]):
        if end > start:
            spans.extend(recursive_spans(text[start:end], limit, base + start, depth + 1))
    return spans


def units(document: Document):
    """No packing across headings, sheets, tables, or paragraph/list boundaries."""
    current, key = [], None
    for block in document.content_blocks:
        if not block.retrievable:
            continue
        if block.kind in {"title", "heading", "table_header"}:
            if current:
                yield current
                current = []
            key = None
            continue
        loc = block.source_locator
        unit_key = (block.heading, loc.get("sheet"), loc.get("table"),
                    "list" if block.kind == "list_item" else "table" if block.kind in {"table", "table_row"} else "prose")
        if current and unit_key != key:
            yield current
            current = []
        key = unit_key
        current.append(block)
    if current:
        yield current


def chunk_document(document: Document, config: dict) -> list[Chunk]:
    target, overlap = config["target_tokens"], config["overlap_tokens"]
    if not isinstance(target, int) or not isinstance(overlap, int) or target <= 0 or not 0 <= overlap < target:
        raise ValueError("Require integer target_tokens > overlap_tokens >= 0")
    if config["token_count_method"] != TOKEN_METHOD:
        raise ValueError(f"Unsupported token counter: {config['token_count_method']}")
    chunks = []
    guide = [{"text": b.text, "source_locator": b.source_locator, "block_id": b.block_id}
             for b in document.content_blocks if b.retrievable and b.kind == "table_row"
             and b.source_locator.get("sheet") == "Panduan"]
    for unit_index, blocks in enumerate(units(document), 1):
        heading = blocks[0].heading
        loc = blocks[0].source_locator
        prefix = ""
        if loc.get("sheet"):
            headers = blocks[0].data.get("headers", [])
            prefix = f"Sheet: {loc['sheet']}\nSection: {loc.get('section') or loc['sheet']}\nHeader: {' | '.join(headers)}\n\n"
            # Only the RACI definition is repeated in text; other guide context is
            # inherited as structured metadata with its exact source references.
            if loc["sheet"] != "Panduan" and all(h in headers for h in ["A", "R", "C", "I"]):
                definition = next((g["text"] for g in guide if "A adalah pengesah" in g["text"]), "")
                if definition:
                    prefix += definition + "\n\n"
        elif heading:
            prefix = heading + "\n\n"
        max_chars = target * 4
        budget = max_chars - len(prefix)
        if budget <= overlap * 4:
            raise ValueError(f"Heading/table context leaves insufficient chunk budget: {document.document_id}/{heading}")
        pieces = []
        # Reserve overlap only for an oversized natural unit. Intact units get none.
        total_body = sum(len(b.text) for b in blocks) + 2 * (len(blocks) - 1)
        split_limit = budget - overlap * 4 if total_body > budget else budget
        for block in blocks:
            text = block.text
            if block.kind == "table_row":
                text = f"Row: {block.source_locator['row_start']}\n{text}"
            for start, end in recursive_spans(text, split_limit):
                if text[start:end].strip():
                    left = len(text[start:end]) - len(text[start:end].lstrip())
                    right = len(text[start:end].rstrip())
                    pieces.append(Piece(text[start:end].strip(), block, start + left, start + right))
        groups, current = [], []
        for piece in pieces:
            candidate = "\n\n".join(p.text for p in current + [piece])
            if current and len(candidate) > split_limit:
                groups.append(current)
                current = []
            current.append(piece)
        if current:
            groups.append(current)
        previous = ""
        previous_group = []
        for part_index, group in enumerate(groups):
            body = "\n\n".join(p.text for p in group)
            overlap_text = ""
            overlap_pieces = []
            if part_index and overlap:
                available = min(overlap * 4, budget - len(body) - 2)
                if available > 0:
                    if loc.get("sheet") or blocks[0].kind in {"table", "list_item"}:
                        # Table/list overlap must be whole structured pieces. A
                        # clipped row can separate a value from its group/PIC.
                        for p in reversed(previous_group):
                            candidate = "\n\n".join(v.text for v in [p] + overlap_pieces)
                            if len(candidate) > available:
                                break
                            overlap_pieces.insert(0, p)
                        overlap_text = "\n\n".join(p.text for p in overlap_pieces)
                    else:
                        overlap_text = previous[-available:]
                        # Start at a word/line boundary, never fabricate a new word.
                        if len(previous) > available and not previous[-available-1].isspace():
                            boundary = re.search(r"\s+", overlap_text)
                            overlap_text = overlap_text[boundary.end():] if boundary else ""
                        overlap_text = overlap_text.strip()
            text = prefix + (overlap_text + "\n\n" if overlap_text else "") + body
            references = []
            for p in group:
                reference = {"block_id": p.block.block_id, **p.block.source_locator,
                             "serialized_char_start": p.start, "serialized_char_end": p.end}
                if reference not in references:
                    references.append(reference)
            source = {"blocks": references}
            if loc.get("sheet"):
                source.update(sheet=loc["sheet"], table=loc.get("table"), header_row=loc.get("header_row"),
                              row_start=min(p.block.source_locator["row_start"] for p in group),
                              row_end=max(p.block.source_locator["row_end"] for p in group))
            for stem in ["page", "line"]:
                relevant = [p.block.source_locator for p in group if f"{stem}_start" in p.block.source_locator]
                if relevant:
                    source[f"{stem}_start"] = min(r[f"{stem}_start"] for r in relevant)
                    source[f"{stem}_end"] = max(r[f"{stem}_end"] for r in relevant)
            if overlap_text:
                source["overlap_blocks"] = [{"block_id": p.block.block_id, **p.block.source_locator,
                                             "serialized_char_start": p.start, "serialized_char_end": p.end}
                                            for p in (overlap_pieces or previous_group)]
            index = len(chunks) + 1
            chunks.append(Chunk(
                f"{document.document_id}-C{index:03}", document.document_id, index,
                document.title, document.category, heading, text, document.source_file,
                document.source_type, source, token_count(text), TOKEN_METHOD,
                document.corpus_version, document.validation_status,
                hashlib.sha256(text.encode("utf-8")).hexdigest(),
                {"format": document.metadata["format"], "natural_unit": unit_index,
                 "part_index": part_index + 1, "overlap_tokens": token_count(overlap_text),
                 "overlap_text": overlap_text,
                 "associated_event_ids": document.metadata.get("associated_event_ids", []),
                 "guide_context": guide if loc.get("sheet") and loc["sheet"] != "Panduan" else [],
                 "source_sha256": document.metadata["file_sha256"]},
            ))
            previous, previous_group = body, group
    return chunks
