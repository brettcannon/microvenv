import os
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


# There are three possible APIs for helping with virtual environment activation:
# 1. Mutate the environment variable dictionary in-place;
#    ``activate(os.environ.copy())``
# 2. Return a mutated copy; ``activated_env_copy()``
# 3. Calculate the environment variables to add; ``os.environ | activation()``
#
# Option 1 has the issue that if you forget to pass in a copy you will end up
# mutating the running process' environment (in most cases).
# Option 2 has the issue of needing an awkward name to communicate what exactly
# is occurring.
# Option 3 has the issue of not being able to delete environment variables
# (i.e., PYTHONHOME).
#
# The decision was to go with option 3 with an exception if PYTHONHOME is set as
# it's the most self-documenting for the common case of PYTHONHOME not already
# being set.
def activation(env_vars=os.environ):
    """Returns a dict with env vars to activate the current virtual environment.

    If the current interpreter is not from a virtual environment,
    ActivationError is raised.

    Since this API is designed to be additive to a environment variables dict
    (i.e., ``os.environ | activation()``), key deletions are not supported. As
    such, ActivationError is raised if PYTHONHOME is found to be set.

    No environment variables are provided in relation to shell prompts.
    """
    # XXX in a virtual environment
    # XXX PYTHONHOME
    # XXX PATH
    # XXX VIRTUAL_ENV
