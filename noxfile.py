import nox  # type: ignore


@nox.session(python=["3.7", "3.8", "3.9", "3.10", "3.11"])
def test(session):
    session.install("pytest")  # XXX: get from pyproject.toml
    session.run("pytest")


@nox.session
def lint(session):
    session.install("black", "ruff")  # XXX: get from pyproject.toml
    session.run("ruff", "check", ".")
    session.run("black", "--check", ".")
