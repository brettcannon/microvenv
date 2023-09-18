import contextlib

import pytest

import microvenv


@contextlib.contextmanager
def write_config(venv_path, data):
    """Context manager to write the pyvenv.cfg and then restore it."""
    config_path = venv_path / "pyvenv.cfg"
    original_config = config_path.read_text(encoding="utf-8")
    config_path.write_text(data, encoding="utf-8")
    try:
        yield config_path
    finally:
        config_path.write_text(original_config, encoding="utf-8")


@pytest.mark.parametrize("equals", ["=", " = ", "= ", " ="])
def test_formatting_around_equals(full_venv, equals):
    with write_config(full_venv, f"key{equals}value\n"):
        config = microvenv.parse_config(full_venv)

        assert config["key"] == "value"


def test_comments(full_venv):
    with write_config(full_venv, "# A comment\nkey = value\n"):
        config = microvenv.parse_config(full_venv)

        assert config["key"] == "value"


def test_multiple_equals(full_venv):
    with write_config(full_venv, "key = value=value\n"):
        config = microvenv.parse_config(full_venv)

        assert config["key"] == "value=value"


def test_lowercase_keys(full_venv):
    with write_config(full_venv, "Key = value\n"):
        config = microvenv.parse_config(full_venv)

        assert config["key"] == "value"
