import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import DEPARTMENTS, PRIORITIES, CATEGORIES, DEPARTMENT_GROUPS, ADMIN_GROUP_ID
from telegram_client import TelegramClient


def validate_classification(classification):
    """Validate and normalize a classification dict. Falls back to GENERAL/MEDIUM/INQUIRY on invalid values."""
    result = dict(classification)

    if result.get("department") not in DEPARTMENTS:
        result["department"] = "GENERAL"

    if result.get("priority") not in PRIORITIES:
        result["priority"] = "MEDIUM"

    valid_categories = []
    for cats in CATEGORIES.values():
        valid_categories.extend(cats)
    if result.get("category") not in valid_categories:
        result["category"] = "INQUIRY"

    if not result.get("summary"):
        result["summary"] = ""

    return result


def format_notification(classification):
    """Format a classification dict into a human-readable notification text."""
    return (
        f"🎫 *Tiket Baru*\n"
        f"Departemen: {classification['department']}\n"
        f"Prioritas: {classification['priority']}\n"
        f"Kategori: {classification['category']}\n"
        f"Ringkasan: {classification['summary']}"
    )


def route_notification(classification, telegram_client=None):
    """Validate classification and send notification to the department's Telegram group."""
    classification = validate_classification(classification)
    department = classification["department"]
    chat_id = DEPARTMENT_GROUPS.get(department, ADMIN_GROUP_ID)

    if telegram_client is None:
        telegram_client = TelegramClient()

    text = format_notification(classification)
    return telegram_client.send_message(chat_id=chat_id, text=text)
