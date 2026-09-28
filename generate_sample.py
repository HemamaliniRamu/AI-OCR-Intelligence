"""
generate_sample.py - Generates a sample invoice image for testing the AI OCR Intelligence System
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def generate_invoice_image(output_path: str = "documents/invoice.png"):
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # 800 x 600 white background invoice
    width, height = 800, 600
    image = Image.new("RGB", (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Load default font
    font_large = ImageFont.load_default()

    # Draw border
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline=(180, 180, 180), width=2)

    # Header
    draw.text((50, 40), "ABC Electronics Inc.", fill=(20, 40, 100), font=font_large)
    draw.text((50, 65), "TAX INVOICE", fill=(50, 50, 50), font=font_large)

    # Meta
    draw.line([(50, 95), (width - 50, 95)], fill=(200, 200, 200), width=1)
    draw.text((50, 110), "Invoice Number: INV-1001", fill=(0, 0, 0), font=font_large)
    draw.text((50, 135), "Date: 13-09-2026", fill=(0, 0, 0), font=font_large)
    draw.text((50, 160), "Customer: Hema", fill=(0, 0, 0), font=font_large)
    draw.text((50, 185), "Payment Mode: Online / UPI", fill=(0, 0, 0), font=font_large)

    # Items Table Header
    draw.rectangle([(50, 230), (width - 50, 260)], fill=(240, 243, 246))
    draw.text((60, 240), "Item Description", fill=(30, 30, 30), font=font_large)
    draw.text((550, 240), "Amount (INR)", fill=(30, 30, 30), font=font_large)

    # Line Items
    draw.text((60, 280), "Laptop", fill=(0, 0, 0), font=font_large)
    draw.text((550, 280), "45000", fill=(0, 0, 0), font=font_large)

    draw.text((60, 320), "Mouse", fill=(0, 0, 0), font=font_large)
    draw.text((550, 320), "1000", fill=(0, 0, 0), font=font_large)

    draw.line([(50, 370), (width - 50, 370)], fill=(220, 220, 220), width=1)

    # Total Section
    draw.text((400, 400), "Total: 46000", fill=(10, 100, 20), font=font_large)

    # Footer
    draw.text((50, 520), "Thank you for your business! For queries contact support@abcelectronics.com", fill=(120, 120, 120), font=font_large)

    image.save(path)
    print(f"Sample invoice generated at: {path.resolve()}")

if __name__ == "__main__":
    generate_invoice_image()
