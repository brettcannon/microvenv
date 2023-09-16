"""A minimal, self-contained implementation of `venv`."""
import argparse
import os
import pathlib
import sys
import sysconfig

# Should not change during execution, so it's reasonable as a global.
_BASE_EXECUTABLE = pathlib.Path(getattr(sys, "_base_executable", sys.executable))

_PYVENVCFG_TEMPLATE = f"""\
home = {_BASE_EXECUTABLE.parent}
include-system-site-packages = false
version = {'.'.join(map(str, sys.version_info[:3]))}
executable = {_BASE_EXECUTABLE.resolve()}
command = {{command}}
"""


def _sysconfig_path(name, env_dir):
    variables = {
        "base": env_dir,
        "platbase": env_dir,
        "installed_base": env_dir,
        "installed_platbase": env_dir,
    }

    return pathlib.Path(sysconfig.get_path(name, "venv", variables))


# Analogous to `venv.create()`.
def create(env_dir=".venv", *, scm_ignore_files=frozenset(["git"])):
    """Create a minimal virtual environment.

    Analogous to `venv.create(env_dir, symlinks=True, with_pip=False)`.
    """
    env_path = pathlib.Path(env_dir)
    # sysconfig scheme support introduced in Python 3.11.
    try:
        scripts_dir = _sysconfig_path("scripts", env_path)
        include_dir = _sysconfig_path("include", env_path)
        purelib_dir = _sysconfig_path("purelib", env_path)
    except KeyError:
        scripts_dir = env_path / "bin"
        include_dir = env_path / "include"
        purelib_dir = (
            env_path
            / "lib"
            / f"python{sys.version_info.major}.{sys.version_info.minor}"
            / "site-packages"
        )
    for dir in (scripts_dir, include_dir, purelib_dir):
        dir.mkdir(parents=True)

    if sys.maxsize > 2**32 and os.name == "posix" and sys.platform != "darwin":
        lib_path = env_path / "lib"
        lib64_path = env_path / "lib64"
        # There is no guarantee the sysconfig scheme will produce a `lib`
        # directory.
        if lib_path.is_dir() and not lib64_path.exists():
            lib64_path.symlink_to("lib", target_is_directory=True)

    for executable_name in (
        "python",
        f"python{sys.version_info.major}",
        f"python{sys.version_info.major}.{sys.version_info.minor}",
    ):
        (scripts_dir / executable_name).symlink_to(_BASE_EXECUTABLE)

    if __spec__ is None:
        command = f"{sys.executable} -c '...'"
    else:
        module_path = pathlib.Path(__spec__.origin).resolve()
        command = f"{sys.executable} {module_path} {env_path.resolve()}"
    (env_path / "pyvenv.cfg").write_text(
        _PYVENVCFG_TEMPLATE.format(command=command),
        encoding="utf-8",
    )

    scm_ignore_files = frozenset(scm_ignore_files)
    if scm_ignore_files == {"git"}:
        (env_path / ".gitignore").write_text("*\n", encoding="utf-8")
    elif scm_ignore_files:
        unexpected = scm_ignore_files - {"git"}
        raise NotImplementedError(
            f"Only `git` is supported as a SCM ignore file, not {unexpected}."
        )


def main():
    parser = argparse.ArgumentParser()
    default_dir = ".venv"
    parser.add_argument(
        "--without-scm-ignore-files",
        dest="scm_ignore_files",
        action="store_const",
        const=frozenset(),
        default=frozenset(["git"]),
        help="Skips adding SCM ignore files to the environment "
        "directory (otherwise a `.gitignore` file is added).",
    )
    parser.add_argument(
        "env_dir",
        default=default_dir,
        nargs="?",
        help=f"Directory to create virtual environment in (default: {default_dir!r}",
    )
    args = parser.parse_args()
    create(args.env_dir, scm_ignore_files=args.scm_ignore_files)


if __name__ == "__main__":
    main()
