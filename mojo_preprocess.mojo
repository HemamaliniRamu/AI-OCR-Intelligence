// mojo_preprocess.mojo
// High-performance text preprocessing and normalization in Mojo
// for the AI OCR Intelligence System

import sys

fn clean_text(text: String) -> String:
    """
    Cleans raw OCR output text:
    - Normalizes double/multiple newlines
    - Collapses redundant whitespace
    - Strips leading/trailing noise
    """
    var result = text
    
    // Replace multiple newlines with single newline
    while result.find("\n\n") != -1:
        result = result.replace("\n\n", "\n")
    
    // Replace multiple consecutive spaces
    while result.find("  ") != -1:
        result = result.replace("  ", " ")
        
    // Normalize common OCR colon spacing irregularities
    result = result.replace(" :", ":")
    result = result.replace(" -", "-")
    
    return result.strip()

fn normalize_invoice_tokens(text: String) -> String:
    """
    Normalizes known invoice headers and token markers
    to standard forms for downstream regex/NLP extraction.
    """
    var cleaned = clean_text(text)
    cleaned = cleaned.replace("Invoice No:", "Invoice Number:")
    cleaned = cleaned.replace("INV NO:", "Invoice Number:")
    cleaned = cleaned.replace("Bill To:", "Customer:")
    cleaned = cleaned.replace("Grand Total:", "Total:")
    return cleaned

fn main() raises:
    print("========================================")
    print(" Modular Mojo OCR Preprocessor (v0.1.0)")
    print("========================================")

    var args = sys.argv()
    if len(args) >= 3:
        // CLI File mode: mojo mojo_preprocess.mojo <input_path> <output_path>
        var input_path = args[1]
        var output_path = args[2]
        
        with open(input_path, "r") as f:
            var content = f.read()
            var processed = normalize_invoice_tokens(content)
            with open(output_path, "w") as out:
                out.write(processed)
        print("Successfully processed via Mojo: " + output_path)
    else:
        // Demo / Verification test
        var raw_ocr = "ABC Electronics\n\n\nInvoice No:   INV-1001\n\nDate : 13-09-2026\n\nCustomer :  Hema\n\nLaptop  45000\nMouse   1000\n\nGrand Total :   46000\n"
        print("[Raw OCR Input]:")
        print(raw_ocr)
        print("----------------------------------------")
        var cleaned = normalize_invoice_tokens(raw_ocr)
        print("[Mojo Preprocessed Output]:")
        print(cleaned)
        print("========================================")
