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

**Edit `pyproject.toml` only.** The `Sync Script Header` workflow regenerates the header on `main` via
`scripts/sync_script_header.py` once the change merges. Run it by hand with
`uv run python scripts/sync_script_header.py` if you want the header updated in your own commit.

A stale header on a PR is expected, not a defect — it stays stale until the post-merge sync lands. Nothing that
runs in CI may reject that state, which is why:

- `tests/test_script_metadata.py` checks *compatibility*, not equality: dependency names must match and the installed
  version must satisfy the header's specifier.
- there is **no pre-commit hook** for the sync. CI runs `pre-commit run --all-files`, so such a hook would be a
  required check that fails every Dependabot PR.
