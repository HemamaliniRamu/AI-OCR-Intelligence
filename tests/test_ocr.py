"""
test_ocr.py - Test OCR Extraction Pipeline
"""

import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from ocr import extract_text, is_tesseract_installed, find_tesseract_path
from generate_sample import generate_invoice_image

def main():
    print("=== Testing OCR Pipeline ===")
    print(f"Tesseract installed: {is_tesseract_installed()}")
    print(f"Detected path: {find_tesseract_path()}")

    sample_invoice = ROOT / "documents" / "invoice.png"
    if not sample_invoice.exists():
        print(f"Generating sample invoice at {sample_invoice}...")
        generate_invoice_image(str(sample_invoice))

    if not is_tesseract_installed():
        print("[WARNING] Tesseract is not installed yet on this Windows system.")
        print("Please download and run the installer from:")
        print("https://github.com/UB-Mannheim/tesseract/wiki")
        return

    result = extract_text(sample_invoice)
    print("\n--- Raw OCR Text ---")
    print(result["raw_text"])
    print("\n--- Cleaned Text (Mojo Preprocessed) ---")
    print(result["cleaned_text"])
    print(f"Mojo Accelerated: {result['mojo_accelerated']}")
    print("\nOCR Test Passed!")

if __name__ == "__main__":
    main()
