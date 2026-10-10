import re
import unicodedata

from wo_retrieval.schemas import Document


def normalize(text: str) -> str:
    """NFC preserves compatibility characters; no case/code/number rewriting."""
    text = unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[^\S\n]+", " ", line).strip() for line in text.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def exclusion_rule(block, title: str) -> str | None:
    text = block.text
    if block.kind == "title" and text == normalize(title):
        return "document_title_to_metadata"
    if re.fullmatch(r"WO-DOC-\d{3}(?:\s*\|\s*(?:Versi [\w.-]+|Wedding Organizer X|Draft simulasi|Belum divalidasi praktisi)){1,3}", text):
        return "identity_version_status_to_metadata"
    if re.fullmatch(r"Draft (?:operasional )?susunan peneliti[.;] (?:Status: belum divalidasi praktisi\. Skenario dan catatan pelaksanaan bersifat simulasi\.|belum divalidasi praktisi\. (?:Seluruh skenario dan catatan pelaksanaan bersifat simulasi\.|Skenario simulasi\.))", text):
        return "exact_provenance_notice_to_metadata"
    if re.fullmatch(r"Konteks: EVT-\d{2}(?:, EVT-\d{2})*(?:\. Dokumen terkait: WO-DOC-\d{3}(?:, WO-DOC-\d{3})*\.)?", text):
        return "event_relation_banner_to_metadata"
    if re.fullmatch(r"Dokumen terkait: WO-DOC-\d{3}(?:, WO-DOC-\d{3})*\.?", text):
        return "event_relation_banner_to_metadata"
    if "page_start" in block.source_locator and block.data.get("font_size", 100) <= 9:
        if re.fullmatch(r"Wedding Organizer X \| WO-DOC-\d{3}(?: \d+)?|\d+", text):
            return "exact_pdf_running_footer_to_metadata"
    if block.source_locator.get("sheet") == "Panduan" and block.kind == "table_row":
        values = block.data.get("values", [])
        if len(values) == 2 and values[0] in {"Identitas", "Provenance", "Validasi"}:
            return "guide_administrative_row_to_metadata"
    return None


def clean(document: Document) -> Document:
    administrative = []
    for block in document.content_blocks:
        block.raw_text = block.text
        block.text = normalize(block.text)
        block.heading = normalize(block.heading) if block.heading else None
        rule = exclusion_rule(block, document.title)
        if rule:
            block.retrievable = False
            block.exclusion_rule = rule
            administrative.append({"block_id": block.block_id, "rule": rule,
                                   "text": block.raw_text, "source_locator": block.source_locator})
    document.metadata["administrative_blocks"] = administrative
    document.metadata["cleaning_method"] = "NFC; horizontal whitespace; max one empty line; exact administrative patterns v1"
    return document
