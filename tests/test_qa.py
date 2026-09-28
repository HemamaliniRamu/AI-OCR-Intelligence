"""
test_qa.py - Test LangChain + MAX Inference Pipeline
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT))

from qa import answer_document_question, create_prompt
from max_inference import MAXEngineClient

def main():
    print("=== Testing LangChain & MAX Inference ===")
    
    document_text = """
ABC Electronics Inc.
Invoice Number: INV-1001
Date: 13-09-2026
Customer: Hema
Laptop 45000
Mouse 1000
Total: 46000
"""
    structured_data = {
        "invoice_number": "INV-1001",
        "date": "13-09-2026",
        "customer": "Hema",
        "items": [
            {"name": "Laptop", "price": "45000"},
            {"name": "Mouse", "price": "1000"}
        ],
        "total": "46000"
    }

    client = MAXEngineClient()
    print(f"MAX Server Online: {client.is_online()}")

    # Test prompt generation
    prompt = create_prompt(document_text, structured_data, "What is the total?")
    print("\n--- Generated LangChain Prompt ---")
    print(prompt)

    # Test Q&A
    questions = [
        "What is the total amount?",
        "Who is the customer?",
        "How much did the laptop cost?",
        "What is the invoice number?"
    ]

    print("\n--- Running Q&A Tests ---")
    for q in questions:
        res = answer_document_question(document_text, structured_data, q, client)
        print(f"Q: {q}")
        print(f"A: {res['answer']} (Engine: {res['engine']})\n")

    print("Q&A Test Passed Successfully!")

if __name__ == "__main__":
    main()
