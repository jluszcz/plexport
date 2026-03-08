import argparse
import csv
import json
import sys
import tomllib
from pathlib import Path

from plexapi.server import PlexServer


CONFIG_PATHS = [
    Path("plexport.toml"),
    Path.home() / ".config" / "plexport" / "config.toml",
]


def load_config(path: Path | None) -> dict:
    if path:
        candidates = [path]
    else:
        candidates = CONFIG_PATHS

    for candidate in candidates:
        if candidate.exists():
            with open(candidate, "rb") as f:
                return tomllib.load(f)

    print(
        "No config file found. Create plexport.toml with:\n\n"
        "[server]\n"
        'url = "http://<your-synology-ip>:32400"\n'
        'token = "<your-plex-token>"\n',
        file=sys.stderr,
    )
    sys.exit(1)


def gather_library_overview(plex: PlexServer, types: set[str] | None = None) -> dict:
    overview = {
        "server_name": plex.friendlyName,
        "version": plex.version,
        "libraries": [],
    }

    for section in plex.library.sections():
        if types and section.type not in types:
            continue
        lib: dict = {
            "name": section.title,
            "type": section.type,
        }

        if section.type == "movie":
            lib["movies"] = [
                {"title": movie.title, "year": movie.year} for movie in section.all()
            ]

        elif section.type == "show":
            lib["shows"] = [
                {
                    "title": show.title,
                    "year": show.year,
                    "seasons": [
                        {
                            "title": season.title,
                            "episodes": [
                                {"title": episode.title, "episode": episode.index}
                                for episode in season.episodes()
                            ],
                        }
                        for season in show.seasons()
                    ],
                }
                for show in section.all()
            ]

        overview["libraries"].append(lib)

    return overview


def output_json(data: dict) -> None:
    print(json.dumps(data, indent=2))


def output_csv(data: dict) -> None:
    writer = csv.writer(sys.stdout)
    writer.writerow(["server_name", data["server_name"]])
    writer.writerow(["version", data["version"]])

    for lib in data["libraries"]:
        writer.writerow([])
        writer.writerow([f"=== {lib['name']} ({lib['type']}) ==="])

        if lib["type"] == "movie":
            writer.writerow(["title", "year"])
            for movie in lib.get("movies", []):
                writer.writerow([movie["title"], movie.get("year", "")])

        elif lib["type"] == "show":
            writer.writerow(
                ["show", "year", "season", "episode_number", "episode_title"]
            )
            for show in lib.get("shows", []):
                for season in show.get("seasons", []):
                    for ep in season.get("episodes", []):
                        writer.writerow(
                            [
                                show["title"],
                                show.get("year", ""),
                                season["title"],
                                ep.get("episode", ""),
                                ep["title"],
                            ]
                        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export statistics from your Plex library."
    )
    parser.add_argument(
        "--config",
        type=Path,
        metavar="FILE",
        help="Path to config file (default: plexport.toml or ~/.config/plexport/config.toml)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--type",
        choices=["movies", "shows"],
        dest="types",
        action="append",
        metavar="TYPE",
        help="Filter by library type: movies, shows (can be specified multiple times)",
    )
    args = parser.parse_args()

    config = load_config(args.config)

    try:
        server_cfg = config["server"]
        url = server_cfg["url"]
        token = server_cfg["token"]
    except KeyError as e:
        print(f"Config missing key: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        plex = PlexServer(url, token)
    except Exception as e:
        print(f"Failed to connect to Plex server: {e}", file=sys.stderr)
        sys.exit(1)

    type_map = {"movies": "movie", "shows": "show"}
    types = {type_map[t] for t in args.types} if args.types else None
    data = gather_library_overview(plex, types)

    if args.format == "csv":
        output_csv(data)
    else:
        output_json(data)


if __name__ == "__main__":
    main()
