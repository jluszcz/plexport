"""Regenerate plexport's PEP 723 header from pyproject.toml.

Dependabot only watches pyproject.toml and uv.lock, so the header — the copy
users actually execute via `uv run ./plexport` — is generated rather than
hand-maintained. The Sync Script Header workflow runs this on main once a
dependency change merges. Run it by hand to update the header sooner.

Deliberately not a pre-commit hook: CI runs `pre-commit run --all-files`, so it
would become a required check, and on a Dependabot PR the header is *expected*
to be stale until the post-merge sync lands.

Exit codes: 0 when already in sync, 1 when the header was rewritten, 2 on error.
"""

import re
import sys
import tomllib
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "plexport"
PYPROJECT = REPO_ROOT / "pyproject.toml"

REQUIRED_KEYS = ("requires-python", "dependencies")

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


def main(pyproject=PYPROJECT, script=SCRIPT):
    project = tomllib.loads(pyproject.read_text()).get("project", {})
    missing = [key for key in REQUIRED_KEYS if key not in project]
    if missing:
        print(
            f"{pyproject.name} has no [project] {' or '.join(missing)}",
            file=sys.stderr,
        )
        return 2

    text = script.read_text()
    if BLOCK.search(text) is None:
        print(f"{script.name} is missing its PEP 723 script block", file=sys.stderr)
        return 2

    # A lambda replacement keeps backslashes in version specifiers literal.
    updated = BLOCK.sub(lambda _: render_block(project), text, count=1)
    if updated == text:
        return 0

    script.write_text(updated)
    print(f"Rewrote {script.name}'s script block from {pyproject.name}")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Exit 1 means "rewrote the header" to both callers, so an unhandled
        # crash must not borrow it.
        traceback.print_exc()
        sys.exit(2)
