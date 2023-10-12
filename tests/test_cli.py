import os
import subprocess
import sys

import pytest

import microvenv

if sys.platform == "win32":
    pytest.skip("Windows is not supported.", allow_module_level=True)


@pytest.fixture
def CLI(executable):
    def _CLI(*args):
        subprocess.check_call(
            [os.fsdecode(executable), microvenv._create.__file__, *args]
        )

    return _CLI


@pytest.mark.parametrize(
    ["args", "expected_dir"], [([], ".venv"), (["some-venv"], "some-venv")]
)
def test_relative_path(monkeypatch, tmp_path, args, expected_dir, CLI):
    """Test using a relative path (both the default and explicitly provided)."""
    path = tmp_path / expected_dir
    monkeypatch.chdir(tmp_path)
    CLI(*args)
    assert path.is_dir()
    assert (path / "pyvenv.cfg").is_file()


def test_absolute_path(tmp_path, CLI):
    path = tmp_path / "some-venv"
    CLI(os.fsdecode(path))

    assert path.is_dir()
    assert (path / "pyvenv.cfg").is_file()


def test_too_many_args(tmp_path, CLI):
    path = tmp_path / "some-venv"
    with pytest.raises(subprocess.CalledProcessError):
        CLI(os.fsdecode(path), "extra-arg")

    assert not path.exists()


def test_default_scm_ignore_files(tmp_path, CLI):
    venv_path = tmp_path / "some-venv"
    CLI(os.fsdecode(venv_path))
    gitignore_path = venv_path / ".gitignore"

    assert gitignore_path.is_file()
    assert gitignore_path.read_text(encoding="utf-8") == "*\n"


def test_without_scm_ignore_files(tmp_path, CLI):
    venv_path = tmp_path / "some-venv"
    CLI("--without-scm-ignore-files", os.fsdecode(venv_path))
    gitignore_path = venv_path / ".gitignore"

    assert not gitignore_path.exists()
