"""The PEP 723 header is what `uv run ./plexport` installs from.

scripts/sync_script_header.py generates the header from pyproject.toml, but that
sync lands on main *after* a Dependabot PR merges. These tests therefore assert
compatibility rather than equality: demanding the two files match byte-for-byte
would make every Dependabot PR unmergeable and stall the sync that fixes it.
"""

import tomllib
from importlib.metadata import version

import pytest
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

from sync_script_header import PYPROJECT, SCRIPT, parse_block


def script_metadata():
    metadata = parse_block(SCRIPT.read_text())
    assert metadata, "plexport is missing its PEP 723 script block"
    return metadata


def project_metadata():
    return tomllib.loads(PYPROJECT.read_text())["project"]


def names(dependencies):
    return {canonicalize_name(Requirement(d).name) for d in dependencies}


def test_dependency_names_match_pyproject():
    """A dependency added to one declaration but not the other is real drift."""
    assert names(script_metadata()["dependencies"]) == names(
        project_metadata()["dependencies"]
    )


@pytest.mark.parametrize("dependency", script_metadata()["dependencies"])
def test_installed_version_satisfies_script_requirement(dependency):
    """CI must exercise plexport against versions its header actually permits."""
    requirement = Requirement(dependency)
    installed = version(requirement.name)
    assert requirement.specifier.contains(installed), (
        f"{requirement.name} {installed} is installed, but plexport's header "
        f"requires {requirement.specifier}"
    )


def test_requires_python_matches_pyproject():
    """Dependabot never edits requires-python, so it can be held to equality."""
    assert script_metadata()["requires-python"] == project_metadata()["requires-python"]
