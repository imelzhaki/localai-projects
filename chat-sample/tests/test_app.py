import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app


def test_build_user_message():
    result = app.build_user_message("hello")
    assert result == {"role": "user", "content": "hello"}


def test_build_assistant_message():
    result = app.build_assistant_message("hi")
    assert result == {"role": "assistant", "content": "hi"}
