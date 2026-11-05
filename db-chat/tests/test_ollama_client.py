import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ollama_client import chat_with_tools


def test_chat_with_tools_returns_text_when_no_tool_call(monkeypatch):
    """Jika model tidak memanggil alat, kembalikan teks respons."""
    kirim = []

    class FakeMessage:
        def __init__(self, content, tool_calls=None):
            self.content = content
            self.tool_calls = tool_calls or []

    class FakeChunk:
        def __init__(self, content, tool_calls=None):
            self.message = FakeMessage(content, tool_calls)

    class FakeClient:
        def chat(self, model, messages, tools, stream):
            kirim.append((model, messages, tools))
            yield FakeChunk("Halo, ada yang bisa saya bantu?")

    monkeypatch.setattr("ollama_client.Client", lambda host: FakeClient())

    teks, panggilan = chat_with_tools(
        [{"role": "user", "content": "Halo"}], tools=[]
    )
    assert teks == "Halo, ada yang bisa saya bantu?"
    assert panggilan == []


def test_chat_with_tools_executes_tool_call(monkeypatch):
    """Jika model memanggil alat, eksekusi dan kembalikan hasil ke model."""
    panggilan_model = []

    class FakeMessage:
        def __init__(self, content, tool_calls=None):
            self.content = content
            self.tool_calls = tool_calls or []

    class FakeChunk:
        def __init__(self, content, tool_calls=None):
            self.message = FakeMessage(content, tool_calls)

    class FakeClient:
        def chat(self, model, messages, tools, stream):
            panggilan_model.append((model, messages, tools))
            if len(panggilan_model) == 1:
                # Panggilan pertama: model meminta alat
                yield FakeChunk("", tool_calls=[
                    {
                        "function": {
                            "name": "get_customer",
                            "arguments": '{"customer_id": 1}',
                        }
                    }
                ])
            else:
                # Panggilan kedua: model memberikan jawaban akhir
                yield FakeChunk("Pelanggan ditemukan: Budi Santoso")

    monkeypatch.setattr("ollama_client.Client", lambda host: FakeClient())

    dieksekusi = []

    def fake_execute(name, args):
        dieksekusi.append((name, args))
        if name == "get_customer":
            return [{"customer_id": 1, "nama": "Budi Santoso", "kota": "Jakarta"}]
        return []

    monkeypatch.setattr("ollama_client.execute_tool", fake_execute)

    teks, panggilan = chat_with_tools(
        [{"role": "user", "content": "Siapa pelanggan ID 1?"}],
        tools=[{"type": "function", "function": {"name": "get_customer", "description": "...", "parameters": {}}}],
    )
    assert "Budi Santoso" in teks
    assert ("get_customer", {"customer_id": 1}) in dieksekusi
