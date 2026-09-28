"""
ocr.py - Optical Character Recognition Engine with Mojo Preprocessing Bridge
AI OCR Intelligence System
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

# Standard Windows Tesseract Installation Candidate Paths
TESSERACT_CANDIDATES = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
    os.path.expandvars(r"%USERPROFILE%\AppData\Local\Tesseract-OCR\tesseract.exe"),
]

def find_tesseract_path() -> str | None:
    """Finds the Tesseract executable path on Windows or from system PATH."""
    which_path = shutil.which("tesseract")
    if which_path and os.path.exists(which_path):
        return which_path
    for path in TESSERACT_CANDIDATES:
        if os.path.exists(path):
            return path
    return None

# Configure Tesseract path if found
tess_path = find_tesseract_path()
if tess_path:
    pytesseract.pytesseract.tesseract_cmd = tess_path

def is_tesseract_installed() -> bool:
    """Checks if Tesseract is detected and executable."""
    return find_tesseract_path() is not None

def is_mojo_installed() -> bool:
    """Checks if the Mojo compiler CLI is available."""
    return shutil.which("mojo") is not None

def run_mojo_preprocess(raw_text: str, project_dir: str | Path | None = None) -> tuple[str, bool]:
    """
    Passes raw OCR text to mojo_preprocess.mojo if Mojo is installed.
    Falls back gracefully to native Python text cleaning if Mojo is not installed.
    Returns (cleaned_text, used_mojo_boolean).
    """
    if project_dir is None:
        project_dir = Path(__file__).parent
    else:
        project_dir = Path(project_dir)

    mojo_script = project_dir / "mojo_preprocess.mojo"

    if is_mojo_installed() and mojo_script.exists():
        try:
            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt", encoding="utf-8") as in_f:
                in_f.write(raw_text)
                in_path = in_f.name

            out_path = in_path + ".out.txt"

            result = subprocess.run(
                ["mojo", str(mojo_script), in_path, out_path],
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.returncode == 0 and os.path.exists(out_path):
                with open(out_path, "r", encoding="utf-8") as out_f:
                    cleaned = out_f.read()
                try:
                    os.remove(in_path)
                    os.remove(out_path)
                except OSError:
                    pass
                return cleaned, True
        except Exception:
            pass  # Fall through to Python fallback on any runtime error

    # Python Fallback (mirrors Mojo logic)
    cleaned = raw_text
    while "\n\n" in cleaned:
        cleaned = cleaned.replace("\n\n", "\n")
    while "  " in cleaned:
        cleaned = cleaned.replace("  ", " ")
    cleaned = cleaned.replace("Invoice No:", "Invoice Number:")
    cleaned = cleaned.replace("INV NO:", "Invoice Number:")
    cleaned = cleaned.replace("Bill To:", "Customer:")
    cleaned = cleaned.replace("Grand Total:", "Total:")
    return cleaned.strip(), False

def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    """Applies grayscale and contrast enhancement to optimize OCR clarity."""
    gray = image.convert("L")
    enhancer = ImageEnhance.Contrast(gray)
    enhanced = enhancer.enhance(1.8)
    return enhanced

def extract_text(image_input: str | Path | Image.Image, use_mojo: bool = True) -> dict:
    """
    Main OCR extraction function.
    Returns dictionary with:
    - raw_text: Raw output from Tesseract
    - cleaned_text: Normalized text (via Mojo or fallback)
    - mojo_accelerated: True if Mojo binary executed the preprocessing
    """
    if not is_tesseract_installed():
        raise FileNotFoundError(
            "Tesseract OCR executable not found!\n"
            "Please install Tesseract OCR for Windows from: https://github.com/UB-Mannheim/tesseract/wiki\n"
            f"Expected locations: {TESSERACT_CANDIDATES}"
        )

    if isinstance(image_input, (str, Path)):
        image = Image.open(image_input)
    else:
        image = image_input

    # Optimize image for OCR
    processed_img = preprocess_image_for_ocr(image)

    # Perform OCR
    raw_text = pytesseract.image_to_string(processed_img)

    if use_mojo:
        cleaned_text, mojo_used = run_mojo_preprocess(raw_text)
    else:
        cleaned_text = raw_text
        mojo_used = False

    return {
        "raw_text": raw_text,
        "cleaned_text": cleaned_text,
        "mojo_accelerated": mojo_used
    }
