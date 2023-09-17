import sys

# Exported as part of the public API.
from ._create import create as create

# https://docs.python.org/3/library/venv.html#how-venvs-work
IN_VIRTUAL_ENV = sys.prefix != sys.base_prefix

