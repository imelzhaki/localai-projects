import json
from pathlib import Path

HISTORY_PATH = Path("data/history.json")


def load_history():
    """Muat riwayat chat dari berkas JSON.

    Mengembalikan daftar dict pesan, atau daftar kosong jika berkas
    hilang atau berisi JSON yang tidak valid.
    """
    try:
        text = HISTORY_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return data


def save_history(messages):
    """Simpan riwayat chat ke berkas JSON.

    Membuat direktori induk jika belum ada.
    """
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_PATH.write_text(json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8")
