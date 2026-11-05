import json
import logging
from ollama import Client
from tools import TOOLS, execute_tool_map

logger = logging.getLogger(__name__)

OLLAMA_HOST = "http://localhost:11434"
MODEL = "llama3.2:3b"


def execute_tool(name, arguments):
    """Eksekusi alat berdasarkan nama dan argumen. Kembalikan hasil (list/dict/str)."""
    fn = execute_tool_map.get(name)
    if fn is None:
        return f"Alat '{name}' tidak tersedia."
    try:
        return fn(**arguments)
    except TypeError as exc:
        logger.error("Argumen salah untuk alat %s: %s", name, exc)
        return f"Argumen salah untuk alat {name}: {exc}"
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Gagal mengeksekusi alat %s: %s", name, exc)
        return f"Gagal mengeksekusi alat {name}: {exc}"


def chat_with_tools(messages, tools=TOOLS, model=MODEL):
    """Kirim pesan ke Ollama dengan dukungan tool calling.

    Menangani ronde pemanggilan alat: saat model meminta alat,
    eksekusi alat, kirim hasilnya kembali ke model, dan terima
    jawaban akhir.

    Returns:
        (teks_jawaban, daftar_panggilan_alat)
    """
    client = Client(host=OLLAMA_HOST)
    daftar_panggilan = []

    while True:
        response = client.chat(
            model=model,
            messages=messages,
            tools=tools,
            stream=False,
        )
        # Ollama client dengan stream=False mengembalikan response object langsung.
        # Beberapa test mock menggunakan generator; tangani kedua kasus.
        if hasattr(response, "__iter__") and not hasattr(response, "message"):
            chunks = list(response)
            response = chunks[-1] if chunks else None
        msg = response.message

        if not msg.tool_calls:
            return msg.content or "", daftar_panggilan

        # Model memanggil alat — eksekusi setiap alat yang diminta
        for tool_call in msg.tool_calls:
            if hasattr(tool_call, "function"):
                name = tool_call.function.name
                arguments_raw = tool_call.function.arguments or "{}"
                tool_call_id = getattr(tool_call, "id", None)
            else:
                name = tool_call["function"]["name"]
                arguments_raw = tool_call["function"].get("arguments", "{}")
                tool_call_id = tool_call.get("id")
            if isinstance(arguments_raw, dict):
                arguments = arguments_raw
            else:
                try:
                    arguments = json.loads(arguments_raw)
                except (json.JSONDecodeError, TypeError):
                    arguments = {}
            daftar_panggilan.append((name, arguments))
            logger.info("Model memanggil alat %s dengan argumen %s", name, arguments)

            hasil = execute_tool(name, arguments)

            messages.append(msg)
            messages.append({
                "role": "tool",
                "content": str(hasil),
                "tool_call_id": tool_call_id,
            })
        # Loop lagi untuk mendapatkan jawaban akhir dari model
