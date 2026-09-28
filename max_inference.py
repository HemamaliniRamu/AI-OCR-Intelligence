"""
max_inference.py - Modular MAX (Modular Accelerated Execution) Inference Client
AI OCR Intelligence System
"""

import os
import re
import requests
from typing import Optional

# Default MAX Server settings (MAX Serve OpenAI-compatible REST API)
DEFAULT_MAX_HOST = os.getenv("MAX_SERVER_HOST", "http://localhost:8000")
DEFAULT_MODEL_NAME = os.getenv("MAX_MODEL_NAME", "modular/llama-3.1-8b-instruct")

class MAXEngineClient:
    """
    Client for interacting with Modular MAX Serve local inference server.
    MAX Serve accelerates model execution using Modular's compiled execution graph.
    """

    def __init__(self, base_url: str = DEFAULT_MAX_HOST, model_name: str = DEFAULT_MODEL_NAME):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    def is_online(self) -> bool:
        """Checks whether the MAX Serve server is running and reachable."""
        try:
            # Check models list or health endpoint
            resp = requests.get(f"{self.base_url}/v1/models", timeout=2.0)
            return resp.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list[str]:
        """Returns the list of loaded models from MAX Serve."""
        try:
            resp = requests.get(f"{self.base_url}/v1/models", timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                return [m["id"] for m in data.get("data", [])]
        except Exception:
            pass
        return []

    def generate_chat_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 512
    ) -> dict:
        """
        Sends an inference request to MAX Serve.
        Returns a dict with 'answer', 'model', 'server_online', and 'error'.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        if not self.is_online():
            return {
                "answer": None,
                "model": self.model_name,
                "server_online": False,
                "error": (
                    f"Modular MAX server is not reachable at {self.base_url}.\n"
                    f"To start MAX Serve, run:\n"
                    f"  max serve --model {self.model_name} --port 8000"
                )
            }

        try:
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            resp = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                timeout=30.0
            )
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return {
                    "answer": content,
                    "model": data.get("model", self.model_name),
                    "server_online": True,
                    "error": None
                }
            else:
                return {
                    "answer": None,
                    "model": self.model_name,
                    "server_online": True,
                    "error": f"MAX server returned HTTP {resp.status_code}: {resp.text}"
                }
        except Exception as e:
            return {
                "answer": None,
                "model": self.model_name,
                "server_online": False,
                "error": f"Connection error: {str(e)}"
            }

def heuristic_document_answer(document_text: str, structured_data: dict, question: str) -> str:
    """
    Context-aware heuristic responder used when MAX server is offline.
    Allows immediate testing and demonstration of the pipeline.
    """
    q = question.lower()
    inv = structured_data.get("invoice_number")
    date = structured_data.get("date")
    customer = structured_data.get("customer")
    total = structured_data.get("total")
    items = structured_data.get("items", [])

    if "total" in q or "amount" in q or "cost" in q or "price" in q:
        if "laptop" in q:
            for item in items:
                if "laptop" in item["name"].lower():
                    return f"The laptop costs {item['price']}."
        if "mouse" in q:
            for item in items:
                if "mouse" in item["name"].lower():
                    return f"The mouse costs {item['price']}."
        if total:
            return f"The total amount on this document is {total}."

    if "invoice" in q or "number" in q:
        if inv:
            return f"The invoice number is {inv}."

    if "customer" in q or "who" in q or "buyer" in q or "client" in q:
        if customer:
            return f"The customer is {customer}."

    if "date" in q or "when" in q:
        if date:
            return f"The invoice was issued on {date}."

    if "item" in q or "product" in q or "purchased" in q or "list" in q:
        if items:
            item_list = ", ".join([f"{it['name']} ({it['price']})" for it in items])
            return f"Purchased items: {item_list}."

    if "expensive" in q:
        if items:
            sorted_items = sorted(items, key=lambda x: float(re.sub(r'[^\d.]', '', x["price"]) or 0), reverse=True)
            top = sorted_items[0]
            return f"The most expensive item is {top['name']} at {top['price']}."

    # Fallback search inside document
    for line in document_text.split("\n"):
        if any(word in line.lower() for word in q.split() if len(word) > 3):
            return f"Relevant line from document: {line.strip()}"

    return "Based on the document, I could not find a specific answer to that question."
