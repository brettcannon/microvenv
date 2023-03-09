import os
import pathlib
import sys
import sysconfig

EXECUTABLE = pathlib.Path(sys.executable).resolve()

# We don't resolve `sys.executable` on purpose.
pyvenvcfg_template = f"""home = {EXECUTABLE.parent}
include-system-site-packages = false
version = {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}
executable = {EXECUTABLE}
command = {{command}}
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

    for executable_name in (
        "python",
        f"python{sys.version_info.major}",
        f"python{sys.version_info.major}.{sys.version_info.minor}",
    ):
        (venv_dir / "bin" / executable_name).symlink_to(EXECUTABLE)

    try:
        script_path = pathlib.Path(__file__).resolve()
    except NameError:
        command = f"{EXECUTABLE} -c '...'"
    else:
        command = f"{EXECUTABLE} {script_path} {venv_dir.resolve()}"
    (venv_dir / "pyvenv.cfg").write_text(
        pyvenvcfg_template.format(venv_dir=venv_dir, command=command), encoding="utf-8"
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
