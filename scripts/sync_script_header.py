"""Regenerate plexport's PEP 723 header from pyproject.toml.

Dependabot only watches pyproject.toml and uv.lock, so the header — the copy
users actually execute via `uv run ./plexport` — is generated rather than
hand-maintained. A pre-commit hook runs this locally; the Sync Script Header
workflow runs it on main after Dependabot's PRs merge.

Exit codes follow the pre-commit convention: 0 when already in sync, 1 when the
header was rewritten, 2 on error.
"""

import re
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "plexport"
PYPROJECT = REPO_ROOT / "pyproject.toml"

# PEP 723: a `# /// script` block of commented TOML, ended by `# ///`.
BLOCK = re.compile(r"^# /// script$\n(?P<body>(^#(| .*)$\n)+)^# ///$", re.MULTILINE)


def parse_block(text):
    """Return the script block's TOML as a dict, or None if there is no block."""
    match = BLOCK.search(text)
    if match is None:
        return None
    toml = "".join(
        line.removeprefix("#").removeprefix(" ") + "\n"
        for line in match.group("body").splitlines()
    )
    return tomllib.loads(toml)


def render_block(project):
    """Render a PEP 723 block from pyproject.toml's [project] table."""
    return "\n".join(
        [
            "# /// script",
            f'# requires-python = "{project["requires-python"]}"',
            "# dependencies = [",
            *(f'#     "{dependency}",' for dependency in project["dependencies"]),
            "# ]",
            "# ///",
        ]
    )


def main():
    project = tomllib.loads(PYPROJECT.read_text())["project"]
    text = SCRIPT.read_text()

    if BLOCK.search(text) is None:
        print(f"{SCRIPT.name} is missing its PEP 723 script block", file=sys.stderr)
        return 2

    # A lambda replacement keeps backslashes in version specifiers literal.
    updated = BLOCK.sub(lambda _: render_block(project), text, count=1)
    if updated == text:
        return 0

    SCRIPT.write_text(updated)
    print(f"Rewrote {SCRIPT.name}'s script block from {PYPROJECT.name}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
