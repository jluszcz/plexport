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
the header is the copy that would silently go stale, and it is the one users execute.

**Edit `pyproject.toml` only.** `scripts/sync_script_header.py` generates the header from it, driven by a pre-commit
hook locally and by the `Sync Script Header` workflow on `main` after Dependabot's PRs merge.

`tests/test_script_metadata.py` checks *compatibility*, not equality: dependency names must match, and the installed
version must satisfy the header's specifier. Equality would make every Dependabot PR unmergeable and stall the
post-merge sync that fixes it, so the header is allowed to trail `pyproject.toml` until that sync lands.
