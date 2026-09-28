"""
test_extractor.py - Test Structured Data Extraction
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from extractor import extract_information, save_information

def main():
    print("=== Testing Structured Information Extraction ===")
    sample_text = """
ABC Electronics Inc.
TAX INVOICE
Invoice Number: INV-1001
Date: 13-09-2026
Customer: Hema
Payment Mode: Online / UPI

Item Description              Amount (INR)
Laptop                        45000
Mouse                         1000

Total: 46000
"""
    data = extract_information(sample_text)
    print("\n--- Extracted Dictionary ---")
    print(data)

    out_file = ROOT / "output" / "extracted.json"
    save_information(data, out_file)
    print(f"\nSaved structured JSON to: {out_file}")

    assert data["invoice_number"] == "INV-1001", "Invoice number mismatch"
    assert data["date"] == "13-09-2026", "Date mismatch"
    assert data["customer"] == "Hema", "Customer mismatch"
    assert data["total"] == "46000", "Total mismatch"
    assert len(data["items"]) >= 2, "Items extraction mismatch"

    print("\nExtraction Test Passed Successfully!")

if __name__ == "__main__":
    main()
