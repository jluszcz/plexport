# Development Guidelines

## Before Committing

The `CI` GitHub workflow's `Test` and `Lint` steps must pass before committing a change. Run them locally first:

```sh
uvx pre-commit run --all-files --show-diff-on-failure
uv run pytest
```

Do not commit if either command fails.
