import os
import requests

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/{method}"


class TelegramClient:
    def __init__(self, token=None):
        self.token = token or os.environ.get("TELEGRAM_BOT_TOKEN", "")

    def _url(self, method):
        return TELEGRAM_API_BASE.format(token=self.token, method=method)

    def send_message(self, chat_id, text):
        """Send a text message to a Telegram chat. Returns the API response JSON."""
        url = self._url("sendMessage")
        payload = {"chat_id": chat_id, "text": text}
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_updates(self, offset=0, limit=100, timeout=30):
        """Poll Telegram for new updates. Returns a list of update dicts."""
        url = self._url("getUpdates")
        params = {"offset": offset, "limit": limit, "timeout": timeout}
        response = requests.get(url, params=params, timeout=timeout + 5)
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            return []
        return data.get("result", [])
