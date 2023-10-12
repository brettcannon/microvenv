import os
import pathlib
import subprocess
import sys

import pytest

import microvenv
import microvenv._create

if sys.platform == "win32":
    pytest.skip("Windows is not supported.", allow_module_level=True)


@pytest.fixture
def base_executable():
    try:
        return pathlib.Path(sys._base_executable)
    except AttributeError:
        return pathlib.Path(sys.executable)


@pytest.fixture(scope="session")
def micro_venv(tmp_path_factory):
    venv_path = tmp_path_factory.mktemp("venvs") / "micro_venv"
    microvenv.create(venv_path)
    return venv_path


def test_code_size(executable, monkeypatch, tmp_path):
    """Make sure the source code can fit into `argv` for use with `-c`."""
    with open(microvenv._create.__file__, "r", encoding="utf-8") as file:
        source = file.read()
    monkeypatch.chdir(tmp_path)
    env_path = pathlib.Path(microvenv.DEFAULT_ENV_DIR)
    subprocess.check_call([os.fsdecode(executable), "-c", source])

    # Since `__name__ == "__main__"` calls `_create.main()`, don't worry about
    # validating the virtual environment details as the CLI tests take care of
    # that.
    assert env_path.is_dir()
    command = microvenv.parse_config(env_path)["command"]
    assert command.startswith(sys.executable)
    assert " -c " in command


def test_structure(full_venv, micro_venv):
    for dirpath, dirnames, filenames in os.walk(full_venv):
        root = pathlib.Path(dirpath)
        relative_root = root.relative_to(full_venv)
        micro_root = micro_venv / relative_root
        for dirname in dirnames:
            micro_dir = micro_root / dirname
            assert micro_dir.is_dir()

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
        # pathlib.Path.readlink() was added in Python 3.9.
        assert os.readlink(micro_lib64) == "lib"


@pytest.mark.parametrize(
    "key",
    ["include-system-site-packages", "version"],
)
def test_pyvenvcfg_data(full_venv, micro_venv, key):
    full_config = microvenv.parse_config(full_venv)
    micro_config = microvenv.parse_config(micro_venv)

    # Use the full config as source of keys to check as as we may have keys in the micro
    # venv that too new for the version of Python being tested against.
    if key in full_config:
        assert key in micro_config
        assert full_config[key] == micro_config[key]


def test_pyvenvcfg_home(base_executable, full_venv, micro_venv):
    full_config = microvenv.parse_config(full_venv)
    micro_config = microvenv.parse_config(micro_venv)

    assert full_config["home"] == os.fsdecode(base_executable.parent)  # Sanity check.
    assert micro_config["home"] == os.fsdecode(base_executable.parent)


def test_pyvenvcfg_executable(base_executable, full_venv, micro_venv):
    resolved_base_executable = base_executable.resolve()
    executable_path = os.fsdecode(resolved_base_executable)
    full_config = microvenv.parse_config(full_venv)
    if "executable" not in full_config:
        # Introduced in Python 3.11.
        pytest.skip("`executable` key not in pyvenv.cfg")

    micro_config = microvenv.parse_config(micro_venv)

    assert full_config["executable"] == executable_path  # Sanity check.
    assert micro_config["executable"] == executable_path


def test_pyvenvcfg_command(executable, micro_venv):
    config = microvenv.parse_config(micro_venv)
    script_path = pathlib.Path(microvenv._create.__file__).resolve()
    assert config["command"] == f"{executable} {script_path} {micro_venv.resolve()}"


def test_pyvenvcfg_command_relative(executable, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    venv_path = tmp_path / "venv"
    microvenv.create(pathlib.Path(venv_path.name))
    script_path = pathlib.Path(microvenv._create.__file__).resolve()
    config = microvenv.parse_config(venv_path)
    assert config["command"] == f"{executable} {script_path} {venv_path.resolve()}"
