import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np

import rag


class TestLoadDocuments:
    def test_load_documents_direktori_tidak_ada(self):
        docs = rag.load_documents("direktori_tidak_ada_xyz")
        assert docs == []

    def test_load_documents_direktori_kosong(self, tmp_path):
        docs = rag.load_documents(str(tmp_path))
        assert docs == []

    def test_load_documents_muat_file_txt(self, tmp_path):
        (tmp_path / "materi.txt").write_text("Ini adalah materi contoh.", encoding="utf-8")
        docs = rag.load_documents(str(tmp_path))
        assert len(docs) == 1
        assert docs[0]["content"] == "Ini adalah materi contoh."
        assert "materi.txt" in docs[0]["source"]

    def test_load_documents_muat_file_md(self, tmp_path):
        (tmp_path / "materi.md").write_text("# Materi Contoh\n\nIni adalah markdown.", encoding="utf-8")
        docs = rag.load_documents(str(tmp_path))
        assert len(docs) == 1
        assert docs[0]["content"] == "# Materi Contoh\n\nIni adalah markdown."
        assert "materi.md" in docs[0]["source"]

    def test_load_documents_muat_file_pdf(self, tmp_path, monkeypatch):
        # Mock PdfReader agar mengembalikan halaman dengan teks
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Ini adalah isi PDF untuk pengujian."
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        monkeypatch.setattr(rag, "PdfReader", lambda path: mock_reader)

        pdf_path = tmp_path / "materi.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 fake")

        docs = rag.load_documents(str(tmp_path))
        assert len(docs) == 1
        assert "Ini adalah isi PDF" in docs[0]["content"]
        assert docs[0]["source"].endswith("materi.pdf")

    def test_load_documents_abaikan_file_lain(self, tmp_path):
        (tmp_path / "materi.txt").write_text("konten teks", encoding="utf-8")
        (tmp_path / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        docs = rag.load_documents(str(tmp_path))
        assert len(docs) == 1
        assert docs[0]["content"] == "konten teks"

    def test_load_documents_muat_file_docx(self, tmp_path, monkeypatch):
        # Mock DocxDocument agar mengembalikan paragraf dan tabel
        mock_para1 = MagicMock()
        mock_para1.text = "Ini adalah paragraf pertama dari dokumen Word."
        mock_para2 = MagicMock()
        mock_para2.text = "Ini adalah paragraf kedua."

        mock_cell1 = MagicMock()
        mock_cell1.text = "Kolom 1"
        mock_cell2 = MagicMock()
        mock_cell2.text = "Kolom 2"
        mock_row = MagicMock()
        mock_row.cells = [mock_cell1, mock_cell2]
        mock_table = MagicMock()
        mock_table.rows = [mock_row]

        mock_doc = MagicMock()
        mock_doc.paragraphs = [mock_para1, mock_para2]
        mock_doc.tables = [mock_table]
        monkeypatch.setattr(rag, "DocxDocument", lambda path: mock_doc)

        docx_path = tmp_path / "materi.docx"
        docx_path.write_bytes(b"fake docx")

        docs = rag.load_documents(str(tmp_path))
        assert len(docs) == 1
        assert "Ini adalah paragraf pertama" in docs[0]["content"]
        assert "Ini adalah paragraf kedua" in docs[0]["content"]
        assert "Kolom 1 | Kolom 2" in docs[0]["content"]
        assert docs[0]["source"].endswith("materi.docx")


class TestSanitizeText:
    def test_sanitize_text_hapus_surrogate(self):
        # Lone surrogate karakter yang menyebabkan tokenizer error
        text = "Halo \udca1\ud83d dunia"
        result = rag._sanitize_text(text)
        assert "\udca1" not in result
        assert "\ud83d" not in result
        assert result == "Halo  dunia"

    def test_sanitize_text_tidak_ubah_teks_normal(self):
        text = "Ini teks biasa tanpa karakter aneh."
        result = rag._sanitize_text(text)
        assert result == text

    def test_sanitize_text_hapus_kontrol(self):
        text = "Teks\x00dengan\x07karakter\x1fkontrol"
        result = rag._sanitize_text(text)
        assert "\x00" not in result
        assert "\x07" not in result
        assert "\x1f" not in result
        assert result == "Teksdengankarakterkontrol"

    def test_sanitize_text_pertahankan_newline_tab(self):
        text = "Baris 1\nBaris 2\tterindentasi"
        result = rag._sanitize_text(text)
        assert result == text


class TestSplitText:
    def test_split_text_pendek(self):
        text = "Ini teks pendek."
        chunks = rag.split_text(text, chunk_size=500, chunk_overlap=50)
        assert chunks == ["Ini teks pendek."]

    def test_split_text_panjang(self):
        text = "A" * 1000
        chunks = rag.split_text(text, chunk_size=500, chunk_overlap=50)
        assert len(chunks) == 3
        assert len(chunks[0]) == 500
        assert len(chunks[1]) == 500
        assert len(chunks[2]) == 100

    def test_split_text_overlap(self):
        text = "A" * 600
        chunks = rag.split_text(text, chunk_size=500, chunk_overlap=100)
        assert len(chunks) == 2
        assert len(chunks[0]) == 500
        assert len(chunks[1]) == 200


def _mock_st_session_state(monkeypatch):
    """Buat mock st.session_state yang mendukung akses atribut dan item."""
    mock_st = MagicMock()
    mock_st.session_state = MagicMock()
    monkeypatch.setattr(rag, "st", mock_st)
    return mock_st


def _mock_encode(return_value):
    """Buat mock model.encode yang mengembalikan numpy array dengan tolist()."""
    mock_model = MagicMock()
    mock_model.encode.return_value = np.array(return_value)
    return mock_model


class TestGetEmbeddingModel:
    def test_get_embedding_model_simpan_di_session_state(self, monkeypatch):
        _mock_st_session_state(monkeypatch)

        with patch.object(rag.SentenceTransformer, "__init__", return_value=None):
            model = rag.get_embedding_model()
            assert rag.st.session_state.embedding_model is not None


class TestCreateVectorStore:
    def test_create_vector_store(self, monkeypatch):
        mock_collection = MagicMock()
        mock_client = MagicMock()
        mock_client.create_collection.return_value = mock_collection

        monkeypatch.setattr(rag.chromadb, "Client", lambda: mock_client)
        _mock_st_session_state(monkeypatch)

        mock_model = _mock_encode([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        monkeypatch.setattr(rag, "get_embedding_model", lambda: mock_model)

        collection = rag.create_vector_store(
            ["chunk 1", "chunk 2"],
            [{"source": "a.txt"}, {"source": "b.txt"}],
        )
        assert collection == mock_collection
        mock_collection.add.assert_called_once()


class TestRetrieveContext:
    def test_retrieve_context_hasil_kosong(self, monkeypatch):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {"documents": [[]]}

        _mock_st_session_state(monkeypatch)

        mock_model = _mock_encode([[0.1, 0.2]])
        monkeypatch.setattr(rag, "get_embedding_model", lambda: mock_model)

        result = rag.retrieve_context("query", mock_collection)
        assert result == []

    def test_retrieve_context_hasil_ada(self, monkeypatch):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "documents": [["konteks 1", "konteks 2"]]
        }

        _mock_st_session_state(monkeypatch)

        mock_model = _mock_encode([[0.1, 0.2]])
        monkeypatch.setattr(rag, "get_embedding_model", lambda: mock_model)

        result = rag.retrieve_context("query", mock_collection)
        assert result == ["konteks 1", "konteks 2"]


class TestInitializeRAG:
    def test_initialize_rag_tidak_ada_dokumen(self, monkeypatch, tmp_path):
        _mock_st_session_state(monkeypatch)

        collection = rag.initialize_rag(str(tmp_path / "kosong"))
        assert collection is None

    def test_initialize_rag_dengan_dokumen(self, monkeypatch, tmp_path):
        (tmp_path / "materi.txt").write_text("Ini adalah materi contoh untuk pengujian RAG.", encoding="utf-8")

        _mock_st_session_state(monkeypatch)

        mock_collection = MagicMock()
        mock_client = MagicMock()
        mock_client.create_collection.return_value = mock_collection
        monkeypatch.setattr(rag.chromadb, "Client", lambda: mock_client)

        mock_model = _mock_encode([[0.1, 0.2, 0.3]])
        monkeypatch.setattr(rag, "get_embedding_model", lambda: mock_model)

        collection = rag.initialize_rag(str(tmp_path))
        assert collection == mock_collection
        assert rag.st.session_state.rag_collection is not None


class TestGetRAGContext:
    def test_get_rag_context_collection_none(self):
        result = rag.get_rag_context("query", None)
        assert result == ""

    def test_get_rag_context_tidak_ada_hasil(self, monkeypatch):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {"documents": [[]]}

        _mock_st_session_state(monkeypatch)

        mock_model = _mock_encode([[0.1, 0.2]])
        monkeypatch.setattr(rag, "get_embedding_model", lambda: mock_model)

        result = rag.get_rag_context("query", mock_collection)
        assert result == ""

    def test_get_rag_context_dengan_hasil(self, monkeypatch):
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "documents": [["konteks relevan dari kurikulum"]]
        }

        _mock_st_session_state(monkeypatch)

        mock_model = _mock_encode([[0.1, 0.2]])
        monkeypatch.setattr(rag, "get_embedding_model", lambda: mock_model)

        result = rag.get_rag_context("query", mock_collection)
        assert "konteks relevan dari kurikulum" in result