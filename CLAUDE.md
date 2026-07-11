# Development Guidelines

## Before Committing

The `CI` GitHub workflow's `lint` and `test` jobs must pass before committing a change. Run them locally first:

```sh
uvx pre-commit run --all-files --show-diff-on-failure
uv run pytest
```

Do not commit if either command fails.
