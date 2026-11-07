import re


def parse_rupiah(text: str) -> int | None:
    """Parse an Indonesian rupiah amount from free text.

    Returns the amount in rupiah (int), or None if the amount is
    ambiguous or unparseable. Never guesses — returns None when no
    unit or thousand separator is present to disambiguate.

    Supported formats:
        "2.500.000"        -> 2500000   (thousand-separator dots)
        "2,5 jt" / "2,5jt" -> 2500000   (decimal comma + unit)
        "1,5 juta"         -> 1500000
        "100rb" / "100 ribu" -> 100000
        "Rp 250.000,-"     -> 250000
        "1jt"              -> 1000000
        "100"              -> None      (ambiguous, no unit)
    """
    if not text or not text.strip():
        return None

    s = text.strip().lower()

    # Remove currency markers and trailing words
    s = s.replace("rp", "").replace(",-", "").replace("-", "").replace("rupiah", "").strip()

    if not s:
        return None

    units = {
        "jt": 1_000_000,
        "juta": 1_000_000,
        "rb": 1_000,
        "ribu": 1_000,
    }

    # Decimal comma pattern: "2,5 jt", "2,5jt", "1,5 juta"
    m = re.match(r"^(\d+),(\d+)\s*(jt|juta|rb|ribu)?$", s)
    if m:
        whole = int(m.group(1))
        frac_str = m.group(2)
        unit = m.group(3)
        multiplier = units.get(unit, 1)
        frac_value = int(frac_str)
        frac_divisor = 10 ** len(frac_str)
        return whole * multiplier + (frac_value * multiplier // frac_divisor)

    # Thousand-separator dots present (e.g. "2.500.000", "75.000")
    has_dots = "." in s
    s_no_dots = s.replace(".", "")

    # Plain number with optional unit
    m = re.match(r"^(\d+)\s*(jt|juta|rb|ribu)?\s*$", s_no_dots)
    if m:
        value = int(m.group(1))
        unit = m.group(2)
        if unit:
            return value * units[unit]
        elif has_dots:
            return value
        else:
            return None

    return None
