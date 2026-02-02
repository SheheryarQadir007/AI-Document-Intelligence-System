
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional

from .utils import clean_text

@dataclass
class Document:
    filename: str
    path: str
    raw_text: str
    text: str              # cleaned (single-line) for retrieval
    error: Optional[str] = None

def _read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def _read_pdf_pypdf2(path: str) -> str:
    import PyPDF2
    reader = PyPDF2.PdfReader(open(path, "rb"))
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)

def load_documents(folder: str) -> List[Document]:
    docs: List[Document] = []
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if os.path.isdir(path):
            continue
        ext = os.path.splitext(name)[1].lower()
        if ext not in [".pdf", ".txt"]:
            continue

        raw = ""
        err: Optional[str] = None
        try:
            if ext == ".txt":
                raw = _read_txt(path)
            else:
                raw = _read_pdf_pypdf2(path)
        except Exception as e:
            err = f"{type(e).__name__}: {e}"
            raw = ""

        docs.append(Document(
            filename=name,
            path=path,
            raw_text=raw.strip() if raw else "",
            text=clean_text(raw) if raw else "",
            error=err
        ))
    return docs
