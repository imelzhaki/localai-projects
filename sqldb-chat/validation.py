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


def validate_columns_against_schema(sql, schema_docs):
    """Cek apakah setiap kolom yang direferensikan dengan alias tabel
    (mis. c.kategori) sebenarnya ada pada tabel yang sesuai dalam skema.

    SQLGlot hanya memvalidasi sintaks, bukan semantik skema. Fungsi ini
    menangkap kesalahan seperti WHERE c.kategori = 'Elektronik' ketika
    kolom kategori sebenarnya ada pada tabel Product, bukan Customer.

    Args:
        sql: String kueri SQL.
        schema_docs: Daftar dokumen skema dari retrieval (dengan table,
                     columns, value_legend).

    Returns:
        (bool, str|None): (True, pesan_error) jika ditemukan kolom yang
        tidak sesuai dengan tabel alias-nya, (False, None) jika semua OK.
    """
    if not sql or not schema_docs:
        return False, None

    # Bangun map: alias -> nama tabel (original case), dan nama tabel -> daftar kolom
    alias_to_table = {}
    table_to_columns = {}

    for doc in schema_docs:
        table_name = doc["table"]
        cols = set()
        for col_desc in doc.get("columns", []):
            # Format kolom: "nama_kolom: deskripsi"
            col_name = col_desc.split(":")[0].strip()
            cols.add(col_name.lower())
        table_to_columns[table_name.lower()] = cols

    # Ekstrak alias tabel dari FROM dan JOIN clauses
    # Pola: FROM table alias / JOIN table alias / FROM table AS alias / JOIN table AS alias
    table_alias_pattern = re.compile(
        r"\b(?:FROM|JOIN)\s+(\w+)(?:\s+AS\s+(\w+))?(?:\s+(\w+))?",
        re.IGNORECASE,
    )
    for match in table_alias_pattern.finditer(sql):
        table_name = match.group(1)
        as_alias = match.group(2)
        plain_alias = match.group(3)

        # Tentukan alias yang digunakan
        if as_alias:
            alias_to_table[as_alias.lower()] = table_name
        elif plain_alias and plain_alias.upper() not in (
            "WHERE", "ON", "AND", "OR", "GROUP", "ORDER", "LIMIT", "HAVING",
        ):
            alias_to_table[plain_alias.lower()] = table_name

        # Tabel itu sendiri juga bisa menjadi alias (tanpa AS)
        alias_to_table[table_name.lower()] = table_name

    # Ekstrak semua referensi kolom dengan alias: alias.nama_kolom
    aliased_column_pattern = re.compile(r"(\w+)\.(\w+)", re.IGNORECASE)
    for match in aliased_column_pattern.finditer(sql):
        alias = match.group(1).lower()
        column = match.group(2).lower()

        # Lewati kata kunci SQL yang tidakใช alias tabel
        sql_keywords = {
            "select", "from", "where", "and", "or", "join", "on", "as",
            "group", "by", "order", "having", "limit", "sum", "count",
            "min", "max", "avg", "extract", "strftime", "case", "when",
            "then", "else", "end", "is", "null", "not", "in", "like",
            "between", "asc", "desc", "distinct", "all", "any", "exists",
        }
        if alias in sql_keywords:
            continue

        if alias in alias_to_table:
            table_lower = alias_to_table[alias].lower()
            if table_lower in table_to_columns:
                if column not in table_to_columns[table_lower]:
                    return True, (
                        f"Kolom '{column}' tidak ada pada tabel '{alias_to_table[alias]}' "
                        f"(alias '{alias}'). Kolom yang tersedia pada "
                        f"tabel ini: {', '.join(sorted(table_to_columns[table_lower]))}."
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