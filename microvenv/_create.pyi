from os import PathLike
import sys
from typing import Iterable

DEFAULT_ENV_DIR: str

if sys.platform != "win32":
    def create(
        env_dir: str | PathLike[str] = ..., *, scm_ignore_files=Iterable[str]
    ) -> None: ...
    def main() -> None: ...
