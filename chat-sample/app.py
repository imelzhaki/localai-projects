import streamlit as st

from history import load_history, save_history
from ollama_client import chat_stream


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

    user_message = build_user_message(prompt)
    st.session_state.messages.append(user_message)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = st.write_stream(chat_stream(st.session_state.messages))
        except Exception as exc:
            st.error(f"Gagal terhubung ke Ollama: {exc}")
            response = ""

    if response:
        assistant_message = build_assistant_message(response)
        st.session_state.messages.append(assistant_message)
        save_history(st.session_state.messages)


def main():
    st.set_page_config(page_title="Ollama Chat", page_icon="💬")
    st.title("Ollama Chat (llama3.2:3b)")
    initialize_history()
    display_history()
    handle_user_input()


if __name__ == "__main__":
    main()
