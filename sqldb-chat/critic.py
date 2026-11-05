"""Critik kedua llama3.2:3b: tinjau SQL terhadap skema yang diambil.

Critik memeriksa nama tabel, nama kolom, dan join terhadap skema yang
diambil dari retrieval. Mengembalikan SQL yang dikoreksi atau mengonfirmasi
SQL asli jika sudah benar.
"""

import logging
import re

from ollama import Client

logger = logging.getLogger(__name__)

OLLAMA_HOST = "http://localhost:11434"
MODEL = "llama3.2:3b"


def _call_llm(prompt):
    """Panggil Ollama untuk menghasilkan teks respons dari prompt."""
    client = Client(host=OLLAMA_HOST)
    response = client.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=False,
    )
    msg = response.message
    return msg.content or ""


def _extract_sql(text):
    """Ekstrak kueri SQL dari teks respons model.

    Menangani:
    - SQL dalam blok markdown ```sql ... ```
    - SQL dalam blok markdown ``` ... ```
    - SQL mentah tanpa pembungkus
    """
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


def _build_critic_prompt(question, sql, schema_docs):
    """Bangun prompt untuk kritik SQL terhadap skema."""
    schema_text = ""
    for doc in schema_docs:
        schema_text += f"Tabel: {doc['table']}\n"
        schema_text += f"Tujuan: {doc['purpose']}\n"
        schema_text += "Kolom:\n"
        for col in doc["columns"]:
            schema_text += f"  - {col}\n"
        if doc.get("value_legend"):
            schema_text += "Legenda nilai:\n"
            for col, legend in doc["value_legend"].items():
                schema_text += f"  - {col}: {legend}\n"
        schema_text += "\n"

    prompt = f"""Anda adalah kritik SQL untuk database SQLite. Periksa kueri SQL berikut
terhadap skema yang diberikan dan koreksi jika ada kesalahan nama tabel,
nama kolom, atau join.

Pertanyaan pengguna: {question}

Skema yang relevan:
{schema_text}

Kueri SQL yang akan dikritik:
{sql}

Tugas:
1. Periksa apakah semua nama tabel dalam SQL ada dalam skema.
2. Periksa apakah semua nama kolom dalam SQL ada dalam skema tabel yang sesuai.
3. Periksa apakah join antara tabel benar (foreign key yang cocok).
4. Jika ada kesalahan, perbaiki dan kembalikan SQL yang dikoreksi.
5. Jika SQL sudah benar, kembalikan SQL asli tanpa perubahan.

Kembalikan HANYA kueri SQL dalam blok markdown ```sql ... ```, tanpa
penjelasan tambahan.
"""
    return prompt


def critique_sql(question, sql, schema_docs):
    """Kritik SQL terhadap skema dan kembalikan hasil koreksi.

    Args:
        question: Pertanyaan asli pengguna.
        sql: Kueri SQL yang akan dikritik.
        schema_docs: Daftar dokumen skema dari retrieval.

    Returns:
        Dict dengan kunci:
            - corrected (bool): True jika SQL dikoreksi, False jika asli.
            - sql (str): SQL akhir (dikoreksi atau asli).
            - error (str|None): Pesan kesalahan jika ada.
    """
    if not sql or not sql.strip():
        return {
            "corrected": False,
            "sql": sql,
            "error": "SQL kosong, tidak ada yang dapat dikritik.",
        }

    prompt = _build_critic_prompt(question, sql, schema_docs)

    try:
        response = _call_llm(prompt)
    except Exception as e:
        logger.warning("Panggilan LLM untuk kritik gagal: %s", e)
        return {
            "corrected": False,
            "sql": sql,
            "error": f"Gagal memanggil LLM untuk kritik: {e}",
        }

    corrected_sql = _extract_sql(response)

    if not corrected_sql:
        return {
            "corrected": False,
            "sql": sql,
            "error": "Tidak dapat mengekstrak SQL dari respons kritik.",
        }

    # Normalisasi untuk perbandingan
    original_normalized = " ".join(sql.strip().split())
    corrected_normalized = " ".join(corrected_sql.strip().split())

    corrected = original_normalized != corrected_normalized

    return {
        "corrected": corrected,
        "sql": corrected_sql,
        "error": None,
    }