import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from history import load_history, save_history, HISTORY_PATH


def test_save_and_load_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr("history.HISTORY_PATH", tmp_path / "history.json")
    messages = [
        {"role": "user", "content": "Bagaimana cara menghitung luas lingkaran?"},
        {"role": "assistant", "content": "Apa yang kamu ketahui tentang lingkaran?"},
    ]
    save_history(messages)
    loaded = load_history()
    assert loaded == messages


def test_missing_file_returns_empty_list(tmp_path, monkeypatch):
    monkeypatch.setattr("history.HISTORY_PATH", tmp_path / "nonexistent.json")
    assert load_history() == []


def test_corrupt_json_returns_empty_list(tmp_path, monkeypatch):
    monkeypatch.setattr("history.HISTORY_PATH", tmp_path / "bad.json")
    (tmp_path / "bad.json").write_text("{not valid json", encoding="utf-8")
    assert load_history() == []
