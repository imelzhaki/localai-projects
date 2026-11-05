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


def test_fetch_page_content_non_html_still_parsed(monkeypatch):
    """Content-Type tanpa text/html tetap dicoba di-parse (lenient)."""

    class FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        @property
        def headers(self):
            class H:
                def get(self, key, default=""):
                    return "application/xhtml+xml"

            return H()

        def read(self):
            return b"<html><body><p>XHTML konten</p></body></html>"

    monkeypatch.setattr(
        "web_fetcher.urllib.request.urlopen", lambda *a, **k: FakeResp()
    )

    text = fetch_page_content("https://example.com")
    assert "XHTML konten" in text


def test_fetch_page_content_mengirim_header_browser(monkeypatch):
    """Permintaan harus menyertakan header User-Agent dan Accept seperti browser."""

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
            return b"<html><body><p>ok</p></body></html>"

    captured = {}

    def fake_urlopen(req, *a, **k):
        captured["headers"] = req.header_items()
        return FakeResp()

    monkeypatch.setattr(
        "web_fetcher.urllib.request.urlopen", fake_urlopen
    )

    fetch_page_content("https://example.com")

    header_dict = {k.lower(): v for k, v in captured["headers"]}
    assert "user-agent" in header_dict
    assert "Mozilla" in header_dict["user-agent"]
    assert "accept" in header_dict


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


def test_fetch_urls_in_text_some_fail(monkeypatch):
    """Saat satu URL gagal dan satu berhasil, hanya konten berhasil yang dikembalikan."""

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
            return b"<html><body><p>Hanya yang berhasil</p></body></html>"

    panggilan = [0]

    def fake_urlopen(*a, **k):
        panggilan[0] += 1
        if panggilan[0] == 2:
            raise Exception("Gagal terhubung")
        return FakeResp()

    monkeypatch.setattr(
        "web_fetcher.urllib.request.urlopen", fake_urlopen
    )

    content, urls = fetch_urls_in_text(
        "Baca https://berhasil.com dan https://gagal.com"
    )
    assert urls == ["https://berhasil.com", "https://gagal.com"]
    assert "Hanya yang berhasil" in content
    assert "gagal.com" not in content
