# Development Guidelines

## Before Committing

The `CI` GitHub workflow's `Test` and `Lint` steps must pass before committing a change. Run them locally first:

```sh
uv run pre-commit run --all-files --show-diff-on-failure
uv run pytest
```

Do not commit if either command fails.

## Dependencies

`plexport` is a PEP 723 single-file script — its `# /// script` header is what `uv run ./plexport` installs from, and
it is a **separate declaration** from `pyproject.toml`. Dependabot only watches `pyproject.toml` and `uv.lock`, so
the header is the copy that silently goes stale, and it is the one users execute.

Change a dependency in both places. `tests/test_script_metadata.py` asserts they agree, so forgetting fails the build
rather than shipping a script that installs a version nobody tested.
