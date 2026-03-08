# plexport

Exports title information from a Plex media server to JSON or CSV.

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure the server connection

Create `plexport.toml` in the project directory (or `~/.config/plexport/config.toml`):

```toml
[server]
url = "http://192.168.x.x:32400"
token = "your-plex-token"
```

To find your Plex token: open Plex Web, browse to any item, click the `...` menu → Get Info → View XML. The token is the `X-Plex-Token` query parameter in the URL.

## Usage

```bash
uv run main.py [--format json|csv] [--type movies] [--type shows] [--config FILE]
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--format` | `json` | Output format: `json` or `csv` |
| `--type` | all | Filter by type: `movies` or `shows` (repeatable) |
| `--config` | `plexport.toml` | Path to config file |

### Examples

```bash
# Export everything as JSON
uv run main.py

# Export only movies as CSV
uv run main.py --type movies --format csv

# Export movies and TV shows separately
uv run main.py --type movies > movies.json
uv run main.py --type shows > shows.json
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

Movies and TV shows are each rendered as a flat table. TV show episodes are one row each with show, season, and episode columns repeated.
