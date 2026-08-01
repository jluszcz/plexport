"""The sync script's exit codes are a contract, not a detail.

Both callers branch on them: the pre-commit hook reads non-zero as "the header
moved", and the workflow maps 1 to "commit and push" but 2 to "fail the job".
"""

import pytest

from sync_script_header import main

SCRIPT = """#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests>=2.0.0",
# ]
# ///
import requests
"""

PYPROJECT = """[project]
requires-python = ">=3.11"
dependencies = ["requests>=2.0.0"]
"""


@pytest.fixture
def paths(tmp_path):
    script = tmp_path / "plexport"
    script.write_text(SCRIPT)
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(PYPROJECT)
    return pyproject, script


def test_returns_0_when_already_in_sync(paths):
    assert main(*paths) == 0


def test_returns_1_when_the_header_is_rewritten(paths):
    pyproject, script = paths
    pyproject.write_text(PYPROJECT.replace("2.0.0", "2.1.0"))
    assert main(pyproject, script) == 1


def test_rewritten_header_picks_up_the_new_specifier(paths):
    pyproject, script = paths
    pyproject.write_text(PYPROJECT.replace("2.0.0", "2.1.0"))
    main(pyproject, script)
    assert '#     "requests>=2.1.0",' in script.read_text()


def test_rewriting_leaves_the_rest_of_the_script_intact(paths):
    pyproject, script = paths
    pyproject.write_text(PYPROJECT.replace("2.0.0", "2.1.0"))
    main(pyproject, script)
    assert script.read_text().endswith("# ///\nimport requests\n")


def test_returns_2_when_pyproject_declares_no_dependencies(paths):
    pyproject, script = paths
    pyproject.write_text('[project]\nrequires-python = ">=3.11"\n')
    assert main(pyproject, script) == 2


def test_returns_2_when_the_script_has_no_pep_723_block(paths):
    pyproject, script = paths
    script.write_text("import requests\n")
    assert main(pyproject, script) == 2
