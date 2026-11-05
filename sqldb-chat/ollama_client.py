"""Klien Ollama untuk generate SQL (ganti chat_with_tools / function calling).

generate_sql(question, schema_docs, fewshot_examples) membangun prompt
bilingual yang berisi: system prompt, skema yang diambil, contoh few-shot,
dan pertanyaan user. Kemudian memanggil llama3.2:3b dengan temperature
rendah (0.1) untuk determinisme dan mengembalikan string SQL mentah.
"""

import logging
import re

from ollama import Client

logger = logging.getLogger(__name__)

OLLAMA_HOST = "http://localhost:11434"
MODEL = "llama3.2:3b"
TEMPERATURE = 0.1


_SYSTEM_PROMPT = """Anda adalah asisten Text-to-SQL yang ahli dalam database SQLite.
Tugas Anda: terjemahkan pertanyaan bahasa alami (Bahasa Indonesia atau Inggris)
menjadi kueri SQL yang valid untuk SQLite.

ATURAN KETAT:
1. Hasilkan HANYA kueri SELECT. JANGAN pernah menghasilkan INSERT, UPDATE, DELETE,
   DROP, atau perintah non-SELECT lainnya.
2. Gunakan HANYA nama tabel dan nama kolom yang ada dalam skema yang disediakan.
   JANGAN menebak atau mengarang nama tabel/kolom.
3. Jika pertanyaan menyebutkan kota, gunakan kolom `kota` pada tabel Customer.
4. Jika pertanyaan menyebutkan kategori produk, gunakan kolom `kategori` pada
   tabel Product dengan nilai: Elektronik, Aksesori, Komputer.
5. Jika pertanyaan menyebutkan status, gunakan nilai: Lunas.
6. Gunakan JOIN yang benar antara tabel yang terkait melalui foreign key.
7. Kembalikan HANYA kueri SQL dalam blok markdown ```sql ... ```, tanpa
   penjelasan atau komentar tambahan.
8. Jawab dalam bahasa yang sama dengan pertanyaan user (Bahasa Indonesia atau
   Inggris), tetapi kueri SQL selalu dalam bahasa Inggris (kata kunci SQL).
9. Untuk fungsi tanggal di SQLite, gunakan `strftime('%m', kolom)` untuk bulan
   dan `strftime('%Y', kolom)` untuk tahun. JANGAN gunakan `EXTRACT()` karena
   tidak didukung oleh SQLite.
10. Jika tidak cukup informasi untuk menghasilkan SQL, kembalikan SELECT sederhana
   dari tabel yang paling relevan.
"""


def _format_schema_docs(schema_docs):
    """Format dokumen skema sebagai teks untuk prompt."""
    if not schema_docs:
        return "Tidak ada skema yang tersedia."
    lines = ["SKema database yang tersedia:"]
    for doc in schema_docs:
        lines.append(f"Tabel: {doc['table']}")
        lines.append(f"Tujuan: {doc['purpose']}")
        lines.append("Kolom:")
        for col in doc["columns"]:
            lines.append(f"  - {col}")
        if doc.get("value_legend"):
            lines.append("Legenda nilai:")
            for col, legend in doc["value_legend"].items():
                lines.append(f"  - {col}: {legend}")
        lines.append("")
    return "\n".join(lines)


def _format_fewshot(fewshot_examples):
    """Format contoh few-shot sebagai teks untuk prompt."""
    if not fewshot_examples:
        return "Tidak ada contoh yang tersedia."
    lines = ["Contoh pertanyaan dan kueri SQL:"]
    for ex in fewshot_examples:
        lines.append(f"Pertanyaan ({ex.get('language', 'id')}): {ex['question']}")
        lines.append(f"SQL: {ex['sql']}")
        lines.append("")
    return "\n".join(lines)


def _extract_sql(text):
    """Ekstrak kueri SQL dari teks respons model."""
    # Coba blok markdown dengan bahasa sql
    match = re.search(r"```sql\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Coba blok markdown tanpa bahasa
    match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        candidate = match.group(1).strip()
        if candidate.upper().startswith("SELECT"):
            return candidate

    # Coba cari pernyataan SELECT mentah
    match = re.search(r"(SELECT\s+.*?)(?:;|$)", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip() + ";"

    return text.strip()


def generate_sql(question, schema_docs, fewshot_examples):
    """Hasilkan SQL dari pertanyaan user menggunakan skema dan contoh few-shot.

    Args:
        question: Pertanyaan bahasa alami dari user.
        schema_docs: Daftar dokumen skema dari retrieval.py.
        fewshot_examples: Daftar contoh Q/SQL dari fewshot.py.

    Returns:
        String kueri SQL yang dihasilkan oleh model.
    """
    schema_text = _format_schema_docs(schema_docs)
    fewshot_text = _format_fewshot(fewshot_examples)

    user_prompt = f"""Skema:
{schema_text}

{fewshot_text}

Pertanyaan: {question}

SQL:"""

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    logger.info("Menghasilkan SQL untuk pertanyaan: %s", question)

    client = Client(host=OLLAMA_HOST)
    response = client.chat(
        model=MODEL,
        messages=messages,
        stream=False,
        options={"temperature": TEMPERATURE},
    )

    msg = response.message
    raw_text = msg.content or ""
    sql = _extract_sql(raw_text)

    logger.info("SQL dihasilkan: %s", sql)
    return sql