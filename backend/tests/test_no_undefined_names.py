"""Static check: no undefined names, anywhere in the source.

WHY THIS EXISTS - AND IT IS THE SAME REASON, THREE TIMES
--------------------------------------------------------
    main.py       NameError: name 'schema_is_current' is not defined
    main.py       NameError: name 'logger' is not defined
    ingestion.py  NameError: name 'logger' is not defined
    detection.py  NameError: name 'y_true' is not defined

Every one of them sat on a code path the test suite never executed - a lifespan
handler, a warning branch, a reporting block that only fires when a particular table
is populated. Every one of them passed `python -c "import ast; ast.parse(...)"`,
because a NameError is not a syntax error: the code is perfectly well-formed, it
simply refers to something that does not exist.

And every one of them detonated on the first real run, on the user's machine, in
front of the user.

A test suite covers the paths it covers. This covers the ones it does not: pyflakes
resolves every name against its enclosing scope, whether the line ever runs or not.
It takes under a second and it would have caught all four.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

TARGETS = [
    ROOT / "backend" / "app",
    ROOT / "scripts",
    ROOT / "migrations",
]


def test_there_are_no_undefined_names() -> None:
    """A NameError on a rarely-taken branch is a bug that ships.

    It is not caught by the type checker, not caught by the parser, and not caught by
    a test suite that never walks that branch. It is caught here.
    """
    pyflakes = pytest.importorskip("pyflakes")  # noqa: F841

    files = [
        str(p)
        for target in TARGETS
        if target.exists()
        for p in target.rglob("*.py")
        if "__pycache__" not in str(p)
    ]
    assert files, "no source files found - check the paths"

    result = subprocess.run(
        [sys.executable, "-m", "pyflakes", *files],
        capture_output=True,
        text=True,
    )

    undefined = [
        line
        for line in result.stdout.splitlines()
        if "undefined name" in line
    ]

    assert not undefined, (
        "UNDEFINED NAMES - these are NameErrors waiting for the right branch:\n\n"
        + "\n".join(f"    {u}" for u in undefined)
        + "\n\nThe code parses. The tests pass. It will still crash the first time "
          "that line executes, which is usually on somebody else's machine."
    )