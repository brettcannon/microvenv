import os
import pathlib
import sys
import sysconfig

PYVENVCFG_TEMPLATE = f"""home = {{base_executable_parent}}
include-system-site-packages = false
version = {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}
executable = {{resolved_base_executable}}
command = {{command}}
"""


def _sysconfig_path(name, venv_dir):
    variables = {
        "base": venv_dir,
        "platbase": venv_dir,
        "installed_base": venv_dir,
        "installed_platbase": venv_dir,
    }

    return pathlib.Path(sysconfig.get_path(name, "venv", variables))


def create(venv_dir):
    base_executable = pathlib.Path(getattr(sys, "_base_executable", sys.executable))

    try:
        scripts_dir = _sysconfig_path("scripts", venv_dir)
        include_dir = _sysconfig_path("include", venv_dir)
        purelib_dir = _sysconfig_path("purelib", venv_dir)
    except KeyError:
        scripts_dir = venv_dir / "bin"
        include_dir = venv_dir / "include"
        purelib_dir = (
            venv_dir
            / "lib"
            / f"python{sys.version_info.major}.{sys.version_info.minor}"
            / "site-packages"
        )
    for dir in (scripts_dir, include_dir, purelib_dir):
        dir.mkdir(parents=True)

    if sys.maxsize > 2**32 and os.name == "posix" and sys.platform != "darwin":
        (venv_dir / "lib64").symlink_to("lib", target_is_directory=True)

    for executable_name in (
        "python",
        f"python{sys.version_info.major}",
        f"python{sys.version_info.major}.{sys.version_info.minor}",
    ):
        (scripts_dir / executable_name).symlink_to(base_executable)

    try:
        module_path = pathlib.Path(__file__).resolve()
    except NameError:
        command = f"{sys.executable} -c '...'"
    else:
        command = f"{sys.executable} {module_path} {venv_dir.resolve()}"
    (venv_dir / "pyvenv.cfg").write_text(
        PYVENVCFG_TEMPLATE.format(
            base_executable_parent=base_executable.parent,
            resolved_base_executable=base_executable.resolve(),
            command=command,
        ),
        encoding="utf-8",
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
