import os
import pathlib

import nox  # type: ignore


@nox.session(python=["3.7", "3.8", "3.9", "3.10", "3.11", "3.12"])
def test(session):
    session.install(".[test]")
    session.run("pytest")


@nox.session
def lint(session):
    session.install(".[lint]")
    session.run("ruff", "check", ".")
    session.run("black", "--check", ".")
    session.run("mypy", ".")
    session.run("stubtest", "microvenv")


@nox.session
def docs(session):
    docs_path = pathlib.Path("docs")
    session.install(".[doc]")
    session.debug("Recording `microvenv --help`")
    out = session.run("python", "-m", "microvenv", "--help", silent=True)
    with open(docs_path / "help.txt", "w", encoding="utf-8") as file:
        file.write(out.strip())
    session.run(
        "sphinx-build",
        "-j",
        "auto",
        "-W",
        os.fsdecode(docs_path),
        os.fsdecode(docs_path / "_build"),
    )
