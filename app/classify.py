
from __future__ import annotations

from .ingest import Document

def classify(doc: Document) -> str:
    """
    Offline-first classifier:
    - If PDF parsing fails or text is too short -> Unclassifiable
    - Else keyword/structure rules.
    """
    if doc.error is not None:
        return "Unclassifiable"

    t = (doc.raw_text or doc.text or "").lower()
    if len(t) < 25:
        return "Unclassifiable"

    # Utility Bill
    if ("account number" in t and "amount due" in t) or ("kwh" in t and "usage" in t) or "utility bill" in t:
        return "Utility Bill"

    # Invoice
    if ("invoice" in t and ("total amount" in t or "invoice #" in t)) or ("invoice number" in t and "total" in t):
        return "Invoice"

    # Resume
    if ("experience" in t and "years" in t and "email" in t) or "resume" in t:
        return "Resume"

    return "Other"
