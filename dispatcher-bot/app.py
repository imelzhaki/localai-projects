import json
import os
import sys
import time
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import OLLAMA_HOST, OLLAMA_MODEL
import ollama_client
import dispatcher
from telegram_client import TelegramClient

logger = logging.getLogger(__name__)

HISTORY_PATH = os.path.join(os.path.dirname(__file__), "data", "history.json")


def extract_text_from_update(update):
    """Extract the text from a Telegram update, or None if it's not a text message."""
    message = update.get("message") or update.get("edited_message")
    if not message:
        return None
    return message.get("text")


def load_history():
    """Load processed message history from JSON file."""
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_history(history):
    """Save processed message history to JSON file."""
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def process_message(text, telegram_client=None):
    """Classify a message and route the notification. Returns the classification dict."""
    if telegram_client is None:
        telegram_client = TelegramClient()

    try:
        classification = ollama_client.classify_message(text)
        dispatcher.route_notification(classification)
        logger.info("Message classified and routed: %s", classification)
    except Exception as exc:
        logger.error("Failed to process message: %s", exc)
        classification = {
            "department": "GENERAL",
            "priority": "MEDIUM",
            "category": "INQUIRY",
            "summary": text,
        }
        try:
            dispatcher.route_notification(classification)
        except Exception as route_exc:
            logger.error("Failed to send fallback notification: %s", route_exc)

    return classification


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
        return

    client = TelegramClient(token=token)
    offset = 0
    history = load_history()

    logger.info("Dispatcher bot started. Polling for messages...")

    while True:
        try:
            updates = client.get_updates(offset=offset, timeout=30)
            for update in updates:
                offset = update["update_id"] + 1
                text = extract_text_from_update(update)
                if not text:
                    continue

                # Skip already-processed messages
                if any(h.get("update_id") == update["update_id"] for h in history):
                    continue

                classification = process_message(text, telegram_client=client)

                history.append(
                    {
                        "update_id": update["update_id"],
                        "message_id": update.get("message", {}).get("message_id"),
                        "text": text,
                        "classification": classification,
                    }
                )
                save_history(history)

        except KeyboardInterrupt:
            logger.info("Dispatcher bot stopped by user")
            break
        except Exception as exc:
            logger.error("Polling error: %s", exc)
            time.sleep(5)


if __name__ == "__main__":
    main()
