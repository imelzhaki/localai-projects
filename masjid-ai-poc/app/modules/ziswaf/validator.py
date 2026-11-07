from dataclasses import dataclass


@dataclass
class ZiswafValidationResult:
    is_valid: bool = True
    error: str | None = None


def validate_amount_raw_substring(amount_raw: str | None, input_text: str) -> ZiswafValidationResult:
    """Ensure amount_raw appears as substring of input_text (case-insensitive, normalized)."""
    if amount_raw is None:
        return ZiswafValidationResult(is_valid=True, error=None)
    if not input_text or not input_text.strip():
        return ZiswafValidationResult(
            is_valid=False, error="amount_raw tidak ditemukan dalam input (input kosong)"
        )
    import re

    norm_amount = re.sub(r"\s+", " ", amount_raw.strip().lower())
    norm_input = re.sub(r"\s+", " ", input_text.strip().lower())
    if norm_amount not in norm_input:
        return ZiswafValidationResult(
            is_valid=False, error=f"amount_raw '{amount_raw}' tidak ditemukan dalam input"
        )
    return ZiswafValidationResult(is_valid=True, error=None)


def validate_category_enum(category: str | None) -> ZiswafValidationResult:
    """Ensure category is one of the valid enum values."""
    if category is None:
        return ZiswafValidationResult(is_valid=True, error=None)
    valid = {"zakat", "infaq", "shadaqah", "wakaf"}
    if category.lower() not in valid:
        return ZiswafValidationResult(
            is_valid=False, error=f"Kategori '{category}' tidak valid. Harus salah satu: {', '.join(sorted(valid))}"
        )
    return ZiswafValidationResult(is_valid=True, error=None)


def validate_payment_method_enum(payment_method: str | None) -> ZiswafValidationResult:
    """Ensure payment_method is one of the valid enum values."""
    if payment_method is None:
        return ZiswafValidationResult(is_valid=True, error=None)
    valid = {"tunai", "transfer", "qris"}
    if payment_method.lower() not in valid:
        return ZiswafValidationResult(
            is_valid=False,
            error=f"Metode pembayaran '{payment_method}' tidak valid. Harus salah satu: {', '.join(sorted(valid))}",
        )
    return ZiswafValidationResult(is_valid=True, error=None)


def validate_no_duplicate_entries(entries: list[dict]) -> ZiswafValidationResult:
    """Detect duplicate entries based on donor_name + amount_raw combination."""
    seen = set()
    for entry in entries:
        key = (entry.get("donor_name"), entry.get("amount_raw"))
        if key in seen:
            return ZiswafValidationResult(
                is_valid=False,
                error=f"Duplikat terdeteksi: donor={entry.get('donor_name')}, amount={entry.get('amount_raw')}",
            )
        seen.add(key)
    return ZiswafValidationResult(is_valid=True, error=None)


def validate_nominal_match(entries: list[dict], input_text: str) -> ZiswafValidationResult:
    """Ensure sum of parsed entry amounts matches the total nominal in input."""
    from app.core.rupiah import parse_rupiah

    total_entries = 0
    for entry in entries:
        amount_raw = entry.get("amount_raw")
        if amount_raw:
            parsed = parse_rupiah(amount_raw)
            if parsed is not None:
                total_entries += parsed

    if not input_text or not input_text.strip():
        return ZiswafValidationResult(
            is_valid=False, error="Input kosong, tidak dapat memverifikasi nominal"
        )

    # Find the largest parsed number in input as the declared total
    import re

    numbers = re.findall(r"[\d\.,]+", input_text)
    parsed_numbers = []
    for num in numbers:
        # Try parsing with rupiah context (append "rupiah" for unit disambiguation)
        parsed = parse_rupiah(num + " rupiah")
        if parsed is not None:
            parsed_numbers.append(parsed)

    if not parsed_numbers:
        return ZiswafValidationResult(is_valid=True, error=None)  # No nominal to compare

    declared_total = max(parsed_numbers)
    if total_entries != declared_total:
        return ZiswafValidationResult(
            is_valid=False,
            error=f"Jumlah entri ({total_entries}) tidak sama dengan nominal dalam input ({declared_total})",
        )
    return ZiswafValidationResult(is_valid=True, error=None)