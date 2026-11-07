import pytest
from app.core.rupiah import parse_rupiah


@pytest.mark.parametrize("text,expected", [
    ("2.500.000", 2500000),
    ("2,5 jt", 2500000),
    ("2,5jt", 2500000),
    ("100rb", 100000),
    ("100 ribu", 100000),
    ("Rp 250.000,-", 250000),
    ("Rp250rb", 250000),
    ("1jt", 1000000),
    ("1,5 juta", 1500000),
    ("75.000", 75000),
    ("500 ribu rupiah", 500000),
    ("100", None),  # ambiguous, no unit
    ("abc", None),
    ("", None),
])
def test_parse_rupiah(text, expected):
    assert parse_rupiah(text) == expected