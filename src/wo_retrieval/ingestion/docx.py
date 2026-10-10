import re
from pathlib import Path

from docx import Document as ReadDocx
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from wo_retrieval.schemas import Block, ParseResult
from .common import require_content, require_nonempty


def parse(path: Path) -> ParseResult:
    require_nonempty(path)
    doc = ReadDocx(path)
    blocks = []
    heading = None
    heading_stack = []
    paragraph_index = table_index = 0
    for body_index, element in enumerate(doc.element.body, 1):
        locator = {"body_position": body_index}
        data = {}
        if element.tag == qn("w:p"):
            paragraph_index += 1
            p = Paragraph(element, doc)
            text = p.text
            if not text.strip():
                continue
            style = p.style.name if p.style else ""
            locator["paragraph_position"] = paragraph_index
            match = re.fullmatch(r"Heading (\d+)", style)
            level = int(match[1]) if match else None
            kind = "heading" if match else "title" if style == "Title" else "paragraph"
            num = p._p.xpath("./w:pPr/w:numPr")
            if num or style.startswith("List") or re.match(r"^\s*(?:[-*•]|\d+[.)])\s+", text):
                kind = "list_item"
                data = {"style": style, "numbering_xml": num[0].xml if num else None}
            if kind == "heading":
                heading = text
                while heading_stack and heading_stack[-1][0] >= level:
                    heading_stack.pop()
                heading_stack.append((level, text))
        elif element.tag == qn("w:tbl"):
            table_index += 1
            table = Table(element, doc)
            rows = [[c.text for c in row.cells] for row in table.rows]
            text = "\n".join(" | ".join(row) for row in rows)
            kind, level = "table", None
            locator.update(table_position=table_index, row_start=1, row_end=len(rows))
            data = {"rows": rows, "header_candidate": rows[0] if rows else [],
                    "header_is_explicit": bool(element.xpath("./w:tr[1]/w:trPr/w:tblHeader"))}
        else:
            continue
        locator["heading"] = heading
        locator["heading_path"] = [text for _, text in heading_stack]
        blocks.append(Block(f"b{body_index:04}", kind, text, locator, heading, level, data))
    return require_content(ParseResult(blocks), path)
