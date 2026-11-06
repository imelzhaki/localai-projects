"""Modul RAG (Retrieval-Augmented Generation) untuk konteks kurikulum.

Memuat dokumen kurikulum (CP, ATP, Modul ajar) dari direktori documents/,
membuat vector store dengan ChromaDB, dan mengambil konteks relevan
berdasarkan pertanyaan siswa.
"""

import logging
import re
from pathlib import Path
from typing import Optional

import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import streamlit as st

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
N_RESULTS = 3


def _sanitize_text(text: str) -> str:
    """Hapus karakter surrogate dan Unicode tidak valid yang menyebabkan tokenizer error."""
    # Hapus lone surrogates (U+D800-U+DFFF) yang tidak valid dalam UTF-8
    text = re.sub(r'[\ud800-\udfff]', '', text)
    # Ganti karakter kontrol lain (kecuali newline/tab yang valid)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    return text


def _load_text_file(path: Path) -> str:
    """Baca isi berkas teks."""
    return path.read_text(encoding="utf-8")


def _load_pdf_file(path: Path) -> str:
    """Baca isi berkas PDF."""
    reader = PdfReader(str(path))
    texts = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    return "\n".join(texts)


def load_documents(documents_dir: str = "documents") -> list[dict]:
    """Muat semua dokumen (.txt, .pdf) dari direktori.

    Mengembalikan list dict dengan kunci: source, content.
    Mengembalikan list kosong jika direktori tidak ada atau kosong.
    """
    docs = []
    dir_path = Path(documents_dir)
    if not dir_path.exists():
        return docs

    for path in sorted(dir_path.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in (".txt", ".md"):
            content = _load_text_file(path)
        elif suffix == ".pdf":
            content = _load_pdf_file(path)
        else:
            continue
        if content.strip():
            docs.append({"source": str(path), "content": content})
            logger.info("Muat dokumen: %s (%d karakter)", path, len(content))
    logger.info("Total dokumen dimuat dari %s: %d", documents_dir, len(docs))
    return docs


def split_text(text: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Bagi teks menjadi potongan-potongan (chunks) dengan overlap."""
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append(text[start:end])
        if end >= text_len:
            break
        start = end - chunk_overlap
        if start < 0:
            start = 0
    return chunks


def get_embedding_model() -> SentenceTransformer:
    """Dapatkan model embedding (muat sekali, gunakan ulang)."""
    if "embedding_model" not in st.session_state:
        st.session_state.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return st.session_state.embedding_model


def create_vector_store(chunks: list[str], metadatas: list[dict], collection_name: str = "curriculum"):
    """Buat vector store ChromaDB dari chunks teks."""
    # Filter chunk yang tidak valid (None, bukan string, atau kosong)
    valid_pairs = [
        (c, m) for c, m in zip(chunks, metadatas)
        if c is not None and isinstance(c, str) and c.strip()
    ]
    if not valid_pairs:
        logger.warning("Tidak ada chunk valid untuk dibuat vector store")
        client = chromadb.Client()
        return client.create_collection(name=collection_name)

    chunks, metadatas = zip(*valid_pairs)
    chunks = list(chunks)
    metadatas = list(metadatas)

    # Sanitasi chunk untuk menghindari tokenizer error pada karakter surrogate
    chunks = [_sanitize_text(c) for c in chunks]
    # Buang chunk yang menjadi kosong setelah sanitasi
    valid_pairs = [(c, m) for c, m in zip(chunks, metadatas) if c.strip()]
    if not valid_pairs:
        logger.warning("Tidak ada chunk valid setelah sanitasi")
        client = chromadb.Client()
        return client.create_collection(name=collection_name)
    chunks, metadatas = zip(*valid_pairs)
    chunks = list(chunks)
    metadatas = list(metadatas)

    client = chromadb.Client()
    collection = client.create_collection(name=collection_name)

    model = get_embedding_model()
    embeddings = model.encode(chunks).tolist()

    collection.add(
        documents=chunks,
        metadatas=metadatas,
        embeddings=embeddings,
        ids=[f"chunk_{i}" for i in range(len(chunks))],
    )
    return collection


def retrieve_context(query: str, collection, n_results: int = N_RESULTS) -> list[str]:
    """Ambil konteks relevan dari vector store berdasarkan query."""
    model = get_embedding_model()
    query = _sanitize_text(query)
    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
    )

    documents = results.get("documents", [[]])
    if not documents or not documents[0]:
        return []
    return documents[0]


def initialize_rag(documents_dir: str = "documents") -> Optional[object]:
    """Inisialisasi vector store dan simpan di session state.

    Mengembalikan collection jika berhasil, None jika tidak ada dokumen.
    """
    if "rag_collection" in st.session_state:
        return st.session_state.rag_collection

    docs = load_documents(documents_dir)
    if not docs:
        logger.warning("Tidak ada dokumen kurikulum ditemukan di %s", documents_dir)
        return None

    chunks = []
    metadatas = []
    for doc in docs:
        doc_chunks = split_text(doc["content"])
        for chunk in doc_chunks:
            if chunk and chunk.strip():  # Lewati chunk kosong atau hanya whitespace
                chunks.append(chunk)
                metadatas.append({"source": doc["source"]})

    if not chunks:
        logger.warning("Tidak ada chunk yang dihasilkan dari dokumen di %s", documents_dir)
        return None

    logger.info("Membuat vector store dari %d chunk (dari %d dokumen)", len(chunks), len(docs))
    collection = create_vector_store(chunks, metadatas)
    st.session_state.rag_collection = collection
    logger.info("RAG diinisialisasi dengan %d chunk dari %d dokumen", len(chunks), len(docs))
    return collection


def get_rag_context(query: str, collection) -> str:
    """Dapatkan konteks RAG sebagai string untuk disisipkan ke system prompt."""
    if collection is None:
        return ""

    relevant = retrieve_context(query, collection)
    if not relevant:
        return ""

    return "\n\n".join(relevant)
