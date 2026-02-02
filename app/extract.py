
from __future__ import annotations

import re
from typing import Dict, Any
from .utils import find_email, find_phone, find_first_date, parse_money
from .ingest import Document

INV_NUM_RE = re.compile(r"invoice\s*#\s*([A-Za-z0-9\-]+)", re.I)
INV_COMPANY_RE = re.compile(r"company:\s*(.+)", re.I)
INV_TOTAL_RE = re.compile(r"total amount:\s*\$?\s*([0-9,]+(?:\.[0-9]{1,2})?)", re.I)
INV_DATE_RE = re.compile(r"date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2}|\d{2}/\d{2}/\d{4})", re.I)

RES_EXP_RE = re.compile(r"experience:\s*([0-9]{1,2})\s*years?", re.I)

UB_ACC_RE = re.compile(r"account number:\s*([A-Za-z0-9\-]+)", re.I)
UB_DATE_RE = re.compile(r"(billing date|date):\s*([0-9]{4}-[0-9]{2}-[0-9]{2}|\d{2}/\d{2}/\d{4})", re.I)
UB_USAGE_RE = re.compile(r"usage:\s*([0-9]+(?:\.[0-9]+)?)\s*kwh", re.I)
UB_DUE_RE = re.compile(r"amount due:\s*\$?\s*([0-9,]+(?:\.[0-9]{1,2})?)", re.I)

def _first_line(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return ""

def extract_fields(doc: Document, doc_class: str) -> Dict[str, Any]:
    raw = doc.raw_text or ""
    out: Dict[str, Any] = {"class": doc_class}

    if doc_class == "Invoice":
        m = INV_NUM_RE.search(raw)
        if m:
            out["invoice_number"] = m.group(1)

        m = INV_DATE_RE.search(raw)
        out["date"] = m.group(1) if m else (find_first_date(raw) or None)

        m = INV_COMPANY_RE.search(raw)
        if m:
            # stop at end of line if possible
            company_line = m.group(1).splitlines()[0].strip()
            # if company line accidentally contains 'Total Amount', split it
            company_line = company_line.split("Total Amount")[0].strip()
            out["company"] = company_line if company_line else None

        m = INV_TOTAL_RE.search(raw)
        out["total_amount"] = parse_money(m.group(1)) if m else None

    elif doc_class == "Resume":
        out["name"] = _first_line(raw) or None
        out["email"] = find_email(raw)
        out["phone"] = find_phone(raw)

        m = RES_EXP_RE.search(raw)
        out["experience_years"] = int(m.group(1)) if m else None

    elif doc_class == "Utility Bill":
        m = UB_ACC_RE.search(raw)
        out["account_number"] = m.group(1) if m else None

        m = UB_DATE_RE.search(raw)
        out["date"] = m.group(2) if m else (find_first_date(raw) or None)

        m = UB_USAGE_RE.search(raw)
        out["usage_kwh"] = float(m.group(1)) if m else None

        m = UB_DUE_RE.search(raw)
        out["amount_due"] = parse_money(m.group(1)) if m else None

    return out
