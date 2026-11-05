import re
import urllib.request
from html.parser import HTMLParser


_URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)


class _TextExtractor(HTMLParser):
    """Ekstrak teks terbaca dari HTML, abaikan blok script dan style."""

    def __init__(self):
        super().__init__()
        self._parts = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip = True
        elif tag in ("p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6"):
            self._parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = False
        elif tag in ("p", "div", "li"):
            self._parts.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self._parts.append(data)

    def get_text(self):
        text = "".join(self._parts)
        lines = [baris.strip() for baris in text.splitlines()]
        lines = [baris for baris in lines if baris]
        return "\n".join(lines)


def extract_urls(teks):
    """Ekstrak semua URL http/https dari teks.

    Mengembalikan daftar string URL yang ditemukan dalam teks.
    """
    return _URL_PATTERN.findall(teks)


def _html_ke_teks(html):
    """Konversi HTML menjadi teks terbaca."""
    parser = _TextExtractor()
    parser.feed(html)
    return parser.get_text()


def fetch_page_content(url, timeout=10):
    """Muat halaman web dan kembalikan teks yang diekstrak.

    Mengembalikan string kosong jika gagal memuat.
    """
    try:
        permintaan = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            },
        )
        with urllib.request.urlopen(permintaan, timeout=timeout) as respons:
            tipe_konten = respons.headers.get("Content-Type", "").lower()
            if "html" not in tipe_konten:
                return ""
            html = respons.read().decode("utf-8", errors="replace")
            return _html_ke_teks(html)
    except Exception:
        return ""


def fetch_urls_in_text(teks):
    """Temukan URL dalam teks, muat konten masing-masing halaman.

    Mengembalikan tuple (konten_gabungan, daftar_url).
    """
    urls = extract_urls(teks)
    if not urls:
        return "", []
    bagian = []
    for url in urls:
        konten = fetch_page_content(url)
        if konten:
            bagian.append(f"=== Konten dari {url} ===\n{konten}")
    return "\n\n".join(bagian), urls
