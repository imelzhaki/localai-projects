import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from socratic_prompt import build_system_prompt


def test_guiding_prompt_mencakup_larang_jawaban_langsung():
    prompt = build_system_prompt("guiding")
    assert "JANGAN" in prompt
    assert "jawaban langsung" in prompt
    assert "pertanyaan penuntang" in prompt
    assert "Bahasa Indonesia" in prompt


def test_hint_prompt_mencakup_petunjuk_kecil():
    prompt = build_system_prompt("hint")
    assert "PETUNJUK" in prompt
    assert "bukan jawaban penuh" in prompt


def test_reveal_prompt_mencakup_jawaban_lengkap():
    prompt = build_system_prompt("reveal")
    assert "JAWABAN" in prompt
    assert "penjelasan singkat" in prompt


def test_tahap_tidak_dikenal_mengembalikan_guiding():
    prompt = build_system_prompt("tidak_valid")
    assert prompt == build_system_prompt("guiding")


def test_semua_tahap_menggunakan_notasi_latex():
    for tahap in ("guiding", "hint", "reveal"):
        prompt = build_system_prompt(tahap)
        assert "LaTeX" in prompt
        assert "$...$" in prompt
