import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app


def test_tentukan_stage_guiding_saat_counter_nol():
    assert app.tentukan_stage(0) == "guiding"


def test_tentukan_stage_guiding_saat_counter_dibawah_batas():
    assert app.tentukan_stage(1) == "guiding"
    assert app.tentukan_stage(2) == "guiding"


def test_tentukan_stage_hint_saat_counter_mencapai_batas():
    assert app.tentukan_stage(3) == "hint"


def test_tentukan_stage_reveal_saat_counter_lebih_dari_batas():
    assert app.tentukan_stage(4) == "reveal"
    assert app.tentukan_stage(5) == "reveal"


def test_reset_mengembalikan_nilai_awal():
    messages, question_count, stage = app.reset_state()
    assert messages == []
    assert question_count == 0
    assert stage == "guiding"
