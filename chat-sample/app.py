import logging
import streamlit as st

from history import load_history, save_history
from ollama_client import chat_stream
from web_fetcher import fetch_urls_in_text_with_status

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

    # Perintah /reset atau /clear: hapus riwayat percakapan
    if perintah in ("/reset", "/clear"):
        st.session_state.messages = []
        save_history([])
        st.success("Riwayat percakapan telah dihapus. Konteks telah disegarkan.")
        logger.info("Riwayat percakapan dihapus oleh user melalui perintah %s", perintah)
        return

    # Perintah /summary: buat ringkasan percakapan
    if perintah == "/summary":
        if not st.session_state.messages:
            st.info("Belum ada percakapan untuk diringkas.")
            logger.info("User meminta ringkasan tetapi riwayat kosong")
            return

        logger.info("Membuat ringkasan percakapan dengan %d pesan", len(st.session_state.messages))
        pesan_ringkasan = list(st.session_state.messages) + [
            {
                "role": "user",
                "content": (
                    "Buatlah ringkasan ringkas dari percakapan di atas dalam Bahasa Indonesia. "
                    "Sertakan poin-poin penting yang dibahas dan kesimpulan jika ada."
                ),
            }
        ]
        with st.chat_message("assistant"):
            try:
                response = st.write_stream(chat_stream(pesan_ringkasan))
                logger.info("Ringkasan diterima dari LLM, panjang: %d karakter", len(response or ""))
            except Exception as exc:
                logger.error("Gagal membuat ringkasan: %s", exc)
                st.error(f"Gagal membuat ringkasan: {exc}")
                response = ""

        if response:
            assistant_message = build_assistant_message(response)
            st.session_state.messages.append(assistant_message)
            save_history(st.session_state.messages)
            logger.info("Ringkasan disimpan ke riwayat percakapan")
        return

    user_message = build_user_message(prompt)
    st.session_state.messages.append(user_message)
    with st.chat_message("user"):
        st.markdown(prompt)

    # Deteksi URL dalam pesan user dan muat konten halaman sebagai konteks
    hasil = fetch_urls_in_text_with_status(prompt)
    urls = hasil["urls"]
    model_messages = list(st.session_state.messages)
    if urls:
        sukses = [u for u in hasil["per_url"] if u["status"] == "ok"]
        gagal = [u for u in hasil["per_url"] if u["status"] == "error"]

        logger.info("Terdeteksi %d URL dalam pesan user: %s", len(urls), urls)

        if sukses:
            st.info(f"Membuka {len(sukses)} halaman: {', '.join(u['url'] for u in sukses)}")
            konten_tergabung = "\n\n".join(
                f"=== {u['url']} ===\n{u['content']}" for u in sukses
            )
            logger.info(
                "Konten web berhasil diambil dari %d URL, total panjang: %d karakter",
                len(sukses),
                len(konten_tergabung),
            )
            # Sisipkan konten web ke dalam pesan user dengan instruksi paksa
            # agar model menggunakan konten web, bukan data latihnya sendiri
            user_message["content"] = (
                f"{prompt}\n\n"
                "=== KONTEN WEB (Gunakan ini sebagai sumber jawaban) ===\n"
                f"{konten_tergabung}\n"
                "=== AKHIR KONTEN WEB ===\n\n"
                "INSTRUKSI PENTING: Jawab pertanyaan di atas HANYA berdasarkan "
                "konten web yang disediakan di atas. Jangan menggunakan pengetahuan "
                "sendiri atau data latih Anda. Jika jawaban tidak ada dalam konten web, "
                "katakan bahwa informasi tidak tersedia dalam halaman web tersebut."
            )
            # Perbarui pesan user di session state agar konten tersimpan
            st.session_state.messages[-1] = user_message
            logger.debug(
                "Pesan user diperbarui dengan konten web. Pesan yang dikirim ke LLM: %s",
                model_messages,
            )

        if gagal:
            daftar_gagal = "; ".join(
                f"{u['url']} ({u['error']})" for u in gagal
            )
            st.warning(f"Gagal membuka halaman: {daftar_gagal}")
            logger.warning("Gagal membuka %d URL: %s", len(gagal), daftar_gagal)

    logger.info("Mengirim %d pesan ke LLM (model: llama3.2:3b)", len(model_messages))
    with st.chat_message("assistant"):
        try:
            response = st.write_stream(chat_stream(model_messages))
            logger.info("Menerima respons dari LLM, panjang: %d karakter", len(response or ""))
        except Exception as exc:
            logger.error("Gagal terhubung ke Ollama: %s", exc)
            st.error(f"Gagal terhubung ke Ollama: {exc}")
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
    st.set_page_config(page_title="Ollama Chat", page_icon="💬")
    st.title("Ollama Chat (llama3.2:3b)")
    initialize_history()
    display_history()
    handle_user_input()


if __name__ == "__main__":
    main()
