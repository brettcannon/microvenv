import os
import pathlib
import sys
import sysconfig

# We don't resolve `sys.executable` on purpose.
pyvenvcfg_template = f"""home = {pathlib.Path(sys.executable).resolve().parent}
include-system-site-packages = false
version = {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}
executable = {pathlib.Path(sys.executable).resolve()}
command = {sys.executable} {__file__} {{venv_dir}}
"""


def create(venv_dir):
    variables = {
        "base": venv_dir,
        "platbase": venv_dir,
        "installed_base": venv_dir,
        "installed_platbase": venv_dir,
    }
    try:
        paths = [
            pathlib.Path(sysconfig.get_path(name, "venv", variables))
            for name in ("scripts", "include", "purelib")
        ]
    except KeyError:
        paths = [
            venv_dir / subdir
            for subdir in (
                "bin",
                "include",
                pathlib.Path(
                    "lib",
                    f"python{sys.version_info.major}.{sys.version_info.minor}",
                    "site-packages",
                ),
            )
        ]
    for dir in paths:
        dir.mkdir(parents=True)

    if sys.maxsize > 2**32 and os.name == "posix" and sys.platform != "darwin":
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


if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage: microvenv.py [venv_dir='.venv']", file=sys.stderr)
        sys.exit(1)

    try:
        venv_dir = sys.argv[1]
    except IndexError:
        venv_dir = ".venv"
    create(pathlib.Path(venv_dir))
