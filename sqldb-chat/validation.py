"""Validasi sintaks SQL menggunakan SQLGlot sebelum eksekusi.

Hanya kueri SELECT yang diizinkan. SQLGlot memvalidasi sintaks dan dialek
SQLite, bukan kesalahan semantik terhadap skema (ditangani oleh critic.py).
"""

import logging

import sqlglot

logger = logging.getLogger(__name__)


def validate_sql(sql):
    """Validasi kueri SQL dengan SQLGlot (dialek SQLite).

    Args:
        sql: String kueri SQL yang akan divalidasi.

    Returns:
        Dict dengan kunci:
            - valid (bool): True jika SQL valid dan SELECT-only.
            - error (str|None): Pesan kesalahan jika invalid, None jika valid.
            - sql (str): SQL yang divalidasi (sama dengan input).
    """
    if not sql or not sql.strip():
        return {"valid": False, "error": "SQL kosong.", "sql": sql}

    # Cek apakah kueri dimulai dengan SELECT (case-insensitive)
    stripped = sql.strip()
    if not stripped.upper().startswith("SELECT"):
        return {
            "valid": False,
            "error": "Hanya kueri SELECT yang diizinkan. Non-SELECT diblokir.",
            "sql": sql,
        }

    try:
        parsed = sqlglot.parse_one(sql, dialect="sqlite")
        if parsed is None:
            return {
                "valid": False,
                "error": "Gagal memparsing SQL: hasil parsing kosong.",
                "sql": sql,
            }
    except Exception as e:
        logger.warning("SQLGlot validation gagal: %s", e)
        return {
            "valid": False,
            "error": f"Kesalahan sintaks SQL: {e}",
            "sql": sql,
        }

    return {"valid": True, "error": None, "sql": sql}