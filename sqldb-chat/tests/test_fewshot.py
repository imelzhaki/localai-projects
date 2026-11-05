import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fewshot import get_fewshot_examples


def test_get_fewshot_examples_returns_bilingual_pairs():
    examples = get_fewshot_examples()
    assert isinstance(examples, list)
    assert len(examples) > 0
    for ex in examples:
        assert "question_id" in ex
        assert "question" in ex
        assert "sql" in ex
        assert "language" in ex


def test_get_fewshot_examples_has_indonesian_and_english():
    examples = get_fewshot_examples()
    languages = {ex["language"] for ex in examples}
    assert "id" in languages
    assert "en" in languages


def test_get_fewshot_examples_sql_is_select_only():
    examples = get_fewshot_examples()
    for ex in examples:
        sql = ex["sql"].strip().upper()
        assert sql.startswith("SELECT"), f"Non-SELECT SQL found: {ex['sql']}"


def test_get_fewshot_examples_uses_known_tables():
    examples = get_fewshot_examples()
    known_tables = {
        "CUSTOMER", "SUPPLIER", "PRODUCT",
        "SALES_ORDER", "SALES_ORDER_ITEM", "PURCHASE_ORDER",
    }
    for ex in examples:
        sql_upper = ex["sql"].upper()
        assert any(t in sql_upper for t in known_tables), (
            f"SQL uses unknown table: {ex['sql']}"
        )