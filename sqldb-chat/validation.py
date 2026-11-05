"""Validasi sintaks SQL menggunakan SQLGlot sebelum eksekusi.

Hanya kueri SELECT yang diizinkan. SQLGlot memvalidasi sintaks dan dialek
SQLite, bukan kesalahan semantik terhadap skema (ditangani oleh critic.py).
"""

import logging
import re

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


def check_aggregate_in_where(sql):
    """Deteksi penggunaan fungsi agregat (MAX, MIN, SUM, COUNT, AVG)
    langsung dalam klausa WHERE, yang tidak valid di SQLite.

    Fungsi agregat hanya boleh digunakan dalam SELECT atau HAVING,
    bukan dalam WHERE (harus menggunakan subquery).

    Args:
        sql: String kueri SQL.

    Returns:
        (bool, str|None): (True, pesan_error) jika ditemukan agregat
        dalam WHERE, (False, None) jika tidak ada masalah.
    """
    if not sql:
        return False, None

    # Ambil bagian WHERE clause (dari kata WHERE hingga akhir atau ORDER BY/GROUP BY/HAVING/LIMIT)
    where_match = re.search(
        r"\bWHERE\b(.*?)(?:\bORDER\s+BY\b|\bGROUP\s+BY\b|\bHAVING\b|\bLIMIT\b|$)",
        sql,
        re.IGNORECASE | re.DOTALL,
    )
    if not where_match:
        return False, None

    where_clause = where_match.group(1)

    # Cek fungsi agregat dalam WHERE
    aggregate_pattern = r"\b(MAX|MIN|SUM|COUNT|AVG)\s*\("
    if re.search(aggregate_pattern, where_clause, re.IGNORECASE):
        return True, (
            "Fungsi agregat (MAX/MIN/SUM/COUNT/AVG) tidak boleh digunakan "
            "langsung dalam klausa WHERE. Gunakan subquery atau HAVING."
        )

    return False, None


def normalize_sql_for_sqlite(sql):
    """Konstruk SQL non-SQLite (mis. EXTRACT) ke ekuivalen SQLite.

    SQLite tidak mendukung EXTRACT(). Konversi:
      EXTRACT(MONTH FROM col) -> strftime('%m', col)
      EXTRACT(YEAR FROM col)  -> strftime('%Y', col)
      EXTRACT(DAY FROM col)   -> strftime('%d', col)

    Args:
        sql: String kueri SQL.

    Returns:
        String SQL yang telah dinormalisasi untuk SQLite.
    """
    if not sql:
        return sql

    # EXTRACT(MONTH FROM col) -> strftime('%m', col)
    sql = re.sub(
        r"EXTRACT\s*\(\s*MONTH\s+FROM\s+(\w+(?:\.\w+)?)\s*\)",
        r"strftime('%m', \1)",
        sql,
        flags=re.IGNORECASE,
    )
    # EXTRACT(YEAR FROM col) -> strftime('%Y', col)
    sql = re.sub(
        r"EXTRACT\s*\(\s*YEAR\s+FROM\s+(\w+(?:\.\w+)?)\s*\)",
        r"strftime('%Y', \1)",
        sql,
        flags=re.IGNORECASE,
    )
    # EXTRACT(DAY FROM col) -> strftime('%d', col)
    sql = re.sub(
        r"EXTRACT\s*\(\s*DAY\s+FROM\s+(\w+(?:\.\w+)?)\s*\)",
        r"strftime('%d', \1)",
        sql,
        flags=re.IGNORECASE,
    )

    return sql