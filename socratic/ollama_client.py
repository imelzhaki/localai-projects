from ollama import Client

OLLAMA_HOST = "http://localhost:11434"
MODEL = "llama3.2:3b"


def chat_stream(messages, model=MODEL):
    """Stream respons chat dari Ollama.

    Menghasilkan potongan teks saat dihasilkan oleh model.
    `messages` adalah daftar dict {"role": ..., "content": ...}.
    """
    client = Client(host=OLLAMA_HOST)
    for chunk in client.chat(model=model, messages=messages, stream=True):
        yield chunk.message.content
