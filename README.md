# `microvenv`

Create a minimal virtual environment.

This module is meant for when `venv` has been removed from the standard library
by your Python distribution. Because `venv` is not available on PyPI and is
developed in the stdlib, it is not possible to install it using `pip` or simply
copy the code and expect it to work with older versions of Python.


## Usage

### Script

```
<python> microvenv.py [path=".venv"]
```

If an argument is provided to the script, it is used as the path to create the
virtual environment in. Otherwise, the virtual environment is created in
`.venv`.

### API

```
microvenv.create(venv_dir: pathlib.Path) -> None
```

## Differences compared to the [`venv` module](https://docs.python.org/3/library/venv.html#module-venv)

- There are no activation scripts (execute `python` directly).
- Pip is not installed.
- Symlinks are used (i.e. Windows users need to enable symlinks).
