import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dispatcher import validate_classification, route_notification, format_notification


def test_validate_classification_returns_same_when_valid():
    classification = {
        "department": "IT_SUPPORT",
        "priority": "HIGH",
        "category": "HARDWARE_FAILURE",
        "summary": "Printer macet",
    }
    result = validate_classification(classification)
    assert result == classification


def test_validate_classification_falls_back_on_invalid_department():
    classification = {
        "department": "INVALID_DEPT",
        "priority": "HIGH",
        "category": "HARDWARE_FAILURE",
        "summary": "Printer macet",
    }
    result = validate_classification(classification)
    assert result["department"] == "GENERAL"


def test_validate_classification_falls_back_on_invalid_priority():
    classification = {
        "department": "IT_SUPPORT",
        "priority": "CRITICAL",
        "category": "HARDWARE_FAILURE",
        "summary": "Printer macet",
    }
    result = validate_classification(classification)
    assert result["priority"] == "MEDIUM"


def test_validate_classification_falls_back_on_invalid_category():
    classification = {
        "department": "IT_SUPPORT",
        "priority": "HIGH",
        "category": "FLYING_CARPET",
        "summary": "Printer macet",
    }
    result = validate_classification(classification)
    assert result["category"] == "INQUIRY"


def test_route_notification_sends_to_correct_group():
    classification = {
        "department": "IT_SUPPORT",
        "priority": "HIGH",
        "category": "HARDWARE_FAILURE",
        "summary": "Printer lantai 2 macet",
    }
    mock_client = MagicMock()
    mock_client.send_message.return_value = {"ok": True}

    with patch("dispatcher.TelegramClient", return_value=mock_client):
        with patch("dispatcher.DEPARTMENT_GROUPS", {"IT_SUPPORT": 123}):
            route_notification(classification)

    mock_client.send_message.assert_called_once()
    args, kwargs = mock_client.send_message.call_args
    assert kwargs["chat_id"] == 123
    assert "IT_SUPPORT" in kwargs["text"]
    assert "HARDWARE_FAILURE" in kwargs["text"]
    assert "Printer lantai 2 macet" in kwargs["text"]


def test_format_notification_contains_all_fields():
    classification = {
        "department": "IT_SUPPORT",
        "priority": "HIGH",
        "category": "HARDWARE_FAILURE",
        "summary": "Printer lantai 2 macet",
    }
    text = format_notification(classification)
    assert "IT_SUPPORT" in text
    assert "HIGH" in text
    assert "HARDWARE_FAILURE" in text
    assert "Printer lantai 2 macet" in text
