from os import PathLike
from typing import TypedDict

IN_VIRTUAL_ENV: bool

DEFAULT_ENV_DIR: str

class ActivationError(Exception): ...

def parse_config(env_dir: str | PathLike[str]) -> dict[str, str]: ...

class _ActivationEnvVars(TypedDict):
    PATH: str
    VIRTUAL_ENV: str

def activation(env_vars: dict[str, str] = ...) -> _ActivationEnvVars: ...
