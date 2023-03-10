import os
import pathlib
import sys
import sysconfig

_BASE_EXECUTABLE = pathlib.Path(getattr(sys, "_base_executable", sys.executable))

_PYVENVCFG_TEMPLATE = f"""home = {_BASE_EXECUTABLE.parent}
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
def create(env_dir=".venv"):
    """Create a minimal virtual environment."""
    env_path = pathlib.Path(env_dir)
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
        (env_path / "lib64").symlink_to("lib", target_is_directory=True)

    for executable_name in (
        "python",
        f"python{sys.version_info.major}",
        f"python{sys.version_info.major}.{sys.version_info.minor}",
    ):
        (scripts_dir / executable_name).symlink_to(_BASE_EXECUTABLE)

    try:
        module_path = pathlib.Path(__file__).resolve()
    except NameError:
        command = f"{sys.executable} -c '...'"
    else:
        command = f"{sys.executable} {module_path} {env_path.resolve()}"
    (env_path / "pyvenv.cfg").write_text(
        _PYVENVCFG_TEMPLATE.format(command=command),
        encoding="utf-8",
    )


if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage: microvenv.py [env_dir='.venv']", file=sys.stderr)
        sys.exit(1)
    try:
        env_dir = sys.argv[1]
    except IndexError:
        env_dir = ".venv"

    create(env_dir)
