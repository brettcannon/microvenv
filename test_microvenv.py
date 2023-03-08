import configparser
import os
import pathlib
import subprocess
import sys
import venv

import pytest

import microvenv


@pytest.fixture(scope="session")
def full_venv(tmp_path_factory):
    venv_path = tmp_path_factory.mktemp("venvs") / "full_venv"
    venv_builder = venv.EnvBuilder(
        symlinks=True, with_pip=False, system_site_packages=False
    )
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
    micro_lib64 = micro_venv / "lib64"
    if not (full_venv / "lib64").exists():
        assert not micro_lib64.exists()
    else:
        assert micro_lib64.exists()
        assert micro_lib64.is_symlink()
        assert micro_lib64.resolve() == (micro_venv / "lib")


@pytest.mark.parametrize(
    "key",
    ["include-system-site-packages", "version"],
)
def test_pyvenvcfg_data(full_venv, micro_venv, key):
    full_config = pyvenvcfg(full_venv)
    micro_config = pyvenvcfg(micro_venv)

    # Use the full config as source of keys to check as as we may have keys in the micro
    # venv that too new for the version of Python being tested against.
    if key in full_config:
        assert key in micro_config
        assert full_config[key] == micro_config[key]


def test_pyvenvcfg_home(full_venv, micro_venv):
    raw_path = pathlib.Path(sys.executable)
    raw_dir = raw_path.parent
    resolved_dir = raw_path.resolve().parent
    dir_options = frozenset(map(os.fsdecode, (raw_dir, resolved_dir)))
    full_config = pyvenvcfg(full_venv)
    micro_config = pyvenvcfg(micro_venv)

    assert full_config["home"] in dir_options  # Sanity check.
    assert micro_config["home"] in dir_options


def test_pyvenvcfg_executable(full_venv, micro_venv):
    full_config = pyvenvcfg(full_venv)
    if "executable" not in full_config:
        # Introduced in Python 3.11.
        pytest.skip("`executable` key not in pyvenv.cfg")

    micro_config = pyvenvcfg(micro_venv)
    raw_path = pathlib.Path(sys.executable)
    resolved_path = raw_path.resolve()
    path_options = frozenset(map(os.fsdecode, (raw_path, resolved_path)))

    assert full_config["executable"] in path_options  # Sanity check.
    assert micro_config["executable"] in path_options


def test_pyvenvfg_command(micro_venv):
    config = pyvenvcfg(micro_venv)
    assert config["command"] == f"{sys.executable} {microvenv.__file__} {micro_venv}"


def test_code_size(monkeypatch, tmp_path):
    """Make sure the source code can fit into `argv` for use with `-c`."""
    with open(microvenv.__file__, "r", encoding="utf-8") as file:
        source = file.read()
    monkeypatch.chdir(tmp_path)
    subprocess.check_call([sys.executable, "-c", source])
