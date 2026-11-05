import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app


def test_build_user_message():
    result = app.build_user_message("hello")
    assert result == {"role": "user", "content": "hello"}


def test_build_assistant_message():
    result = app.build_assistant_message("hi")
    assert result == {"role": "assistant", "content": "hi"}


def test_handle_user_input_tanpa_panggilan_alat(monkeypatch):
    """Pesan tanpa panggilan alat → respons langsung dari model."""
    kirim_ke_model = []

    def fake_chat_with_tools(messages, tools=None):
        kirim_ke_model.extend(messages)
        return "Halo, ada yang bisa saya bantu?", []

    monkeypatch.setattr("app.chat_with_tools", fake_chat_with_tools)
    monkeypatch.setattr("app.st.chat_input", lambda *a, **k: "Halo")

    app.st.session_state = SimpleNamespace(messages=[])

    class PalsuChatMessage:
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False

    monkeypatch.setattr("app.st.chat_message", lambda role: PalsuChatMessage())
    monkeypatch.setattr("app.st.markdown", lambda *a, **k: None)
    monkeypatch.setattr("app.st.info", lambda *a, **k: None)
    monkeypatch.setattr("app.st.error", lambda *a, **k: None)
    monkeypatch.setattr("app.st.write_stream", lambda gen: list(gen)[-1])
    monkeypatch.setattr("app.save_history", lambda messages: None)

    app.handle_user_input()

    assert len(kirim_ke_model) >= 1
    assert kirim_ke_model[0]["role"] == "user"
    assert kirim_ke_model[0]["content"] == "Halo"


def test_handle_user_input_reset_menghapus_riwayat(monkeypatch):
    """Perintah /reset menghapus semua riwayat percakapan."""
    pesan_dihapus = []

    def fake_save_history(messages):
        pesan_dihapus.extend(messages)

    monkeypatch.setattr("app.save_history", fake_save_history)
    monkeypatch.setattr("app.st.chat_input", lambda *a, **k: "/reset")

    app.st.session_state = SimpleNamespace(messages=[{"role": "user", "content": "Halo"}])

    class PalsuChatMessage:
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False

    monkeypatch.setattr("app.st.chat_message", lambda role: PalsuChatMessage())
    monkeypatch.setattr("app.st.markdown", lambda *a, **k: None)
    monkeypatch.setattr("app.st.info", lambda *a, **k: None)
    monkeypatch.setattr("app.st.error", lambda *a, **k: None)
    monkeypatch.setattr("app.st.success", lambda *a, **k: None)
    monkeypatch.setattr("app.st.write_stream", lambda gen: list(gen)[-1])

    app.handle_user_input()

    assert app.st.session_state.messages == []
    assert pesan_dihapus == []
