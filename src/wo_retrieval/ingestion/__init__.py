from pathlib import Path

from . import docx, pdf, txt, xlsx
from .common import ParseError, Parser

PARSERS: dict[str, Parser] = {".docx": docx.parse, ".pdf": pdf.parse, ".txt": txt.parse, ".xlsx": xlsx.parse}


def parse(path: Path):
    parser = PARSERS.get(path.suffix.lower())
    if parser is None:
        raise ParseError(f"Unsupported source format: {path.name}")
    return parser(path)
