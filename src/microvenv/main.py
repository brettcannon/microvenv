import pathlib
import sys

# We don't resolve `sys.executable` on purpose.
pyvenvcfg_template = f"""home = {pathlib.Path(sys.executable).parent}
include-system-site-packages = false
version = {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}
executable = {sys.executable}
command = {sys.executable} {__file__} {{venv_dir}}
"""


def create(venv_dir):
    # XXX Unix-specific
    # XXX Use sysconfig (if possible); https://github.com/python/cpython/blob/cb944d0be869dfb1189265467ec8a986176cc104/Lib/venv/__init__.py#L103
    for subdir in (
        "bin",
        "include",
        pathlib.PurePath(
            "lib",
            f"python{sys.version_info.major}.{sys.version_info.minor}",
            "site-packages",
        ),
    ):
        (venv_dir / subdir).mkdir(parents=True)

    # XXX https://github.com/python/cpython/blob/6c2e052ee07f10a6336bb4de1cef71dbe7d30ee6/Lib/venv/__init__.py#L143
    (venv_dir / "lib64").symlink_to("lib", target_is_directory=True)

    executable = pathlib.Path(sys.executable).resolve()
    for executable_name in (
        "python",
        f"python{sys.version_info.major}",
        f"python{sys.version_info.major}.{sys.version_info.minor}",
    ):
        (venv_dir / "bin" / executable_name).symlink_to(executable)

    (venv_dir / "pyvenv.cfg").write_text(
        pyvenvcfg_template.format(venv_dir=venv_dir), encoding="utf-8"
    )


def main():
    if len(sys.argv) > 2:
        print("Usage: microvenv.py [venv_dir='.venv']", file=sys.stderr)
        sys.exit(1)

    try:
        venv_dir = sys.argv[1]
    except IndexError:
        venv_dir = ".venv"

    create(pathlib.Path(venv_dir))

if __name__ == "__main__":
    main()

