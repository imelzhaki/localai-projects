import logging
import re
import urllib.request
from html.parser import HTMLParser

logger = logging.getLogger(__name__)


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
    hasil = fetch_page_content_with_status(url, timeout)
    return hasil["content"]


def fetch_page_content_with_status(url, timeout=10):
    """Muat halaman web dan kembalikan dict dengan status, konten, dan error.

    Mengembalikan:
        {"status": "ok", "content": "<teks>", "error": None}
        atau
        {"status": "error", "content": "", "error": "<pesan error>"}
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
                return {
                    "status": "error",
                    "content": "",
                    "error": f"Bukan HTML (Content-Type: {tipe_konten or 'tidak diketahui'})",
                }
            html = respons.read().decode("utf-8", errors="replace")
            return {
                "status": "ok",
                "content": _html_ke_teks(html),
                "error": None,
            }
    except Exception as exc:
        logger.error("Gagal mengambil %s: %s", url, exc)
        return {
            "status": "error",
            "content": "",
            "error": str(exc),
        }


def fetch_urls_in_text(teks):
    """Temukan URL dalam teks, muat konten masing-masing halaman.

    Mengembalikan tuple (konten_gabungan, daftar_url).
    """
    hasil = fetch_urls_in_text_with_status(teks)
    return hasil["konten"], hasil["urls"]


def fetch_urls_in_text_with_status(teks):
    """Temukan URL dalam teks, muat konten masing-masing halaman dengan status.

    Mengembalikan dict:
        {
            "urls": ["https://..."],
            "konten": "<gabungan teks dari yang berhasil>",
            "per_url": [
                {"url": "...", "status": "ok|error", "content": "...", "error": "..."}
            ]
        }
    """
    urls = extract_urls(teks)
    if not urls:
        return {"urls": [], "konten": "", "per_url": []}

    per_url = []
    bagian = []
    for url in urls:
        hasil = fetch_page_content_with_status(url)
        entri = {
            "url": url,
            "status": hasil["status"],
            "content": hasil["content"],
            "error": hasil["error"],
        }
        per_url.append(entri)
        if hasil["status"] == "ok" and hasil["content"]:
            bagian.append(f"=== Konten dari {url} ===\n{hasil['content']}")

    sukses = [u for u in per_url if u["status"] == "ok"]
    gagal = [u for u in per_url if u["status"] == "error"]

    logger.info(
        "Selesai memproses %d URL: %d sukses, %d gagal",
        len(urls),
        len(sukses),
        len(gagal),
    )
    for entri in per_url:
        if entri["status"] == "ok":
            logger.debug("URL %s berhasil diambil, panjang konten: %d", entri["url"], len(entri["content"]))
        else:
            logger.warning("URL %s gagal diambil: %s", entri["url"], entri["error"])

    return {
        "urls": urls,
        "konten": "\n\n".join(bagian),
        "per_url": per_url,
    }
