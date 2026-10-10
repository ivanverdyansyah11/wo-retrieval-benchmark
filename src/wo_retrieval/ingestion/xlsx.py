import datetime
import re
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.cell_range import CellRange

from wo_retrieval.schemas import Block, ParseResult
from .common import ParseError, require_content, require_nonempty


def value_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    return str(value)


def parse(path: Path) -> ParseResult:
    require_nonempty(path)
    values = load_workbook(path, data_only=True)
    formulas = load_workbook(path, data_only=False)
    blocks, warnings = [], []
    formula_count = 0
    for sheet in values:
        raw = formulas[sheet.title]
        merged = [str(r) for r in raw.merged_cells.ranges]
        title = None
        headers = None
        header_row = None
        table_index = 0
        previous_blank = True
        for row in sheet:
            cells = [value_text(c.value) for c in row]
            used = [i for i, v in enumerate(cells) if v]
            if not used:
                previous_blank = True
                continue
            row_number = row[0].row
            loc = {"sheet": sheet.title, "row_start": row_number, "row_end": row_number,
                   "merged_ranges": [r for r in merged if CellRange(r).min_row <= row_number <= CellRange(r).max_row]}
            formula_cells = {}
            for c in raw[row_number]:
                if c.data_type == "f":
                    formula_count += 1
                    formula_cells[c.coordinate] = c.value
                    if sheet[c.coordinate].value is None:
                        raise ParseError(f"Missing formula cache: {path.name}/{sheet.title}!{c.coordinate}")
            if len(used) == 1 and used[0] == 0:
                text = cells[0]
                # Single-cell rows are section titles or administrative notices.
                administrative = text.startswith(("WO-DOC-", "Draft "))
                if not administrative:
                    title = sheet.title if re.fullmatch(r"Panduan WO-DOC-\d{3}", text) else text
                    headers = None
                kind = "paragraph" if administrative else "heading"
                blocks.append(Block(f"s{values.sheetnames.index(sheet.title)+1}-r{row_number:04}", kind,
                                    text, loc, f"{title or sheet.title} / {sheet.title}", 1 if kind == "heading" else None))
                previous_blank = True
                continue
            # Explicit Excel tables win; otherwise use first multi-cell row after a
            # title/blank break. Repeated labels reopen the same header context.
            explicit = next((t for t in raw.tables.values() if CellRange(t.ref).min_row == row_number), None)
            is_header = headers is None or (previous_blank and len(used) >= 2) or explicit is not None or cells == headers
            if is_header:
                table_index += 1
                header_row = row_number
                headers = [v or f"Column {get_column_letter(i+1)}" for i, v in enumerate(cells)]
                if len(set(headers)) != len(headers):
                    warnings.append(f"Duplicate column labels at {sheet.title}!{row_number}; column positions retained")
                if any(not v for v in cells):
                    warnings.append(f"Blank header label at {sheet.title}!{row_number}; coordinate label used")
                kind = "table_header"
                text = " | ".join(headers)
            else:
                kind = "table_row"
                text = "\n".join(f"{label}: {v}" for label, v in zip(headers, cells))
            loc.update(header_row=header_row, table=f"{sheet.title}:table-{table_index}",
                       section=title, column_start="A", column_end=get_column_letter(len(cells)))
            data = {"headers": headers.copy(), "values": cells, "formulas": formula_cells,
                    "formula_values": "stored_cache_not_recalculated" if formula_cells else None,
                    "column_coordinates": [f"{get_column_letter(i+1)}{row_number}" for i in range(len(cells))]}
            blocks.append(Block(f"s{values.sheetnames.index(sheet.title)+1}-r{row_number:04}", kind,
                                text, loc, f"{title or sheet.title} / {sheet.title}", data=data))
            previous_blank = False
    values.close()
    formulas.close()
    return require_content(ParseResult(blocks, warnings, {
        "formula_cells": formula_count, "formula_policy": "read stored caches; fail if missing; no recalculation",
        "xlsx_header_rule": "Excel table header or first multi-cell row after section/blank; recorded coordinates",
    }), path)
