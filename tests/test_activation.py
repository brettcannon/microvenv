import os
import pathlib
import sys

import pytest

import microvenv


def test_no_venv(monkeypatch):
    monkeypatch.setattr(microvenv, "IN_VIRTUAL_ENV", False)
    with pytest.raises(microvenv.ActivationError):
        microvenv.activation()


def test_PYTHONHOME():
    with pytest.raises(microvenv.ActivationError):
        microvenv.activation({"PYTHONHOME": "/home/user"})


def test_no_PATH():
    bin_dir = os.fsdecode(pathlib.Path(sys.executable).parent)
    env_vars = microvenv.activation({})

    assert env_vars["PATH"] == bin_dir


def test_PATH_prepended():
    path_var = os.pathsep.join(["A", "B", "C"])
    bin_dir = os.fsdecode(pathlib.Path(sys.executable).parent)
    env_vars = microvenv.activation({"PATH": path_var})

    assert env_vars["PATH"] == os.pathsep.join([bin_dir, path_var])


def test_VIRTUAL_ENV():
    env_path = pathlib.Path(sys.executable).parent.parent
    env_vars = microvenv.activation({})

    assert env_vars["VIRTUAL_ENV"] == os.fsdecode(env_path)


def test_default_env_vars():
    bin_path = pathlib.Path(sys.executable).parent
    bin_dir = os.fsdecode(bin_path)
    path = os.pathsep.join([bin_dir, os.environ["PATH"]])
    virtual_env = os.fsdecode(bin_path.parent)
    env_vars = microvenv.activation()

    assert env_vars["PATH"] == path
    assert env_vars["VIRTUAL_ENV"] == virtual_env
