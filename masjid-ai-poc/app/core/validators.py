import re
from typing import List


def is_substring_of_input(candidate: str, input_text: str) -> bool:
    """Check if candidate appears in input_text (case-insensitive, normalized whitespace)."""
    if not candidate or not input_text:
        return False
    norm_candidate = re.sub(r"\s+", " ", candidate.strip().lower())
    norm_input = re.sub(r"\s+", " ", input_text.strip().lower())
    return norm_candidate in norm_input


def in_enum(value: str, allowed: List[str]) -> bool:
    """Check if value is a member of allowed enum list."""
    return value in allowed


def numbers_subset(output_text: str, allowed_numbers: List[str]) -> bool:
    """Check that every number in output_text appears in allowed_numbers."""
    found = re.findall(r"\d[\d\.,]*", output_text)
    allowed_set = set(allowed_numbers)
    for num in found:
        if num not in allowed_set:
            return False
    return True


def contains_forbidden_patterns(
    text: str, patterns: List[str], allowed_from_input: List[str]
) -> bool:
    """Check if text contains any forbidden pattern not present in allowed_from_input."""
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            for match in matches:
                if match not in allowed_from_input:
                    return True
    return False
