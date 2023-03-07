# `microvenv`

Create a minimal virtual environment.

This module is meant for when the [`venv` module](https://docs.python.org/3/library/venv.html#module-venv) has been removed from the standard library by your Python distribution. Because `venv` is not available on PyPI and is developed in the stdlib, it is not possible to install it using `pip` or simply copy the code and expect it to work with older versions of Python. This module then attempts to be that portable alternative for creating virtual environments.

In general, though, using the [`venv` module](https://docs.python.org/3/library/venv.html#module-venv) should be preferred and this module is only used as a fallback.


## Usage

```
<python> microvenv.py [path=".venv"]
```

If an argument is provided to the script, it is used as the path to create the virtual environment in. Otherwise, the virtual environment is created in `.venv`.

For programmatic usage, use the [`runpy` module](https://docs.python.org/3/library/runpy.html#module-runpy) to execute the script.

## Differences compared to the [`venv` module](https://docs.python.org/3/library/venv.html#module-venv)

The module operates similarly to `py -m venv --symlinks --without-pip .venv`,
except that:

- There are no activation scripts (execute `python` in the virtual environment directly).
- Windows is not supported.
