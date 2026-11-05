import logging
from pathlib import Path

import streamlit as st

from database import DB_PATH, init_db
from history import load_history, save_history
from ollama_client import generate_sql
from schema import build_schema_docs
from retrieval import build_index, retrieve_schema_docs
from fewshot import get_fewshot_examples
from validation import (
    validate_sql,
    normalize_sql_for_sqlite,
    check_aggregate_in_where,
    validate_columns_against_schema,
)
from critic import critique_sql
from execution import execute_select

logger = logging.getLogger(__name__)


def build_user_message(content):
    return {"role": "user", "content": content}


def build_assistant_message(content):
    return {"role": "assistant", "content": content}


def initialize_history():
    if "messages" not in st.session_state:
        st.session_state.messages = load_history()


def initialize_schema():
    """Inisialisasi skema dan indeks retrieval (dipanggil dari main).

    Jika build_index gagal (mis. sentence-transformers tidak tersedia),
    aplikasi tetap dapat berjalan dengan retrieval dikosongkan.
    """
    if "schema_docs" not in st.session_state:
        init_db()
        st.session_state.schema_docs = build_schema_docs()
        try:
            build_index(st.session_state.schema_docs, persist_dir="data/chroma_db")
            logger.info("Indeks skema dibangun di startup")
        except Exception as exc:
            logger.warning(
                "Gagal membangun indeks skema: %s. Retrieval akan dikosongkan.", exc
            )
    if "fewshot_examples" not in st.session_state:
        st.session_state.fewshot_examples = get_fewshot_examples()
        logger.info("Contoh few-shot dimuat: %d", len(st.session_state.fewshot_examples))


def _get_schema_docs():
    """Dapatkan dokumen skema dari session state, atau bangun jika belum ada."""
    try:
        if "schema_docs" in st.session_state:
            return st.session_state["schema_docs"]
    except Exception:
        pass
    return build_schema_docs()


def _get_fewshot_examples():
    """Dapatkan contoh few-shot dari session state, atau muat jika belum ada."""
    try:
        if "fewshot_examples" in st.session_state:
            return st.session_state["fewshot_examples"]
    except Exception:
        pass
    return get_fewshot_examples()


def display_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def process_question(question):
    """Jalankan pipeline lengkap: retrieve → generate → validate → critic → execute.

    Returns:
        Dict dengan kunci: question, sql, rows, error, corrected.
    """
    schema_docs = _get_schema_docs()
    fewshot_examples = _get_fewshot_examples()

    # 1. Retrieve skema yang relevan (gunakan cache dari session state
    #    agar tidak introspeksi database berulang kali)
    schema_docs = _get_schema_docs()
    retrieved = retrieve_schema_docs(question, top_k=3, schema_docs=schema_docs)

    # 2. Generate SQL via llama3.2:3b
    sql = generate_sql(question, schema_docs, fewshot_examples)

    # 3. Validasi sintaks dengan SQLGlot
    validation = validate_sql(sql)
    if not validation["valid"]:
        return {
            "question": question,
            "sql": sql,
            "rows": None,
            "error": validation["error"],
            "corrected": False,
        }

    # 4. Critik kedua (semantic review)
    criticism = critique_sql(question, sql, retrieved)
    final_sql = criticism["sql"]

    # Normalisasi konstruk non-SQLite (mis. EXTRACT -> strftime) sebelum eksekusi
    final_sql = normalize_sql_for_sqlite(final_sql)

    # Cek penggunaan fungsi agregat dalam WHERE (tidak valid di SQLite)
    agg_bad, agg_error = check_aggregate_in_where(final_sql)
    if agg_bad:
        return {
            "question": question,
            "sql": final_sql,
            "rows": None,
            "error": agg_error,
            "corrected": criticism["corrected"],
        }

    # Cek apakah kolom dengan alias tabel ada pada tabel yang sesuai
    col_bad, col_error = validate_columns_against_schema(final_sql, schema_docs)
    if col_bad:
        return {
            "question": question,
            "sql": final_sql,
            "rows": None,
            "error": col_error,
            "corrected": criticism["corrected"],
        }

    # 5. Eksekusi read-only
    exec_result = execute_select(final_sql)
    if not exec_result["ok"]:
        return {
            "question": question,
            "sql": final_sql,
            "rows": None,
            "error": exec_result["error"],
            "corrected": criticism["corrected"],
        }

    return {
        "question": question,
        "sql": final_sql,
        "rows": exec_result["rows"],
        "error": None,
        "corrected": criticism["corrected"],
    }


def _display_record_card(record):
    """Tampilkan satu baris data sebagai kartu form (label + nilai)."""
    st.markdown("### Detail Data")
    with st.container(border=True):
        cols = st.columns(2)
        for i, (key, value) in enumerate(record.items()):
            with cols[i % 2]:
                st.markdown(f"**{key}**")
                st.write(value if value is not None else "-")


def handle_user_input():
    prompt = st.chat_input("Ketik pertanyaan (Bahasa Indonesia atau Inggris)...")
    if not prompt:
        return

    perintah = prompt.strip().lower()

    if perintah in ("/reset", "/clear"):
        st.session_state.messages = []
        save_history([])
        st.success("Riwayat percakapan telah dihapus. Konteks telah disegarkan.")
        logger.info("Riwayat percakapan dihapus oleh user melalui perintah %s", perintah)
        return

    user_message = build_user_message(prompt)
    st.session_state.messages.append(user_message)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            result = process_question(prompt)

            if result["error"]:
                st.error(f"Kesalahan: {result['error']}")
                response = f"Kesalahan: {result['error']}"
            elif result["rows"] is None or len(result["rows"]) == 0:
                st.info("Tidak ada data yang ditemukan.")
                response = "Tidak ada data yang ditemukan."
            else:
                with st.expander("Lihat kueri SQL", expanded=False):
                    st.code(result["sql"], language="sql")
                if result["corrected"]:
                    st.info("🔍 SQL telah dikoreksi oleh kritik skema.")

                rows = result["rows"]
                if len(rows) == 1:
                    _display_record_card(rows[0])
                    response = "Ditemukan 1 baris data."
                else:
                    st.dataframe(rows)
                    response = f"Ditemukan {len(rows)} baris data."

        except Exception as exc:
            logger.error("Gagal memproses pesan: %s", exc)
            st.error(f"Gagal memproses pesan: {exc}")
            response = f"Gagal memproses pesan: {exc}"

    if response:
        assistant_message = build_assistant_message(response)
        st.session_state.messages.append(assistant_message)
        save_history(st.session_state.messages)

    st.caption(
        "⚠️ Data dihasilkan oleh AI berdasarkan skema database. "
        "Selalu verifikasi terhadap database asli sebelum membuat keputusan bisnis."
    )


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    st.set_page_config(page_title="SQLDB-Chat", page_icon="🗄️")
    st.title("SQLDB-Chat — Text-to-SQL dengan Pemahaman Skema (llama3.2:3b)")
    initialize_history()
    initialize_schema()
    display_history()
    handle_user_input()


if __name__ == "__main__":
    main()
