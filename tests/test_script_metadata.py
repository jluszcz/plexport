"""The PEP 723 header is what `uv run ./plexport` installs from.

Dependabot only watches pyproject.toml and uv.lock, so the header — the part
users actually execute — is unmaintained unless something checks it.
"""

import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "plexport"
PYPROJECT = REPO_ROOT / "pyproject.toml"

# PEP 723: a `# /// script` block of commented TOML, ended by `# ///`.
BLOCK = re.compile(r"^# /// script$\n(?P<body>(^#(| .*)$\n)+)^# ///$", re.MULTILINE)


def script_metadata():
    match = BLOCK.search(SCRIPT.read_text())
    assert match, "plexport is missing its PEP 723 script block"
    toml = "".join(
        line.removeprefix("#").removeprefix(" ") + "\n"
        for line in match.group("body").splitlines()
    )
    return tomllib.loads(toml)


def project_metadata():
    return tomllib.loads(PYPROJECT.read_text())["project"]


def test_dependencies_match_pyproject():
    assert sorted(script_metadata()["dependencies"]) == sorted(
        project_metadata()["dependencies"]
    )


def test_requires_python_matches_pyproject():
    assert script_metadata()["requires-python"] == project_metadata()["requires-python"]
