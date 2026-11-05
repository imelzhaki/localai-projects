import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import ollama_client


def test_generate_sql_returns_sql_string(monkeypatch):
    """generate_sql mengembalikan string SQL."""

    def fake_chat(messages, model, options, stream):
        class FakeMessage:
            content = "SELECT * FROM Customer WHERE kota = 'Jakarta';"

        class FakeResponse:
            message = FakeMessage()

        return FakeResponse()

    monkeypatch.setattr(ollama_client.Client, "chat", staticmethod(fake_chat))

    question = "Tampilkan pelanggan di Jakarta"
    schema_docs = [
        {
            "table": "Customer",
            "purpose": "Menyimpan data pelanggan.",
            "columns": ["customer_id: ID pelanggan", "nama: Nama pelanggan", "kota: Kota pelanggan"],
            "value_legend": {},
        }
    ]
    fewshot_examples = [
        {
            "question": "Tampilkan semua pelanggan.",
            "sql": "SELECT * FROM Customer;",
            "language": "id",
        }
    ]

    result = ollama_client.generate_sql(question, schema_docs, fewshot_examples)
    assert isinstance(result, str)
    assert "SELECT" in result.upper()


def test_generate_sql_includes_schema_and_fewshot(monkeypatch):
    """generate_sql menyertakan skema dan contoh few-shot dalam prompt."""

    captured_prompt = {}

    def fake_chat(messages, model, options, stream):
        captured_prompt["content"] = messages[-1]["content"]
        class FakeMessage:
            content = "SELECT * FROM Customer;"

        class FakeResponse:
            message = FakeMessage()

        return FakeResponse()

    monkeypatch.setattr(ollama_client.Client, "chat", staticmethod(fake_chat))

    question = "Test"
    schema_docs = [
        {
            "table": "Customer",
            "purpose": "Tabel pelanggan.",
            "columns": ["customer_id: ID", "nama: Nama"],
            "value_legend": {},
        }
    ]
    fewshot_examples = [
        {
            "question": "Contoh pertanyaan.",
            "sql": "SELECT * FROM Customer;",
            "language": "id",
        }
    ]

    ollama_client.generate_sql(question, schema_docs, fewshot_examples)

    prompt = captured_prompt["content"]
    assert "Customer" in prompt
    assert "Contoh pertanyaan" in prompt
    assert "SELECT * FROM Customer;" in prompt
