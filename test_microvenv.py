import configparser
import os
import pathlib
import sys
import venv

import pytest

import microvenv


@pytest.fixture(scope="session")
def full_venv(tmp_path_factory):
    venv_path = tmp_path_factory.mktemp("venvs") / "full_venv"
    venv_builder = venv.EnvBuilder()
    venv_builder.create(venv_path)
    return venv_path


@pytest.fixture(scope="session")
def micro_venv(tmp_path_factory):
    venv_path = tmp_path_factory.mktemp("venvs") / "micro_venv"
    microvenv.create(venv_path)
    return venv_path


def pyvenvcfg(venv_path):
    config_text = (venv_path / "pyvenv.cfg").read_text(encoding="utf-8")
    config = configparser.ConfigParser()
    config.read_string("\n".join(["[_]", config_text]))
    return config["_"]


def test_structure(full_venv, micro_venv):
    for dirpath, dirnames, filenames in os.walk(full_venv):
        root = pathlib.Path(dirpath)
        relative_root = root.relative_to(full_venv)
        micro_root = micro_venv / relative_root
        for dirname in dirnames:
            micro_dir = micro_root / dirname
            micro_dir.is_dir()

        for filename in filenames:
            # Don't care about activation scripts.
            if filename.lower().startswith("activate"):
                continue
            micro_file = micro_root / filename
            full_file = root / filename
            if full_file.is_file():
                assert micro_file.is_file()
            # Make sure that e.g. `python` is properly symlinked.
            elif full_file.is_symlink():
                assert micro_file.is_symlink()
                assert micro_file.resolve() == full_file.resolve()


def test_lib64(full_venv, micro_venv):
    if not (full_venv / "lib64").exists():
        pytest.skip("lib64 does not exist")

    micro_lib64 = micro_venv / "lib64"
    assert micro_lib64.is_symlink()
    assert micro_lib64.resolve() == (micro_venv / "lib")


@pytest.mark.parametrize(
    "key", ["home", "include-system-site-packages", "version", "executable", "command"]
)
def test_pyvenvcfg(full_venv, micro_venv, key):
    full_config = pyvenvcfg(full_venv)
    micro_config = pyvenvcfg(micro_venv)

    # Use the full config as source of keys to check as as we may have keys in the micro
    # venv that too new for the version of Python being tested against.
    if key in full_config:
        assert key in micro_config
        assert full_config[key] == micro_config[key]


def test_command(micro_venv):
    config = pyvenvcfg(micro_venv)
    assert config["command"] == f"{sys.executable} {microvenv.__file__} {micro_venv}"
