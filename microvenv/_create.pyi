from os import PathLike
from typing import Iterable

DEFAULT_ENV_DIR: str

def create(
    env_dir: str | PathLike[str] = ..., *, scm_ignore_files=Iterable[str]
) -> None: ...
def main() -> None: ...
