import pytest
from pydantic import ValidationError

from app.modules.ziswaf.schema import ZiswafEntry

VALID_CATEGORIES = {"zakat", "infaq", "shadaqah", "wakaf"}
VALID_PAYMENT_METHODS = {"tunai", "transfer", "qris"}


def test_ziswaf_entry_valid_full():
    entry = ZiswafEntry(
        donor_name="Budi",
        category="zakat",
        amount_raw="2.500.000",
        payment_method="tunai",
        note="pembangunan masjid",
    )
    assert entry.donor_name == "Budi"
    assert entry.category == "zakat"
    assert entry.amount_raw == "2.500.000"
    assert entry.payment_method == "tunai"
    assert entry.note == "pembangunan masjid"


def test_ziswaf_entry_all_none():
    entry = ZiswafEntry()
    assert entry.donor_name is None
    assert entry.category is None
    assert entry.amount_raw is None
    assert entry.payment_method is None
    assert entry.note is None


def test_ziswaf_entry_invalid_category():
    with pytest.raises(ValidationError):
        ZiswafEntry(category="sedekah")


def test_ziswaf_entry_invalid_payment_method():
    with pytest.raises(ValidationError):
        ZiswafEntry(payment_method="kartu kredit")


def test_ziswaf_entry_amount_raw_preserved():
    entry = ZiswafEntry(amount_raw="2,5 jt")
    assert entry.amount_raw == "2,5 jt"


def test_ziswaf_entry_amount_raw_with_dots():
    entry = ZiswafEntry(amount_raw="2.500.000")
    assert entry.amount_raw == "2.500.000"


def test_ziswaf_entry_amount_raw_rb():
    entry = ZiswafEntry(amount_raw="100rb")
    assert entry.amount_raw == "100rb"


def test_ziswaf_entry_category_enum_values():
    for cat in VALID_CATEGORIES:
        entry = ZiswafEntry(category=cat)
        assert entry.category == cat


def test_ziswaf_entry_payment_method_enum_values():
    for pm in VALID_PAYMENT_METHODS:
        entry = ZiswafEntry(payment_method=pm)
        assert entry.payment_method == pm


def test_ziswaf_entry_json_schema():
    schema = ZiswafEntry.schema()
    assert "properties" in schema
    assert "donor_name" in schema["properties"]
    assert "category" in schema["properties"]
    assert "amount_raw" in schema["properties"]