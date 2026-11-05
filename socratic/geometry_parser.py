"""Deteksi dan parsing permintaan gambar geometri dari input user.

Contoh input yang terdeteksi:
- "gambarkan segitiga sama kaki"
- "gambar persegi panjang"
- "lingkaran dengan radius 5"
- "kubus 3D"
"""

from dataclasses import dataclass, field


@dataclass
class GeometryRequest:
    """Hasil parsing permintaan geometri dari user."""

    shape: str | None = None  # "segitiga" | "segiempat" | "lingkaran" | "kubus" | None
    action: str | None = None  # "gambar" | None
    parameters: dict = field(default_factory=dict)


# Kata kunci untuk deteksi aksi gambar
GAMBAR_KEYWORDS = ("gambar", "gambarkan", "gambarkanlah", "draw", "tampilkan")

# Kata kunci untuk deteksi bentuk geometri
SHAPE_KEYWORDS = {
    "segitiga": ("segitiga", "sama kaki", "sama sisi", "siku-siku"),
    "segiempat": ("segiempat", "persegi", "persegi panjang", "belah ketupat"),
    "lingkaran": ("lingkaran", "circle"),
    "kubus": ("kubus", "balok", "3d", "tiga dimensi"),
    "bola": ("bola", "sfera", "spher", "sphere"),
}


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(kw in text for kw in keywords)


def parse_geometry_request(user_input: str) -> GeometryRequest:
    """Parsing input user untuk mendeteksi permintaan gambar geometri.

    Mengembalikan GeometryRequest dengan shape dan action yang terdeteksi,
    atau GeometryRequest kosong jika tidak ada permintaan gambar.
    """
    text = user_input.strip().lower()

    # Deteksi aksi gambar
    if not _contains_any(text, GAMBAR_KEYWORDS):
        return GeometryRequest()

    # Deteksi bentuk geometri
    for shape, keywords in SHAPE_KEYWORDS.items():
        if _contains_any(text, keywords):
            return GeometryRequest(shape=shape, action="gambar")

    # Jika ada kata "gambar" tapi bentuk tidak dikenali
    return GeometryRequest(action="gambar")


def default_points_for_shape(shape: str) -> list[tuple[float, float]] | None:
    """Kembalikan titik default untuk bentuk geometri 2D."""
    if shape == "segitiga":
        # Segitiga sama kaki: alas horizontal, puncak di tengah atas
        return [(0, 0), (4, 0), (2, 3)]
    if shape == "segiempat":
        # Persegi panjang 4x3
        return [(0, 0), (4, 0), (4, 3), (0, 3)]
    return None
