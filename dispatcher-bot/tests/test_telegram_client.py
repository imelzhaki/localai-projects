import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from telegram_client import TelegramClient


def test_send_message_posts_to_telegram_api():
    client = TelegramClient(token="test-token")
    mock_response = MagicMock()
    mock_response.json.return_value = {"ok": True, "result": {"message_id": 1}}
    mock_response.raise_for_status.return_value = None

    with patch("telegram_client.requests.post", return_value=mock_response) as mock_post:
        result = client.send_message(chat_id=123, text="hello")

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "sendMessage" in args[0]
    assert kwargs["json"]["chat_id"] == 123
    assert kwargs["json"]["text"] == "hello"
    assert result == {"ok": True, "result": {"message_id": 1}}


def test_get_updates_returns_messages():
    client = TelegramClient(token="test-token")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "ok": True,
        "result": [
            {
                "update_id": 1,
                "message": {
                    "message_id": 5,
                    "chat": {"id": 123},
                    "text": "Printer macet",
                },
            }
        ],
    }
    mock_response.raise_for_status.return_value = None

    with patch("telegram_client.requests.get", return_value=mock_response) as mock_get:
        updates = client.get_updates(offset=0, timeout=10)

    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert "getUpdates" in args[0]
    assert kwargs["params"]["offset"] == 0
    assert kwargs["params"]["timeout"] == 10
    assert len(updates) == 1
    assert updates[0]["message"]["text"] == "Printer macet"
