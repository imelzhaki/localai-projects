import logging
import streamlit as st

from history import load_history, save_history
from ollama_client import chat_stream
from socratic_prompt import build_system_prompt
from geometry_viz import (
    create_triangle_figure,
    create_quadrilateral_figure,
    create_circle_figure,
    create_cube_figure,
    create_sphere_figure,
)
from geometry_parser import parse_geometry_request, default_points_for_shape

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

    # Gambar geometri jika user memintanya (contoh: "gambarkan segitiga sama kaki")
    geometry_req = parse_geometry_request(prompt)
    if geometry_req.action == "gambar" and geometry_req.shape:
        with st.chat_message("assistant"):
            st.caption(f"📐 Gambar {geometry_req.shape}:")
            if geometry_req.shape == "segitiga":
                points = default_points_for_shape("segitiga")
                fig = create_triangle_figure(points)
                st.plotly_chart(fig, use_container_width=True)
            elif geometry_req.shape == "segiempat":
                points = default_points_for_shape("segiempat")
                fig = create_quadrilateral_figure(points)
                st.plotly_chart(fig, use_container_width=True)
            elif geometry_req.shape == "lingkaran":
                fig = create_circle_figure((0, 0), 2)
                st.plotly_chart(fig, use_container_width=True)
            elif geometry_req.shape == "kubus":
                fig = create_cube_figure()
                st.plotly_chart(fig, use_container_width=True)
            elif geometry_req.shape == "bola":
                fig = create_sphere_figure(radius=0.5)
                st.plotly_chart(fig, use_container_width=True)


def render_geometry_visualizer():
    """Render visualisasi geometri 2D dan 3D menggunakan Plotly."""
    st.subheader("📐 Visualisasi Geometri")
    jenis = st.selectbox(
        "Pilih bangun geometri:",
        ["Tidak ada", "Segitiga", "Segiempat", "Lingkaran", "Kubus 3D"],
    )

    if jenis == "Segitiga":
        st.caption("Masukkan 3 titik (x, y) untuk segitiga:")
        col1, col2, col3 = st.columns(3)
        with col1:
            x1 = st.number_input("x1", value=0.0, key="tri_x1")
            y1 = st.number_input("y1", value=0.0, key="tri_y1")
        with col2:
            x2 = st.number_input("x2", value=4.0, key="tri_x2")
            y2 = st.number_input("y2", value=0.0, key="tri_y2")
        with col3:
            x3 = st.number_input("x3", value=2.0, key="tri_x3")
            y3 = st.number_input("y3", value=3.0, key="tri_y3")
        fig = create_triangle_figure([(x1, y1), (x2, y2), (x3, y3)])
        st.plotly_chart(fig, use_container_width=True)

    elif jenis == "Segiempat":
        st.caption("Masukkan 4 titik (x, y) untuk segiempat:")
        col1, col2 = st.columns(2)
        with col1:
            x1 = st.number_input("x1", value=0.0, key="quad_x1")
            y1 = st.number_input("y1", value=0.0, key="quad_y1")
            x2 = st.number_input("x2", value=4.0, key="quad_x2")
            y2 = st.number_input("y2", value=0.0, key="quad_y2")
        with col2:
            x3 = st.number_input("x3", value=4.0, key="quad_x3")
            y3 = st.number_input("y3", value=3.0, key="quad_y3")
            x4 = st.number_input("x4", value=0.0, key="quad_x4")
            y4 = st.number_input("y4", value=3.0, key="quad_y4")
        fig = create_quadrilateral_figure([(x1, y1), (x2, y2), (x3, y3), (x4, y4)])
        st.plotly_chart(fig, use_container_width=True)

    elif jenis == "Lingkaran":
        st.caption("Masukkan pusat dan radius lingkaran:")
        col1, col2, col3 = st.columns(3)
        with col1:
            cx = st.number_input("Pusat x", value=0.0, key="circ_cx")
        with col2:
            cy = st.number_input("Pusat y", value=0.0, key="circ_cy")
        with col3:
            r = st.number_input("Radius", value=2.0, key="circ_r")
        fig = create_circle_figure((cx, cy), r)
        st.plotly_chart(fig, use_container_width=True)

    elif jenis == "Kubus 3D":
        st.caption("Kubus satuan 3D (interaktif — bisa di-putar dan di-zoom):")
        fig = create_cube_figure()
        st.plotly_chart(fig, use_container_width=True)


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

    render_geometry_visualizer()
    handle_user_input()


if __name__ == "__main__":
    main()
