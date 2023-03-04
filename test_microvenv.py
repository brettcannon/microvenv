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
            assert micro_file.is_file()
            # Make sure that e.g. `python` is properly symlinked.
            if full_file.is_symlink():
                assert micro_file.is_symlink()
                assert micro_file.resolve() == full_file.resolve()


def test_lib64(full_venv, micro_venv):
    if not (full_venv / "lib64").exists():
        pytest.skip("lib64 does not exist")

    micro_lib64 = micro_venv / "lib64"
    assert micro_lib64.is_symlink()
    assert micro_lib64.resolve() == (micro_venv / "lib")


def test_pyvenvcfg(full_venv, micro_venv):
    full_config_text = (full_venv / "pyvenv.cfg").read_text(encoding="utf-8")
    full_config = configparser.ConfigParser()
    full_config.read_string("\n".join(["[_]", full_config_text]))

    micro_config_text = (micro_venv / "pyvenv.cfg").read_text(encoding="utf-8")
    micro_config = configparser.ConfigParser()
    micro_config.read_string("\n".join(["[_]", micro_config_text]))

    # Use the full config as the keys to check for as we may have keys in the micro
    # venv that too new for the version of Python being tested against.
    for key in full_config["_"]:
        if key == "command":
            continue
        assert key in micro_config["_"]
        assert full_config["_"][key] == micro_config["_"][key]

    assert (
        micro_config["_"]["command"]
        == f"{sys.executable} {microvenv.__file__} {micro_venv}"
    )
