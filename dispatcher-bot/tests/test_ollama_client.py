import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ollama_client import classify_message, SYSTEM_PROMPT


def test_classify_message_returns_valid_json_dict():
    mock_chunk = MagicMock()
    mock_chunk.message.content = (
        '{"department": "IT_SUPPORT", "priority": "HIGH", '
        '"category": "HARDWARE_FAILURE", "summary": "Printer macet"}'
    )
    mock_client = MagicMock()
    mock_client.chat.return_value = mock_chunk

    with patch("ollama_client.Client", return_value=mock_client):
        result = classify_message("Printer lantai 2 macet total")

    assert result["department"] == "IT_SUPPORT"
    assert result["priority"] == "HIGH"
    assert result["category"] == "HARDWARE_FAILURE"
    assert "Printer" in result["summary"]


def test_classify_message_uses_format_json():
    mock_chunk = MagicMock()
    mock_chunk.message.content = '{"department": "GENERAL", "priority": "MEDIUM", "category": "INQUIRY", "summary": "halo"}'
    mock_client = MagicMock()
    mock_client.chat.return_value = mock_chunk

    with patch("ollama_client.Client", return_value=mock_client) as mock_client_class:
        classify_message("halo")

    _, kwargs = mock_client_class.return_value.chat.call_args
    assert kwargs.get("format") == "json"


def test_classify_message_invalid_json_returns_general_fallback():
    mock_chunk = MagicMock()
    mock_chunk.message.content = "not valid json at all"
    mock_client = MagicMock()
    mock_client.chat.return_value = mock_chunk

    with patch("ollama_client.Client", return_value=mock_client):
        result = classify_message("random text")

    assert result["department"] == "GENERAL"
    assert result["priority"] == "MEDIUM"
    assert result["category"] == "INQUIRY"
    assert result["summary"] == "random text"


def test_system_prompt_requires_json_only():
    assert "JSON" in SYSTEM_PROMPT
    assert "code fence" in SYSTEM_PROMPT or "```" in SYSTEM_PROMPT
    assert "department" in SYSTEM_PROMPT
