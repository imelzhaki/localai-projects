import sys
import os
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app


def test_build_user_message():
    result = app.build_user_message("hello")
    assert result == {"role": "user", "content": "hello"}


def test_build_assistant_message():
    result = app.build_assistant_message("hi")
    assert result == {"role": "assistant", "content": "hi"}


def _siapkan_mock_streamlit(monkeypatch, prompt, isi_url, daftar_url):
    """Palsukan komponen Streamlit dan fungsi pengambilan URL untuk pengujian handle_user_input."""

    kirim_ke_model = []

    def fake_chat_stream(messages, model="llama3.2:3b"):
        kirim_ke_model.extend(messages)
        yield "Balasan tiruan"

    monkeypatch.setattr("app.chat_stream", fake_chat_stream)
    monkeypatch.setattr("app.st.chat_input", lambda *a, **k: prompt)
    monkeypatch.setattr(
        "app.fetch_urls_in_text",
        lambda teks: (isi_url, daftar_url),
    )

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

    return kirim_ke_model


def test_handle_user_input_sisipkan_konteks_url(monkeypatch):
    """handle_user_input menyisipkan pesan sistem dengan konten URL saat user sertakan URL."""

    kirim_ke_model = _siapkan_mock_streamlit(
        monkeypatch,
        prompt="Baca https://contoh.com untuk info",
        isi_url="Konten tiruan dari contoh.com",
        daftar_url=["https://contoh.com"],
    )

    app.handle_user_input()

    assert len(kirim_ke_model) >= 1
    assert kirim_ke_model[0]["role"] == "system"
    assert "Konten tiruan dari contoh.com" in kirim_ke_model[0]["content"]


def test_handle_user_input_tanpa_url_tidak_sisipkan_sistem(monkeypatch):
    """handle_user_input tidak menyisipkan pesan sistem saat tidak ada URL."""

    kirim_ke_model = _siapkan_mock_streamlit(
        monkeypatch,
        prompt="Halo apa kabar",
        isi_url="",
        daftar_url=[],
    )

    app.handle_user_input()

    assert len(kirim_ke_model) >= 1
    assert kirim_ke_model[0]["role"] == "user"
    assert all(m["role"] != "system" for m in kirim_ke_model)
