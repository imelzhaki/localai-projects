from typing import Type, TypeVar
from pydantic import BaseModel
from ollama import Client as OllamaClient


T = TypeVar("T", bound=BaseModel)


class LLMOutputError(Exception):
    """Raised when LLM output is invalid after all retries."""


def structured_chat(
    model: str,
    system: str,
    user: str,
    schema: Type[T],
    base_url: str = "http://localhost:11434",
    temperature: float = 0.0,
    num_ctx: int = 8192,
    think: bool = False,
    timeout: int = 60,
    max_retries: int = 3,
) -> T:
    """Send a structured chat request to Ollama and return a validated Pydantic model."""
    client = OllamaClient(host=base_url)
    schema_json = schema.schema()

    for attempt in range(max_retries):
        try:
            response = client.chat(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                format=schema_json,
                options={
                    "temperature": temperature,
                    "num_ctx": num_ctx,
                    "think": think,
                },
            )
            content = response["message"]["content"]
            return schema.parse_raw(content)
        except Exception as exc:
            if attempt == max_retries - 1:
                raise LLMOutputError(
                    f"Invalid LLM output after {max_retries} retries: {exc}"
                ) from exc
    raise LLMOutputError("Invalid LLM output after retries")
