import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app


def test_process_message_classifies_and_routes():
    mock_classification = {
        "department": "IT_SUPPORT",
        "priority": "HIGH",
        "category": "HARDWARE_FAILURE",
        "summary": "Printer macet",
    }

    with patch("app.ollama_client.classify_message", return_value=mock_classification) as mock_classify:
        with patch("app.dispatcher.route_notification") as mock_route:
            app.process_message("Printer lantai 2 macet")

    mock_classify.assert_called_once_with("Printer lantai 2 macet")
    mock_route.assert_called_once_with(mock_classification)


def test_process_message_handles_ollama_error():
    with patch("app.ollama_client.classify_message", side_effect=Exception("Ollama down")):
        # Should not raise; process_message handles errors internally
        app.process_message("any message")


def test_extract_text_from_update():
    update = {
        "update_id": 1,
        "message": {"message_id": 5, "chat": {"id": 123}, "text": "Halo"},
    }
    assert app.extract_text_from_update(update) == "Halo"


def test_extract_text_from_update_returns_none_for_non_message():
    update = {"update_id": 2, "edited_message": {}}
    assert app.extract_text_from_update(update) is None
