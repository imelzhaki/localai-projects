import logging
from pathlib import Path

import chromadb

from schema import build_schema_docs

logger = logging.getLogger(__name__)

DB_PATH = Path("data/sqldb-chat.db")
COLLECTION_NAME = "sqldb_schema"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def _get_model():
    """Dapatkan model sentence-transformers (lazy load).

    Mengembalikan None jika sentence-transformers tidak dapat diimpor
    (masalah lingkungan torch/transformers). Pengguna harus menangani
    kasus None di pemanggil.
    """
    try:
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(EMBED_MODEL)
    except Exception as e:
        logger.warning(
            "Tidak dapat memuat sentence-transformers: %s. "
            "Retrieval skema akan dikosongkan.", e
        )
        return None


def build_index(docs, persist_dir="data/chroma_db"):
    """Sematkan dokumen skema ke ChromaDB dengan sentence-transformers.

    Jika sentence-transformers tidak tersedia, indeksi dilewati dan
    fungsi kembali tanpa mengubah apa-apa (degrade gracefully).
    """
    Path(persist_dir).mkdir(parents=True, exist_ok=True)

    model = _get_model()
    if model is None:
        logger.warning(
            "Indeks skema dilewati karena sentence-transformers tidak tersedia."
        )
        return

    client = chromadb.PersistentClient(path=persist_dir)
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(name=COLLECTION_NAME)

    texts = []
    metadatas = []
    ids = []
    for i, doc in enumerate(docs):
        text = (
            f"Tabel: {doc['table']}. Tujuan: {doc['purpose']}. "
            f"Kolom: {'; '.join(doc['columns'])}."
        )
        texts.append(text)
        metadatas.append({"table": doc["table"]})
        ids.append(f"doc_{i}")

    embeddings = model.encode(texts).tolist()
    collection.add(
        documents=texts, metadatas=metadatas, ids=ids, embeddings=embeddings
    )
    logger.info(
        "Diindeks %d dokumen skema ke ChromaDB di %s", len(docs), persist_dir
    )


def retrieve_schema_docs(
    question, top_k=3, persist_dir="data/chroma_db", schema_docs=None
):
    """Ambil top-K dokumen skema yang relevan dengan pertanyaan.

    Jika sentence-transformers atau koleksi ChromaDB tidak tersedia,
    mengembalikan daftar kosong (degrade gracefully).

    Args:
        question: Pertanyaan pengguna.
        top_k: Jumlah dokumen teratas yang diambil.
        persist_dir: Direktori penyimpanan ChromaDB.
        schema_docs: Daftar dokumen skema lengkap (dari build_schema_docs).
                     Jika None, akan dipanggil build_schema_docs() (untuk
                     kompatibilitas mundur, tapi disarankan melewatkan cache
                     dari session state agar tidak introspeksi DB berulang).
    """
    model = _get_model()
    if model is None:
        logger.warning(
            "Retrieval skema dikosongkan karena sentence-transformers tidak tersedia."
        )
        return []

    try:
        client = chromadb.PersistentClient(path=persist_dir)
        collection = client.get_collection(name=COLLECTION_NAME)
    except Exception as e:
        logger.warning(
            "Tidak dapat membuka koleksi ChromaDB: %s. Retrieval dikosongkan.", e
        )
        return []

    query_embedding = model.encode([question]).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas"],
    )

    # Ambil nama tabel dari ChromaDB, lalu lengkapi dengan detail skema penuh
    # (purpose, columns, value_legend) agar critic dapat mengaksesnya.
    retrieved_tables = []
    for i in range(len(results["ids"][0])):
        table = results["metadatas"][0][i]["table"]
        retrieved_tables.append(table)

    # Gunakan schema_docs yang diberikan (cache dari session state) atau
    # bangun baru jika tidak tersedia (fallback untuk kompatibilitas mundur).
    if schema_docs is None:
        schema_docs = build_schema_docs()
    docs_by_table = {doc["table"]: doc for doc in schema_docs}

    docs = []
    for table in retrieved_tables:
        if table in docs_by_table:
            docs.append(docs_by_table[table])

    logger.info(
        "Diambil %d dokumen skema untuk pertanyaan: %s", len(docs), question
    )
    return docs
