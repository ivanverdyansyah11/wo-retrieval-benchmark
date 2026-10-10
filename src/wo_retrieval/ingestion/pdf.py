from pathlib import Path

from pypdf import PdfReader

from wo_retrieval.schemas import Block, ParseResult
from .common import ParseError, require_content, require_nonempty


def parse(path: Path) -> ParseResult:
    require_nonempty(path)
    reader = PdfReader(path)
    blocks, warnings = [], []
    heading = None
    for page_number, page in enumerate(reader.pages, 1):
        groups = []

        def visit(text, cm, tm, font, size):
            if not text.strip():
                return
            # The corpus PDFs use a shared text origin for lines in one paragraph.
            # Keep callback order; never sort unreliable transformed coordinates.
            key = (tuple(cm), (font or {}).get("/BaseFont", ""), size)
            if groups and groups[-1][0] == key:
                groups[-1][1].append(text.strip())
            else:
                groups.append((key, [text.strip()]))

        extracted = page.extract_text(visitor_text=visit)
        if not extracted.strip():
            raise ParseError(f"PDF page {page_number} has no text layer: {path.name}; OCR disabled")
        for page_block, (key, lines) in enumerate(groups, 1):
            _, font, size = key
            text = " ".join(lines)
            # Deterministic typographic rule for this corpus; recorded in metadata.
            kind = "title" if size >= 16 else "heading" if size >= 12 and "Bold" in font else "paragraph"
            if kind == "heading":
                heading = text
            locator = {"page_start": page_number, "page_end": page_number,
                       "page_block": page_block, "heading": heading}
            blocks.append(Block(f"p{page_number:03}-b{page_block:03}", kind, text,
                                locator, heading, 1 if kind == "heading" else None,
                                {"font": font, "font_size": size}))
    if not any(b.kind == "heading" for b in blocks):
        warnings.append("PDF typography did not expose headings; retained page/block order")
    return require_content(ParseResult(blocks, warnings, {
        "pdf_pages": len(reader.pages),
        "pdf_heading_rule": "font_size>=12 and Bold; title>=16; callback order; same-origin lines grouped",
    }), path)
