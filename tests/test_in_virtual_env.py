import sys

import microvenv


def test_in_virtual_env():
    assert microvenv.IN_VIRTUAL_ENV == (sys.prefix != sys.base_prefix)
