import pytest
import sqlite3
import tempfile
import os
from app.core.audit import AuditLogger


@pytest.fixture
def audit_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)


def test_audit_log_write_and_read(audit_db):
    logger = AuditLogger(audit_db)
    logger.log(
        module="ziswaf",
        model="qwen3:4b",
        prompt_version="v1",
        raw_input="H. Ahmad zakat 2.500.000",
        model_output='{"donor_name": "H. Ahmad", "amount_raw": "2.500.000"}',
        validation_result="PASS",
        status="DRAFT",
        confirmed_by=None,
    )
    logs = logger.get_all()
    assert len(logs) == 1
    assert logs[0]["module"] == "ziswaf"
    assert logs[0]["status"] == "DRAFT"
