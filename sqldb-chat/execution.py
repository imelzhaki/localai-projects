"""Eksekusi kueri SELECT read-only terhadap SQLite.

Koneksi dibuka dalam mode read-only (mode=ro) sehingga setiap operasi
INSERT/UPDATE/DELETE akan ditolak oleh SQLite secara konstruktif.
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path("data/sqldb-chat.db")


def _get_connection():
    """Buka koneksi SQLite dalam mode read-only."""
    uri = f"file:{DB_PATH.resolve()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def execute_select(sql, params=()):
    """Jalankan kueri SELECT parameterisasi dan kembalikan hasil sebagai dict.

    Args:
        sql: String kueri SQL (harus SELECT).
        params: Parameter untuk kueri parameterisasi.

    Returns:
        Dict dengan kunci:
            - ok (bool): True jika eksekusi berhasil.
            - rows (list|None): Daftar baris sebagai dict, atau None jika gagal.
            - error (str|None): Pesan kesalahan jika gagal, None jika berhasil.
    """
    if not sql or not sql.strip():
        return {"ok": False, "rows": None, "error": "SQL kosong."}

    stripped = sql.strip()
    if not stripped.upper().startswith("SELECT"):
        return {
            "ok": False,
            "rows": None,
            "error": "Hanya kueri SELECT yang diizinkan. Non-SELECT diblokir.",
        }

    conn = _get_connection()
    try:
        cur = conn.execute(sql, params)
        rows = [dict(row) for row in cur.fetchall()]
        return {"ok": True, "rows": rows, "error": None}
    except sqlite3.Error as e:
        logger.warning("Eksekusi SQL gagal: %s", e)
        return {"ok": False, "rows": None, "error": str(e)}
    finally:
        conn.close()