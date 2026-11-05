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
        hasil = fn(**arguments)
        # Hasil kosong -> pesan eksplisit agar model tidak halusinasi
        if isinstance(hasil, (list, dict)) and len(hasil) == 0:
            return f"Tidak ada data yang ditemukan untuk alat {name}."
        return hasil
    except TypeError as exc:
        logger.error("Argumen salah untuk alat %s: %s", name, exc)
        return f"Argumen salah untuk alat {name}: {exc}"
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Gagal mengeksekusi alat %s: %s", name, exc)
        return f"Gagal mengeksekusi alat {name}: {exc}"


_SYSTEM_PROMPT = """Anda adalah asisten database kantor. Aturan ketat:

1. Hanya jawab berdasarkan hasil alat (tool) yang dipanggil. JANGAN pernah mengarang, menebak, atau menyimpulkan data dari luar hasil alat.
2. Jika alat mengembalikan data kosong (list kosong atau dict kosong), katakan dengan jelas: "Tidak ada data yang ditemukan."
3. Jika alat mengembalikan error, sampaikan error tersebut kepada user tanpa menebak.
4. Selama menyebutkan angka uang/omset, pastikan angka tersebut berasal langsung dari hasil alat, bukan dari perhitungan Anda sendiri.
5. Data ini dihasilkan oleh AI. Selalu verifikasi terhadap database asli sebelum membuat keputusan bisnis.
6. Jawab dalam Bahasa Indonesia.
7. Jika user meminta "semua penjualan" atau "penjualan bulan terakhir" tanpa menyebutkan kategori, panggil get_sales_data TANPA parameter kategori (biarkan kosong). JANGAN menebak atau mengarang nama kategori. Kategori yang valid: Elektronik, Aksesori, Komputer.
8. Laporan hasil alat secara utuh dan tepat. JANGAN menambahkan komentar, interpretasi, atau informasi tambahan yang tidak ada dalam hasil alat. Sampaikan apa yang dikembalikan alat, tidak lebih dan tidak kurang.
9. Hanya kirim parameter yang didefinisikan dalam skema alat. JANGAN menambahkan parameter yang tidak ada (contoh: jangan kirim "category" pada get_sales_by_product yang hanya menerima nama_produk dan month).
10. JANGAN kirim parameter dengan nilai kosong (string kosong "", "null", "None", atau null). Jika tidak ada nilai yang bermakna, biarkan parameter tersebut tidak dikirim sama sekali.
11. Untuk produk berdasarkan kategori, gunakan list_products(kategori="Elektronik") atau get_product(kategori="Elektronik"). Untuk filter stok atau harga, gunakan list_products(stok_max=10) atau list_products(harga_max=500000). JANGAN kirim parameter "category" pada list_products — gunakan "kategori".
12. JANGAN pernah mengarang atau menebak ID (product_id, customer_id, order_id, supplier_id). Jika tidak tahu ID, biarkan parameter ID kosong dan gunakan parameter nama atau kategori sebagai gantinya."""

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

    # Sisipkan system prompt di awal jika belum ada
    has_system = any(m.get("role") == "system" for m in messages)
    if not has_system:
        messages = [{"role": "system", "content": _SYSTEM_PROMPT}] + list(messages)

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
