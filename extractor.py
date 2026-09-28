"""
extractor.py - Structured Information Extractor for Invoices and Forms
AI OCR Intelligence System
"""

import json
import re
from pathlib import Path

def extract_information(text: str) -> dict:
    """
    Parses cleaned OCR document text to extract key invoice/form fields:
    - Invoice Number
    - Date
    - Customer Name
    - Line Items (Item Name & Price)
    - Total Amount
    """
    data = {
        "invoice_number": None,
        "date": None,
        "customer": None,
        "items": [],
        "subtotal": None,
        "total": None
    }

    # Extract Invoice Number
    invoice_match = re.search(
        r"(?:Invoice\s*(?:Number|No|#)|INV\s*#?|Invoice)\s*[:\-]\s*([A-Za-z0-9\-]+)",
        text,
        re.IGNORECASE
    )
    if not invoice_match:
        invoice_match = re.search(
            r"(?:Invoice\s*(?:Number|No|#)|INV\s*#)\s+([A-Za-z0-9\-]+)",
            text,
            re.IGNORECASE
        )
    if invoice_match:
        data["invoice_number"] = invoice_match.group(1).strip()

    # Extract Date
    date_match = re.search(
        r"Date\s*[:\-]?\s*([0-9]{1,4}[\/\-\.][0-9]{1,2}[\/\-\.][0-9]{2,4}|[A-Za-z]+\s+[0-9]{1,2},?\s+[0-9]{4})",
        text,
        re.IGNORECASE
    )
    if date_match:
        data["date"] = date_match.group(1).strip()

    # Extract Customer / Bill To
    customer_match = re.search(
        r"(?:Customer|Bill\s*To|Client)\s*[:\-]?\s*([^\n\r]+)",
        text,
        re.IGNORECASE
    )
    if customer_match:
        data["customer"] = customer_match.group(1).strip()

    # Extract Total / Grand Total / Amount Due
    total_match = re.search(
        r"(?:Grand\s*Total|Total|Amount\s*Due)\s*[:\-]?\s*(?:₹|Rs\.?|\$|EUR|€)?\s*([0-9,]+(?:\.[0-9]{2})?)",
        text,
        re.IGNORECASE
    )
    if total_match:
        data["total"] = total_match.group(1).replace(",", "").strip()

    # Parse Line Items (e.g., "Laptop 45000", "Mouse 1000", "Keyboard 2500")
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Skip header lines, customer, totals
        if any(keyword in line.lower() for keyword in ["invoice", "date", "customer", "total", "bill to", "tax", "subtotal"]):
            continue
        # Match pattern: <Item Description> <Price/Number>
        item_match = re.search(r"^([A-Za-z\s\-_]+?)\s+(?:₹|Rs\.?|\$|EUR|€)?\s*([0-9,]+(?:\.[0-9]{2})?)$", line)
        if item_match:
            desc = item_match.group(1).strip()
            price = item_match.group(2).replace(",", "").strip()
            if len(desc) >= 2 and not desc.lower().startswith("phone"):
                data["items"].append({"name": desc, "price": price})

    return data

def save_information(data: dict, output_path: str | Path = "output/extracted.json") -> Path:
    """Saves structured data dictionary as indented JSON file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return path
