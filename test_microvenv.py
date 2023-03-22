import os
import pathlib
import subprocess
import sys
import venv

import pytest

import microvenv


@pytest.fixture
def base_executable():
    try:
        return pathlib.Path(sys._base_executable)
    except AttributeError:
        return pathlib.Path(sys.executable)


@pytest.fixture
def executable():
    return pathlib.Path(sys.executable)


@pytest.fixture(scope="session")
def full_venv(tmp_path_factory):
    venv_path = tmp_path_factory.mktemp("venvs") / "full_venv"
    venv.create(venv_path, symlinks=True, with_pip=False, system_site_packages=False)
    return venv_path


@pytest.fixture(scope="session")
def micro_venv(tmp_path_factory):
    venv_path = tmp_path_factory.mktemp("venvs") / "micro_venv"
    microvenv.create(venv_path)
    return venv_path


def pyvenvcfg(venv_path):
    config = {}
    with open(venv_path / "pyvenv.cfg", "r", encoding="utf-8") as file:
        for line in file:
            if "=" in line:
                # This is how `site` reads a `pyvenv.cfg`, so it's about as
                # official as we can get.
                key, _, value = line.partition("=")
                config[key.strip().lower()] = value.strip()
    return config


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
    full_config = pyvenvcfg(full_venv)
    micro_config = pyvenvcfg(micro_venv)

    # Use the full config as source of keys to check as as we may have keys in the micro
    # venv that too new for the version of Python being tested against.
    if key in full_config:
        assert key in micro_config
        assert full_config[key] == micro_config[key]


def test_pyvenvcfg_home(base_executable, full_venv, micro_venv):
    full_config = pyvenvcfg(full_venv)
    micro_config = pyvenvcfg(micro_venv)

    assert full_config["home"] == os.fsdecode(base_executable.parent)  # Sanity check.
    assert micro_config["home"] == os.fsdecode(base_executable.parent)


def test_pyvenvcfg_executable(base_executable, full_venv, micro_venv):
    resolved_base_executable = base_executable.resolve()
    executable_path = os.fsdecode(resolved_base_executable)
    full_config = pyvenvcfg(full_venv)
    if "executable" not in full_config:
        # Introduced in Python 3.11.
        pytest.skip("`executable` key not in pyvenv.cfg")

    micro_config = pyvenvcfg(micro_venv)

    assert full_config["executable"] == executable_path  # Sanity check.
    assert micro_config["executable"] == executable_path


def test_pyvenvcfg_command(executable, micro_venv):
    config = pyvenvcfg(micro_venv)
    script_path = pathlib.Path(microvenv.__file__).resolve()
    assert config["command"] == f"{executable} {script_path} {micro_venv.resolve()}"


def test_pyvenvcfg_command_relative(executable, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    venv_path = tmp_path / "venv"
    microvenv.create(pathlib.Path(venv_path.name))
    script_path = pathlib.Path(microvenv.__file__).resolve()
    config = pyvenvcfg(venv_path)
    assert config["command"] == f"{executable} {script_path} {venv_path.resolve()}"


def test_code_size(executable, monkeypatch, tmp_path):
    """Make sure the source code can fit into `argv` for use with `-c`."""
    with open(microvenv.__file__, "r", encoding="utf-8") as file:
        source = file.read()
    monkeypatch.chdir(tmp_path)
    env_path = pathlib.Path(".venv")
    subprocess.check_call([os.fsdecode(executable), "-c", source])

    assert env_path.is_dir()
    command = pyvenvcfg(env_path)["command"]
    assert command.startswith(sys.executable)
    assert " -c " in command


@pytest.mark.parametrize(
    ["args", "expected_dir"], [([], ".venv"), (["some-venv"], "some-venv")]
)
def test_cli_relative_path(executable, monkeypatch, tmp_path, args, expected_dir):
    """Test using a relative path (both the default and explicitly provided)."""
    path = tmp_path / expected_dir
    monkeypatch.chdir(tmp_path)
    subprocess.check_call([os.fsdecode(executable), microvenv.__file__, *args])
    assert path.is_dir()
    assert (path / "pyvenv.cfg").is_file()


def test_cli_absolute_path(executable, tmp_path):
    path = tmp_path / "some-venv"
    subprocess.check_call(
        [os.fsdecode(executable), microvenv.__file__, os.fsdecode(path)]
    )
    assert path.is_dir()
    assert (path / "pyvenv.cfg").is_file()


def test_cli_too_many_args(executable, tmp_path):
    path = tmp_path / "some-venv"
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_call(
            [
                os.fsdecode(executable),
                microvenv.__file__,
                os.fsdecode(path),
                "extra-arg",
            ]
        )
    assert not path.exists()
