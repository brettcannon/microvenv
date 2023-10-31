# microvenv

Create a minimal virtual environment (and utility code around environments).

The key purpose of this module is for when the [`venv` module](https://docs.python.org/3/library/venv.html#module-venv) has been removed from the standard library by your Python distribution. Because `venv` is not available on PyPI and is developed in the stdlib, it is not possible to install it using `pip` or simply copy the code and expect it to work with older versions of Python. This module then attempts to be that portable alternative for creating virtual environments.

In general, though, using the [`venv` module](https://docs.python.org/3/library/venv.html#module-venv) should be preferred and this module used as a fallback.

There is also utility code around virtual environments. See the [docs](https://microvenv.rtfd.io/) for details.

## CLI Usage

**NOTE**: The CLI is not available on Windows.

```console
python -m microvenv [--without-scm-ignore-files] [env_dir=".venv"]
```

If an argument is provided to the script, it is used as the path to create the virtual environment in. Otherwise, the virtual environment is created in `.venv`.

For programmatic usage, there is the `create()` function, which is analogous to the [`venv.create()` function](https://docs.python.org/3/library/venv.html#venv.create).

```python
def create(env_dir: os.PathLike[str] | str = ".venv", *, scm_ignore_files={"git"}) -> None
```

The `microvenv/_create.py` file is also small enough to have its contents passed in via the `-c` flag to `python`.

### Differences compared to the [`venv` module](https://docs.python.org/3/library/venv.html#module-venv)

The code operates similarly to `py -m venv --symlinks --without-pip .venv`,
except that:

- There are no activation scripts (you can execute `python` in the virtual environment directly)
- Windows is not supported
