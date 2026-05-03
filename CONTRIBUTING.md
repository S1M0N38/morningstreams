# Contributing

## Setup

```bash
uv sync --group dev
```

## Quality checks

```bash
uv run ruff check .        # lint
uv run ruff format .       # format
uv run ty check            # type check
```

## Install locally

```bash
uv tool install -e .
```

## Commits

Use [conventional commits](https://www.conventionalcommits.org/):

```
fix(engine): handle stale docker containers
feat(cli): add --timeout flag
docs: update installation instructions
```

## Branches

- **`dev`** — active development, PRs target this branch
- **`main`** — releases only, managed by [release-please](https://github.com/googleapis/release-please). Do not push directly.
