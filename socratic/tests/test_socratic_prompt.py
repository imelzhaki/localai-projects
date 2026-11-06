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


def test_intro_prompt_mencakup_perkenalan_diri():
    prompt = build_system_prompt("guiding", is_first=True)
    assert "Socrates" in prompt
    assert "Perkenalkan diri" in prompt
    assert "mata pelajaran" in prompt
    assert "tingkat sekolah" in prompt
    assert "kelas" in prompt
    assert "pertanyaan pembuka" in prompt
    assert "JANGAN berikan rumus" in prompt


def test_intro_prompt_tidak_menggunakan_guiding_prompt():
    prompt_intro = build_system_prompt("guiding", is_first=True)
    prompt_guiding = build_system_prompt("guiding", is_first=False)
    assert prompt_intro != prompt_guiding
    assert "Socrates" in prompt_intro
    assert "Socrates" not in prompt_guiding


def test_intro_prompt_menggunakan_notasi_latex():
    prompt = build_system_prompt("guiding", is_first=True)
    assert "LaTeX" in prompt
    assert "$...$" in prompt
