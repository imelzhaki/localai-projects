import json
import os
from ollama import Client

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")

FALLBACK_RESULT = {
    "department": "GENERAL",
    "priority": "MEDIUM",
    "category": "INQUIRY",
    "summary": "",
}

SYSTEM_PROMPT = """You are a precise JSON-only data extraction engine.

CRITICAL RULES:
1. You MUST respond strictly with a valid JSON object matching the requested schema.
2. Do NOT include any intro text, explanations, or conversational phrases.
3. Do NOT use Markdown code blocks or code fences (do NOT use ```json or ```).
4. All keys and string values must be enclosed in double quotes.
5. Ensure the JSON is syntactically valid and parseable by standard JSON.parse() engines.
6. If any requested field cannot be determined, set its value to null or an empty string.

Output schema:
{
  "department": "IT_SUPPORT | HR | FINANCE | GENERAL",
  "priority": "LOW | MEDIUM | HIGH | URGENT",
  "category": "HARDWARE_FAILURE | SOFTWARE_ISSUE | NETWORK | LEAVE_REQUEST | PAYROLL | ONBOARDING | INVOICE | REIMBURSEMENT | BUDGET | INQUIRY | FEEDBACK",
  "summary": "string"
}"""


def classify_message(message, host=OLLAMA_HOST, model=OLLAMA_MODEL):
    """Classify a free-text message into a structured JSON dict via Ollama."""
    client = Client(host=host)
    user_prompt = (
        "Classify the following message into the JSON schema above.\n\n"
        f"Input text:\n{message}"
    )
    try:
        response = client.chat(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            format="json",
            options={"temperature": 0.1},
        )
        content = response.message.content
        result = json.loads(content)
        result.setdefault("department", "GENERAL")
        result.setdefault("priority", "MEDIUM")
        result.setdefault("category", "INQUIRY")
        result.setdefault("summary", message)
        return result
    except (json.JSONDecodeError, KeyError, AttributeError, Exception):
        result = dict(FALLBACK_RESULT)
        result["summary"] = message
        return result
