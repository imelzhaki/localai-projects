import logging
import streamlit as st

from history import load_history, save_history
from ollama_client import chat_stream
from socratic_prompt import build_system_prompt

logger = logging.getLogger(__name__)

MAX_GUIDING_QUESTIONS = 3


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


def display_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


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
        save_history([])
        st.success("Riwayat percakapan telah dihapus. Topik baru telah dimulai.")
        logger.info("Riwayat percakapan dihapus oleh user melalui perintah /reset")
        return

    user_message = build_user_message(prompt)
    st.session_state.messages.append(user_message)
    with st.chat_message("user"):
        st.markdown(prompt)

    # Susun system prompt sesuai tahap saat ini
    stage = st.session_state.stage
    system_prompt = build_system_prompt(stage)
    model_messages = [{"role": "system", "content": system_prompt}] + list(
        st.session_state.messages
    )

    logger.info(
        "Mengirim %d pesan ke LLM (stage: %s, question_count: %d)",
        len(model_messages),
        stage,
        st.session_state.question_count,
    )

    with st.chat_message("assistant"):
        try:
            response = st.write_stream(chat_stream(model_messages))
        except Exception as exc:
            logger.error("Gagal terhubung ke Ollama: %s", exc)
            st.error(f"Gagal terhubung ke Ollama: {exc}")
            response = ""

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

    if st.button("Mulai topik baru"):
        messages, question_count, stage = reset_state()
        st.session_state.messages = messages
        st.session_state.question_count = question_count
        st.session_state.stage = stage
        save_history([])
        st.success("Topik baru telah dimulai. Silakan ajukan pertanyaan baru.")

    handle_user_input()


if __name__ == "__main__":
    main()
