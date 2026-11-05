import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ollama_client import chat_stream


def test_chat_stream_yields_chunks(monkeypatch):
    """chat_stream harus menghasilkan potongan teks dari klien ollama tiruan."""
    chunks = ["Apa ", "yang ", "kamu ", "ketahui ", "tentang ", "lingkaran?", "?"]

    class FakeMessage:
        def __init__(self, content):
            self.content = content

    class FakeChunk:
        def __init__(self, content):
            self.message = FakeMessage(content)

    class FakeClient:
        def chat(self, model, messages, stream):
            assert model == "llama3.2:3b"
            assert len(messages) >= 1
            for c in chunks:
                yield FakeChunk(c)

    monkeypatch.setattr("ollama_client.Client", lambda host: FakeClient())

    result = list(chat_stream([{"role": "user", "content": "Say hi"}]))
    assert result == chunks


def test_chat_stream_uses_default_model(monkeypatch):
    """chat_stream harus default ke llama3.2:3b jika tidak ada model yang diberikan."""

    class FakeMessage:
        def __init__(self, content):
            self.content = content

    class FakeChunk:
        def __init__(self, content):
            self.message = FakeMessage(content)

    class FakeClient:
        def chat(self, model, messages, stream):
            assert model == "llama3.2:3b"
            yield FakeChunk("ok")

    captured = {}

    def fake_client(host):
        captured["host"] = host
        return FakeClient()

    monkeypatch.setattr("ollama_client.Client", fake_client)
    monkeypatch.setattr("ollama_client.OLLAMA_HOST", "http://localhost:11434")

    list(chat_stream([{"role": "user", "content": "x"}]))
    assert captured["host"] == "http://localhost:11434"
