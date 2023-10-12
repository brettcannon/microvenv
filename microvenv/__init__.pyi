from os import PathLike, _Environ
from typing import TypedDict

IN_VIRTUAL_ENV: bool

class ActivationError(Exception): ...

def parse_config(env_dir: str | PathLike[str]) -> dict[str, str]: ...

class _ActivationEnvVars(TypedDict):
    PATH: str
    VIRTUAL_ENV: str

def activation(env_vars: _Environ[str] = ...) -> _ActivationEnvVars: ...
