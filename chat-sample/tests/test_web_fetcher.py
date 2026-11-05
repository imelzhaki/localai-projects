import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from web_fetcher import extract_urls, fetch_page_content, fetch_urls_in_text


def test_extract_urls_single(monkeypatch):
    urls = extract_urls("Kunjungi https://example.com untuk info")
    assert urls == ["https://example.com"]


def test_extract_urls_multiple(monkeypatch):
    urls = extract_urls("https://a.com dan https://b.com/page")
    assert urls == ["https://a.com", "https://b.com/page"]


def test_extract_urls_none(monkeypatch):
    urls = extract_urls("Halo apa kabar, tidak ada URL di sini")
    assert urls == []


def test_fetch_page_content_returns_text(monkeypatch):
    class FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        @property
        def headers(self):
            class H:
                def get(self, key, default=""):
                    return "text/html"

            return H()

        def read(self):
            return b"<html><body><h1>Judul Halaman</h1><p>Ini isi konten halaman.</p></body></html>"

    monkeypatch.setattr(
        "web_fetcher.urllib.request.urlopen", lambda *a, **k: FakeResp()
    )

    text = fetch_page_content("https://example.com")
    assert "Judul Halaman" in text
    assert "Ini isi konten halaman" in text


def test_fetch_page_content_error_returns_empty(monkeypatch):
    monkeypatch.setattr(
        "web_fetcher.urllib.request.urlopen",
        lambda *a, **k: (_ for _ in ()).throw(Exception("Gagal terhubung")),
    )

    text = fetch_page_content("https://invalid.com")
    assert text == ""


def test_fetch_urls_in_text(monkeypatch):
    class FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        @property
        def headers(self):
            class H:
                def get(self, key, default=""):
                    return "text/html"

            return H()

        def read(self):
            return b"<html><body><p>Konten dari contoh.com</p></body></html>"

    monkeypatch.setattr(
        "web_fetcher.urllib.request.urlopen", lambda *a, **k: FakeResp()
    )

    content, urls = fetch_urls_in_text("Baca https://contoh.com untuk info")
    assert urls == ["https://contoh.com"]
    assert "Konten dari contoh.com" in content
