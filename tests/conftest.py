import pathlib
import sys
import venv

import pytest


@pytest.fixture
def executable():
    """Return the current interpreter's path."""
    return pathlib.Path(sys.executable)


@pytest.fixture(scope="session")
def full_venv(tmp_path_factory):
    """Create a virtual environment via venv."""
    symlinks = sys.platform != "win32"
    venv_path = tmp_path_factory.mktemp("venvs") / "full_venv"
    venv.create(
        venv_path, symlinks=symlinks, with_pip=False, system_site_packages=False
    )
    return venv_path
