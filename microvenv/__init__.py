import pathlib
import sys

# Exported as part of the public API.
from ._create import create as create

# https://docs.python.org/3/library/venv.html#how-venvs-work
IN_VIRTUAL_ENV = sys.prefix != sys.base_prefix



def parse_config(env_dir):
    """Parse the pyvenv.cfg file in the specified virtual environment.

    A dict is returned with strings for keys and values. All keys are
    lowercased, but otherwise no validation is performed. No changes are made to
    the values (e.g., include-system-site-packages is not converted to a boolean
    nor lowerased).

    Parsing is done in a way identical to how the 'site' modules does it. This
    means that ANY line with an ``=`` sign is considered a line with a key/value
    pair on it. As such, all other lines are treated as if they are comments.
    But this also means that having a line start with e.g., ``#`` does not
    signify a comment either if there is a ``=`` in the line.
    """
    config = {}
    venv_path = pathlib.Path(env_dir)
    with open(venv_path / "pyvenv.cfg", "r", encoding="utf-8") as file:
        # This is how `site` parses `pyvenv.cfg`, so it's about as
        # official as we can get.
        for line in file:
            if "=" in line:
                key, _, value = line.partition("=")
                config[key.strip().lower()] = value.strip()
    return config

