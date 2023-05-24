import nox

CONSTRAINTS_FILE = "pinned-versions.txt"
PYTHON_DEFAULT = "3.9"
EXTRAS_TO_PIN = ("tests", )


@nox.session(python=PYTHON_DEFAULT)
def pin_dependencies(session: nox.Session) -> None:
    session.install("pip-tools")
    extras_str = ",".join(EXTRAS_TO_PIN)
    session.run(
        "pip-compile",
        "setup.cfg",
        "--extra",
        extras_str,
        "-o",
        "pinned-versions.txt"
    )


@nox.session(python=PYTHON_DEFAULT)
def test(session: nox.Session) -> None:
    session.install(".[tests]", "--constraint", CONSTRAINTS_FILE)
    session.run("pytest", "src")


@nox.session(python=PYTHON_DEFAULT)
def format_code(session: nox.Session) -> None:
    session.install("black", "isort")
    session.run("black", "-l", "120", ".")
    session.run("isort", ".")


@nox.session(python=PYTHON_DEFAULT)
def linting_check(session: nox.Session) -> None:
    session.install(".[linting]", "--constraint", CONSTRAINTS_FILE)
    session.run("pylint", "src")


@nox.session(python=PYTHON_DEFAULT)
def typing_check(session: nox.Session) -> None:
    session.install(".[typing]", "--constraint", CONSTRAINTS_FILE)
    session.run("mypy", "src")
