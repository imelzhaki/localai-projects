import logging
import streamlit as st

from history import load_history, save_history
from ollama_client import chat_with_tools, TOOLS

logger = logging.getLogger(__name__)


def build_user_message(content):
    return {"role": "user", "content": content}


def build_assistant_message(content):
    return {"role": "assistant", "content": content}


def initialize_history():
    if "messages" not in st.session_state:
        st.session_state.messages = load_history()


def display_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input():
    prompt = st.chat_input("Ketik pesan...")
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
            teks, panggilan = chat_with_tools(
                list(st.session_state.messages), tools=TOOLS
            )
            if panggilan:
                for nama, args in panggilan:
                    st.info(f"Memanggil alat: {nama}({args})")
            response = st.write_stream([teks]) if teks else ""
        except Exception as exc:
            logger.error("Gagal memproses pesan: %s", exc)
            st.error(f"Gagal memproses pesan: {exc}")
            response = ""

    if response:
        assistant_message = build_assistant_message(response)
        st.session_state.messages.append(assistant_message)
        save_history(st.session_state.messages)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    st.set_page_config(page_title="DBChat", page_icon="💬")
    st.title("DBChat — Agent Database Kantor (llama3.2:3b)")
    initialize_history()
    display_history()
    handle_user_input()


if __name__ == "__main__":
    main()
