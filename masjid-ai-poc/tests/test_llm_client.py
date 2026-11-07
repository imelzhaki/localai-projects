import pytest
from unittest.mock import MagicMock, patch
from pydantic import BaseModel
from app.llm.client import structured_chat, LLMOutputError


class EntrySchema(BaseModel):
    donor_name: str
    amount_raw: str


def test_structured_chat_returns_validated_model():
    with patch("app.llm.client.OllamaClient") as MockClient:
        instance = MockClient.return_value
        instance.chat.return_value = {
            "message": {"content": '{"donor_name": "H. Ahmad", "amount_raw": "2.500.000"}'}
        }

        result = structured_chat(
            model="qwen3:4b",
            system="Extract data",
            user="H. Ahmad zakat 2.500.000",
            schema=EntrySchema,
        )

        assert isinstance(result, EntrySchema)
        assert result.donor_name == "H. Ahmad"
        assert result.amount_raw == "2.500.000"


def test_structured_chat_raises_on_invalid_output():
    with patch("app.llm.client.OllamaClient") as MockClient:
        instance = MockClient.return_value
        instance.chat.side_effect = Exception("Invalid JSON")

        with pytest.raises(LLMOutputError):
            structured_chat(
                model="qwen3:4b",
                system="Extract data",
                user="bad input",
                schema=EntrySchema,
            )
