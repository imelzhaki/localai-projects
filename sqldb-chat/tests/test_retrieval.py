import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from database import DB_PATH, init_db
import schema
import retrieval


class FakeModel:
    """Model tiruan yang menghasilkan embedding berbasis kata kunci untuk uji."""

    _vocab: dict = {}
    _next_idx: int = 0

    def encode(self, texts):
        import numpy as np

        if isinstance(texts, str):
            texts = [texts]
        # Bangun vocab dari semua teks yang pernah di-encode
        all_words = set()
        for text in texts:
            all_words.update(text.lower().split())
        for word in all_words:
            if word not in self._vocab:
                self._vocab[word] = self._next_idx
                self._next_idx += 1

        dim = len(self._vocab)
        embeddings = []
        for text in texts:
            vec = np.zeros(dim, dtype=np.float32)
            for word in text.lower().split():
                idx = self._vocab.get(word)
                if idx is not None:
                    vec[idx] += 1.0
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            embeddings.append(vec)
        return np.array(embeddings)


def test_retrieve_schema_docs_returns_relevant_table(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("schema.DB_PATH", db_path)
    monkeypatch.setattr("retrieval.DB_PATH", db_path)
    model = FakeModel()
    monkeypatch.setattr("retrieval._get_model", lambda: model)
    init_db()

    docs = schema.build_schema_docs()
    # Pra-bangun vocab dengan semua teks dokumen dan pertanyaan agar dimensi stabil
    all_texts = []
    for d in docs:
        all_texts.append(
            f"Tabel: {d['table']}. Tujuan: {d['purpose']}. "
            f"Kolom: {'; '.join(d['columns'])}."
        )
    all_texts.append("customer di Jakarta")
    model.encode(all_texts)

    index_path = tmp_path / "chroma"
    retrieval.build_index(docs, persist_dir=str(index_path))

    results = retrieval.retrieve_schema_docs(
        "customer di Jakarta", top_k=3, persist_dir=str(index_path)
    )

    assert isinstance(results, list)
    assert len(results) > 0
    for r in results:
        assert "table" in r
        assert "purpose" in r
        assert "columns" in r
        assert "value_legend" in r
        assert r["table"] in {d["table"] for d in docs}


def test_retrieve_schema_docs_returns_top_k(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_path)
    monkeypatch.setattr("schema.DB_PATH", db_path)
    monkeypatch.setattr("retrieval.DB_PATH", db_path)
    monkeypatch.setattr("retrieval._get_model", lambda: FakeModel())
    init_db()

    docs = schema.build_schema_docs()
    index_path = tmp_path / "chroma2"
    retrieval.build_index(docs, persist_dir=str(index_path))

    results = retrieval.retrieve_schema_docs(
        "produk elektronik", top_k=2, persist_dir=str(index_path)
    )

    assert len(results) <= 2
