import logging
import threading

import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx

from history import load_history, save_history
from ollama_client import chat_stream
from socratic_prompt import build_system_prompt
from rag import initialize_rag, get_rag_context

logger = logging.getLogger(__name__)

MAX_GUIDING_QUESTIONS = 3

SCHOOL_LEVELS = ["SD", "SMP", "SMA"]
CLASS_LEVELS = ["1", "2", "3"]


def build_user_message(content):
    return {"role": "user", "content": content}


def build_assistant_message(content):
    return {"role": "assistant", "content": content}


def tentukan_stage(question_count):
    """Tentukan tahap bimbingan berdasarkan jumlah pertanyaan penuntang."""
    if question_count >= MAX_GUIDING_QUESTIONS + 1:
        return "reveal"
    if question_count >= MAX_GUIDING_QUESTIONS:
        return "hint"
    return "guiding"


def reset_state():
    """Mengembalikan state ke nilai awal."""
    return [], 0, "guiding"


def initialize_state():
    if "messages" not in st.session_state:
        st.session_state.messages = load_history()
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0
    if "stage" not in st.session_state:
        st.session_state.stage = "guiding"
    if "school_level" not in st.session_state:
        st.session_state.school_level = None
    if "class_level" not in st.session_state:
        st.session_state.class_level = None
    if "subject" not in st.session_state:
        st.session_state.subject = None
    if "rag_initialized" not in st.session_state:
        st.session_state.rag_initialized = False
    if "rag_loading" not in st.session_state:
        st.session_state.rag_loading = False


def _initialize_rag_background(school_level, class_level, subject):
    """Run RAG initialization in a background thread so UI stays responsive."""
    try:
        collection = initialize_rag("documents")
        st.session_state.rag_collection = collection
        st.session_state.rag_initialized = True
    except Exception as exc:
        logger.error("Gagal inisialisasi RAG: %s", exc)
        st.session_state.rag_collection = None
        st.session_state.rag_initialized = False
    finally:
        st.session_state.rag_loading = False
        st.rerun()


def display_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def render_curriculum_selector():
    """Render UI pemilihan tingkat sekolah, kelas, dan mata pelajaran."""
    st.subheader("🏫 Konteks Kurikulum Merdeka")
    st.caption("Pilih tingkat sekolah, kelas, dan mata pelajaran sebelum memulai bimbingan.")

    col1, col2 = st.columns(2)
    with col1:
        school_level = st.selectbox(
            "Tingkat sekolah:",
            SCHOOL_LEVELS,
            index=SCHOOL_LEVELS.index(st.session_state.school_level)
            if st.session_state.school_level in SCHOOL_LEVELS
            else 0,
        )
    with col2:
        class_level = st.selectbox(
            "Kelas:",
            CLASS_LEVELS,
            index=CLASS_LEVELS.index(st.session_state.class_level)
            if st.session_state.class_level in CLASS_LEVELS
            else 0,
        )

    subject = st.text_input(
        "Mata pelajaran (contoh: Bahasa Indonesia, Pendidikan Agama, IPS, Sejarah, dll.):",
        value=st.session_state.subject or "",
        placeholder="Masukkan nama mata pelajaran",
    )

    if st.session_state.rag_loading:
        st.info("Saya sedang memproses ⏳ — mohon tunggu hingga RAG selesai memuat dokumen kurikulum.")
        st.button("Mulai bimbingan", type="primary", disabled=True)

        # Mulai thread background hanya sekali (saat belum ada thread yang hidup)
        if "rag_thread" not in st.session_state or not st.session_state.rag_thread.is_alive():
            thread = threading.Thread(
                target=_initialize_rag_background,
                args=(
                    st.session_state.school_level,
                    st.session_state.class_level,
                    st.session_state.subject,
                ),
                daemon=True,
            )
            add_script_run_ctx(thread)  # Agar st.rerun() dan session_state bekerja dari thread
            st.session_state.rag_thread = thread
            thread.start()

        return False

    if st.button("Mulai bimbingan", type="primary"):
        if not subject.strip():
            st.error("Mata pelajaran harus diisi.")
            return False

        # Simpan data form ke session state sebelum rerun
        st.session_state.school_level = school_level
        st.session_state.class_level = class_level
        st.session_state.subject = subject.strip()
        st.session_state.rag_loading = True
        st.session_state.rag_initialized = False
        st.session_state.rag_collection = None

        st.rerun()
        return False

    return False


def handle_user_input():
    prompt = st.chat_input("Ketik pertanyaan atau konsep sulit...")
    if not prompt:
        return

    perintah = prompt.strip().lower()

    # Perintah /reset: hapus riwayat dan atur ulang counter
    if perintah == "/reset":
        messages, question_count, stage = reset_state()
        st.session_state.messages = messages
        st.session_state.question_count = question_count
        st.session_state.stage = stage
        st.session_state.school_level = None
        st.session_state.class_level = None
        st.session_state.subject = None
        st.session_state.rag_initialized = False
        st.session_state.rag_collection = None
        if "embedding_model" in st.session_state:
            del st.session_state.embedding_model
        save_history([])
        st.success("Riwayat percakapan telah dihapus. Silakan pilih ulang konteks kurikulum.")
        logger.info("Riwayat percakapan dihapus oleh user melalui perintah /reset")
        return

    user_message = build_user_message(prompt)
    st.session_state.messages.append(user_message)
    with st.chat_message("user"):
        st.markdown(prompt)

    # Tampilkan indikator proses saat RAG dan LLM sedang bekerja
    with st.status("Saya sedang memproses ⏳", expanded=False) as status:
        # Ambil konteks RAG berdasarkan pertanyaan user
        rag_context = ""
        if st.session_state.rag_initialized and st.session_state.rag_collection is not None:
            rag_context = get_rag_context(prompt, st.session_state.rag_collection)

        # Susun system prompt sesuai tahap dan konteks kurikulum
        stage = st.session_state.stage
        is_first = st.session_state.question_count == 0
        system_prompt = build_system_prompt(
            stage,
            school_level=st.session_state.school_level,
            class_level=st.session_state.class_level,
            subject=st.session_state.subject,
            rag_context=rag_context,
            is_first=is_first,
        )
        model_messages = [{"role": "system", "content": system_prompt}] + list(
            st.session_state.messages
        )

        logger.info(
            "Mengirim %d pesan ke LLM (stage: %s, question_count: %d, school: %s, class: %s)",
            len(model_messages),
            stage,
            st.session_state.question_count,
            st.session_state.school_level,
            st.session_state.class_level,
        )

        with st.chat_message("assistant"):
            try:
                response = st.write_stream(chat_stream(model_messages))
            except Exception as exc:
                logger.error("Gagal terhubung ke Ollama: %s", exc)
                st.error(f"Gagal terhubung ke Ollama: {exc}")
                response = ""

        status.update(label="Selesai memproses ✅", state="complete")

    if response:
        assistant_message = build_assistant_message(response)
        st.session_state.messages.append(assistant_message)
        # Setiap respons asisten meningkatkan counter
        st.session_state.question_count += 1
        st.session_state.stage = tentukan_stage(st.session_state.question_count)
        save_history(st.session_state.messages)
        logger.info(
            "Respons asisten diterima, question_count sekarang: %d, stage: %s",
            st.session_state.question_count,
            st.session_state.stage,
        )


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    st.set_page_config(page_title="Socratic Tutor", page_icon="🎓")
    st.title("Socratic Tutor (llama3.2:3b)")
    st.caption("Tutor interaktif metode Socratic — hanya bertanya, tidak memberi jawaban langsung.")
    initialize_state()
    display_history()

    # Jika belum ada konteks kurikulum, tampilkan pemilih
    if not st.session_state.rag_initialized:
        render_curriculum_selector()
        return

    # Tampilkan informasi konteks kurikulum saat ini
    st.caption(
        f"Konteks: {st.session_state.school_level} Kelas {st.session_state.class_level} - "
        f"{st.session_state.subject}"
    )

    if st.button("Mulai topik baru"):
        messages, question_count, stage = reset_state()
        st.session_state.messages = messages
        st.session_state.question_count = question_count
        st.session_state.stage = stage
        st.session_state.school_level = None
        st.session_state.class_level = None
        st.session_state.subject = None
        st.session_state.rag_initialized = False
        st.session_state.rag_collection = None
        if "embedding_model" in st.session_state:
            del st.session_state.embedding_model
        save_history([])
        st.success("Topik baru telah dimulai. Silakan pilih ulang konteks kurikulum.")
        st.rerun()

    handle_user_input()


if __name__ == "__main__":
    main()
