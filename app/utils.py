
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Tuple

WHITESPACE_RE = re.compile(r"\s+")

def clean_text(text: str) -> str:
    """Basic text cleanup for downstream regex + retrieval."""
    text = text.replace("\x00", " ")
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text

DATE_PATTERNS = [
    re.compile(r"\b(\d{4}-\d{2}-\d{2})\b"),                 # 2025-01-31
    re.compile(r"\b(\d{2}/\d{2}/\d{4})\b"),                 # 01/31/2025
]

def find_first_date(text: str) -> Optional[str]:
    for pat in DATE_PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(1)
    return None

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(\+?\d[\d\-\s().]{7,}\d)")

def find_email(text: str) -> Optional[str]:
    m = EMAIL_RE.search(text)
    return m.group(0) if m else None

def find_phone(text: str) -> Optional[str]:
    m = PHONE_RE.search(text)
    if not m:
        return None
    return clean_text(m.group(1))

MONEY_RE = re.compile(r"\$?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)")

def parse_money(val: str) -> Optional[float]:
    try:
        val = val.replace(",", "").strip()
        return float(val)
    except Exception:
        return None
