import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import DEPARTMENTS, PRIORITIES, CATEGORIES, DEPARTMENT_GROUPS, OLLAMA_HOST, OLLAMA_MODEL


def test_departments_contains_expected_values():
    assert "IT_SUPPORT" in DEPARTMENTS
    assert "HR" in DEPARTMENTS
    assert "FINANCE" in DEPARTMENTS
    assert "GENERAL" in DEPARTMENTS


def test_priorities_contains_expected_values():
    assert "LOW" in PRIORITIES
    assert "MEDIUM" in PRIORITIES
    assert "HIGH" in PRIORITIES
    assert "URGENT" in PRIORITIES


def test_categories_mapped_per_department():
    assert "HARDWARE_FAILURE" in CATEGORIES["IT_SUPPORT"]
    assert "LEAVE_REQUEST" in CATEGORIES["HR"]
    assert "INVOICE" in CATEGORIES["FINANCE"]
    assert "INQUIRY" in CATEGORIES["GENERAL"]


def test_ollama_host_and_model_defaults():
    assert OLLAMA_HOST == "http://localhost:11434"
    assert OLLAMA_MODEL == "llama3.2:3b"
