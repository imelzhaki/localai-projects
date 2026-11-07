import sqlite3
from datetime import datetime
from typing import List, Dict, Optional


class AuditLogger:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                waktu TEXT NOT NULL,
                module TEXT NOT NULL,
                model TEXT NOT NULL,
                versi_prompt TEXT NOT NULL,
                input_mentah TEXT NOT NULL,
                output_model TEXT NOT NULL,
                hasil_validasi TEXT NOT NULL,
                status TEXT NOT NULL,
                dikonfirmasi_oleh TEXT
            )
        """)
        conn.commit()
        conn.close()

    def log(
        self,
        module: str,
        model: str,
        prompt_version: str,
        raw_input: str,
        model_output: str,
        validation_result: str,
        status: str,
        confirmed_by: Optional[str] = None,
    ):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            INSERT INTO audit_log
            (waktu, module, model, versi_prompt, input_mentah, output_model, hasil_validasi, status, dikonfirmasi_oleh)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(),
                module,
                model,
                prompt_version,
                raw_input,
                model_output,
                validation_result,
                status,
                confirmed_by,
            ),
        )
        conn.commit()
        conn.close()

    def get_all(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM audit_log ORDER BY id DESC").fetchall()
        conn.close()
        return [dict(row) for row in rows]
