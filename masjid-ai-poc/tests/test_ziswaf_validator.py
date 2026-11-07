import pytest

from app.modules.ziswaf.validator import (
    validate_amount_raw_substring,
    validate_category_enum,
    validate_payment_method_enum,
    validate_no_duplicate_entries,
    validate_nominal_match,
    ZiswafValidationResult,
)


def test_validate_amount_raw_substring_true():
    result = validate_amount_raw_substring("2.500.000", "Saya infaq 2.500.000 rupiah")
    assert result.is_valid is True
    assert result.error is None


def test_validate_amount_raw_substring_false():
    result = validate_amount_raw_substring("2.500.000", "Saya infaq 1.000.000 rupiah")
    assert result.is_valid is False
    assert "amount_raw" in result.error.lower()


def test_validate_amount_raw_substring_none_input():
    result = validate_amount_raw_substring("2.500.000", "")
    assert result.is_valid is False


def test_validate_amount_raw_substring_none_amount():
    result = validate_amount_raw_substring(None, "Saya infaq 2.500.000 rupiah")
    assert result.is_valid is True  # None amount_raw is allowed (not provided)


def test_validate_category_enum_valid():
    for cat in ["zakat", "infaq", "shadaqah", "wakaf"]:
        result = validate_category_enum(cat)
        assert result.is_valid is True


def test_validate_category_enum_invalid():
    result = validate_category_enum("sedekah")
    assert result.is_valid is False
    assert "kategori" in result.error.lower()


def test_validate_category_enum_none():
    result = validate_category_enum(None)
    assert result.is_valid is True  # None is allowed


def test_validate_payment_method_enum_valid():
    for pm in ["tunai", "transfer", "qris"]:
        result = validate_payment_method_enum(pm)
        assert result.is_valid is True


def test_validate_payment_method_enum_invalid():
    result = validate_payment_method_enum("kartu kredit")
    assert result.is_valid is False
    assert "pembayaran" in result.error.lower()


def test_validate_payment_method_enum_none():
    result = validate_payment_method_enum(None)
    assert result.is_valid is True


def test_validate_no_duplicate_entries_no_dupes():
    entries = [
        {"donor_name": "Budi", "amount_raw": "2.500.000"},
        {"donor_name": "Siti", "amount_raw": "1.000.000"},
    ]
    result = validate_no_duplicate_entries(entries)
    assert result.is_valid is True


def test_validate_no_duplicate_entries_has_dupes():
    entries = [
        {"donor_name": "Budi", "amount_raw": "2.500.000"},
        {"donor_name": "Budi", "amount_raw": "2.500.000"},
    ]
    result = validate_no_duplicate_entries(entries)
    assert result.is_valid is False
    assert "duplikat" in result.error.lower() or "duplicate" in result.error.lower()


def test_validate_nominal_match_true():
    # Total of entry amounts equals the nominal found in input
    entries = [
        {"amount_raw": "2.500.000"},
        {"amount_raw": "1.000.000"},
    ]
    result = validate_nominal_match(entries, "Total 3.500.000 rupiah")
    assert result.is_valid is True


def test_validate_nominal_match_false():
    entries = [
        {"amount_raw": "2.500.000"},
    ]
    result = validate_nominal_match(entries, "Total 1.000.000 rupiah")
    assert result.is_valid is False


def test_ziswaf_validation_result_default():
    result = ZiswafValidationResult()
    assert result.is_valid is True
    assert result.error is None