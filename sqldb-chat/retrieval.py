import logging
from pathlib import Path

import chromadb

logger = logging.getLogger(__name__)

DB_PATH = Path("data/sqldb-chat.db")
COLLECTION_NAME = "sqldb_schema"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def _get_model():
    """Dapatkan model sentence-transformers (lazy load)."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBED_MODEL)


def build_index(docs, persist_dir="data/chroma_db"):
    """Sematkan dokumen skema ke ChromaDB dengan sentence-transformers."""
    Path(persist_dir).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=persist_dir)
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(name=COLLECTION_NAME)

    model = _get_model()
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


def retrieve_schema_docs(question, top_k=3, persist_dir="data/chroma_db"):
    """Ambil top-K dokumen skema yang relevan dengan pertanyaan."""
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_collection(name=COLLECTION_NAME)

    model = _get_model()
    query_embedding = model.encode([question]).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas"],
    )

    docs = []
    for i in range(len(results["ids"][0])):
        table = results["metadatas"][0][i]["table"]
        docs.append(
            {"table": table, "document": results["documents"][0][i]}
        )

    logger.info(
        "Diambil %d dokumen skema untuk pertanyaan: %s", len(docs), question
    )
    return docs
