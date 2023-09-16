import pathlib
import sys

import pytest


@pytest.fixture
def executable():
    return pathlib.Path(sys.executable)
