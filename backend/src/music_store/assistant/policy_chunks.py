"""Chunks the Policy Manual PDF by section: one chunk per subsection."""

import re
from pathlib import Path

from pypdf import PdfReader

from music_store.models.policy import PolicyChunkModel

_HEADING = re.compile(r"^(\d+(?:\.\d+)?)\.?\s+(\S.*)$")
_PAGE_NOISE = re.compile(r"^(Empório da Música Manual de Políticas e Procedimentos|Página \d+)$")
_COLUMN_GAP = re.compile(r"\s{2,}")


def _pdf_lines(pdf_path: Path) -> list[str]:
    lines: list[str] = []
    for page in PdfReader(pdf_path).pages:
        for raw in page.extract_text(extraction_mode="layout").splitlines():
            line = _COLUMN_GAP.sub(" | ", raw.strip())
            if line and not _PAGE_NOISE.match(line):
                lines.append(line)
    return lines


def _heading(line: str, top: int, sub: int) -> tuple[str, str] | None:
    """Return (number, title) when the line is the next section or subsection heading.

    Following the numbering in sequence keeps numbered list items ("1. Saudação") from
    being mistaken for sections.
    """
    match = _HEADING.match(line)
    if not match:
        return None
    number, title = match.groups()
    if "." not in number:
        return (number, title) if int(number) == top + 1 else None
    parent, child = number.split(".")
    return (number, title) if int(parent) == top and int(child) == sub + 1 else None


def load_policy_chunks(pdf_path: Path) -> list[PolicyChunkModel]:
    chunks: list[PolicyChunkModel] = []
    top, sub = 0, 0
    parent_title: str | None = None
    current: tuple[str, str, str | None] | None = None  # section, title, parent title
    body: list[str] = []

    def flush() -> None:
        if current is not None and body:
            section, title, parent = current
            chunks.append(
                PolicyChunkModel(
                    section=section, title=title, parent_title=parent, text="\n".join(body)
                )
            )

    for line in _pdf_lines(pdf_path):
        found = _heading(line, top, sub)
        if found is None:
            body.append(line)
            continue
        flush()
        body = []
        number, title = found
        if "." in number:
            sub += 1
            current = (number, title, parent_title)
        else:
            top, sub = int(number), 0
            parent_title = title
            current = (number, title, None)
    flush()
    return chunks
