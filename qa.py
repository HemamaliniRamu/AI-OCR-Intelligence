"""
qa.py - Question Answering over OCR Documents with LangChain & Modular MAX
AI OCR Intelligence System
"""

import json
from langchain_core.prompts import PromptTemplate
from max_inference import MAXEngineClient, heuristic_document_answer

# LangChain Prompt Template for OCR Intelligence
DOCUMENT_QA_TEMPLATE = """You are an intelligent Document AI Assistant powered by Modular MAX and LangChain.
Your job is to answer questions accurately based ONLY on the provided document text and structured data extracted from an invoice or form.

---------------------
DOCUMENT TEXT (OCR):
{document}
---------------------
STRUCTURED EXTRACTED DATA (JSON):
{structured_data}
---------------------

USER QUESTION: {question}

INSTRUCTIONS:
1. Answer the question directly, concisely, and accurately.
2. If the user asks for numbers, totals, or item names, quote them exactly as shown.
3. If the answer cannot be determined from the document, say "I cannot find this information in the document."

ANSWER:"""

prompt_template = PromptTemplate(
    input_variables=["document", "structured_data", "question"],
    template=DOCUMENT_QA_TEMPLATE
)

def create_prompt(document: str, structured_data: dict, question: str) -> str:
    """Generates the formatted prompt using LangChain PromptTemplate."""
    formatted_json = json.dumps(structured_data, indent=2)
    return prompt_template.format(
        document=document.strip(),
        structured_data=formatted_json,
        question=question.strip()
    )

def answer_document_question(
    document_text: str,
    structured_data: dict,
    question: str,
    max_client: MAXEngineClient | None = None
) -> dict:
    """
    Orchestrates LangChain prompt building and Modular MAX inference.
    
    Returns:
    {
        "answer": str,
        "engine": "Modular MAX Serve" | "Heuristic OCR Fallback",
        "model": str,
        "server_online": bool,
        "error": str | None
    }
    """
    if max_client is None:
        max_client = MAXEngineClient()

    formatted_prompt = create_prompt(document_text, structured_data, question)

    if max_client.is_online():
        result = max_client.generate_chat_completion(
            prompt=formatted_prompt,
            system_prompt="You are a precise document extraction and Q&A assistant."
        )
        if result["answer"]:
            return {
                "answer": result["answer"].strip(),
                "engine": f"Modular MAX Engine ({result['model']})",
                "model": result["model"],
                "server_online": True,
                "error": None
            }

    # If MAX server is offline or returned empty, provide the context-aware answer
    fallback_ans = heuristic_document_answer(document_text, structured_data, question)
    return {
        "answer": fallback_ans,
        "engine": "Heuristic Pipeline (MAX Serve offline)",
        "model": "rule-based context parser",
        "server_online": False,
        "error": "MAX Serve offline: using local document extractor. Run 'max serve' to activate the full neural model."
    }
