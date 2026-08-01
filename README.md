# plexport

Exports title information from a Plex media server to JSON or CSV.

## Requirements

- [uv](https://docs.astral.sh/uv/) (installs Python 3.11+ and dependencies automatically)

## Setup

Configuration is two environment variables — for example with [direnv](https://direnv.net/), create a gitignored `.envrc`:

```bash
export PLEX_URL=http://192.168.x.x:32400
export PLEX_TOKEN=your-plex-token
```

To find your Plex token: open Plex Web, browse to any item, click the `...` menu → Get Info → View XML. The token is the `X-Plex-Token` query parameter in the URL.

## Usage

`plexport` is a self-contained [uv script](https://docs.astral.sh/uv/guides/scripts/) — no install step needed:

```bash
./plexport [--format json|csv] [--type movies] [--type shows]
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--format` | `json` | Output format: `json` or `csv` |
| `--type` | all | Filter by type: `movies` or `shows` (repeatable) |

Progress is reported on stderr, so it never mixes with redirected output. Library types other than movies and TV shows (music, photos) are skipped with a note.

### Examples

```bash
# Export everything as JSON
./plexport

# Export only movies as CSV
./plexport --type movies --format csv

# Export movies and TV shows separately
./plexport --type movies > movies.json
./plexport --type shows > shows.json

# Get all movie titles
./plexport --type movies | jq '.libraries[].movies[].title'

# Get all show titles
./plexport --type shows | jq '.libraries[].shows[].title'
```

## Output

### JSON

```json
{
  "server_name": "Synology",
  "version": "1.43.0.10492-121068a07",
  "libraries": [
    {
      "name": "Movies",
      "type": "movie",
      "movies": [
        { "title": "Foo", "year": 2026 }
      ]
    },
    {
      "name": "TV Shows",
      "type": "show",
      "shows": [
        {
          "title": "The Office",
          "year": 2005,
          "seasons": [
            {
              "title": "Season 1",
              "episodes": [
                { "title": "Pilot", "episode": 1 }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### CSV

One flat table with a single header row, loadable directly into Excel or pandas. Movies leave the season/episode columns empty; each episode is one row.

```csv
library,type,title,year,season,episode,episode_title
Movies,movie,Heat,1995,,,
TV Shows,show,The Office,2005,Season 1,1,Pilot
```

## Development

```bash
uv sync                 # install dependencies (including pytest)
uv run pytest           # run the tests
uvx pre-commit install  # set up git hooks (ruff lint + format, misc checks)
```

To change a dependency, edit `pyproject.toml` only. `plexport`'s PEP 723 header is generated from it by
`scripts/sync_script_header.py`, which runs on `main` after the change merges. To update the header in your own
commit instead, run `uv run python scripts/sync_script_header.py`.
