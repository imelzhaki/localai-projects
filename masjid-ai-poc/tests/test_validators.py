import pytest
from app.core.validators import (
    is_substring_of_input,
    in_enum,
    numbers_subset,
    contains_forbidden_patterns,
)


def test_is_substring_of_input_true():
    assert is_substring_of_input("2.500.000", "H. Ahmad zakat 2.500.000 cash") is True


def test_is_substring_of_input_false():
    assert is_substring_of_input("2.500.000", "H. Ahmad zakat 3.000.000 cash") is False


def test_is_substring_of_input_case_insensitive():
    assert is_substring_of_input("H. AHMAD", "H. Ahmad zakat") is True


def test_in_enum_true():
    assert in_enum("ZAKAT_MAAL", ["ZAKAT_MAAL", "ZAKAT_FITRAH", "INFAQ"]) is True


def test_in_enum_false():
    assert in_enum("LAINNYA", ["ZAKAT_MAAL", "ZAKAT_FITRAH", "INFAQ"]) is False


def test_numbers_subset_true():
    assert numbers_subset("Total Rp 2.500.000", ["2.500.000", "100.000"]) is True


def test_numbers_subset_false():
    assert numbers_subset("Total Rp 999.999", ["2.500.000", "100.000"]) is False


def test_contains_forbidden_patterns_found():
    patterns = [r"QS\.", r"HR\."]
    assert contains_forbidden_patterns("Baca QS. Al-Baqarah", patterns, []) is True


def test_contains_forbidden_patterns_not_found():
    patterns = [r"QS\.", r"HR\."]
    assert contains_forbidden_patterns("Baca ayat 5", patterns, []) is False
