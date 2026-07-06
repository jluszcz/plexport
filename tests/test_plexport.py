import csv
import io
import json
from types import SimpleNamespace

import pytest

import plexport


def fake_episode(title, index, season_index, season_title):
    return SimpleNamespace(
        title=title, index=index, parentIndex=season_index, parentTitle=season_title
    )


class FakeShow:
    def __init__(self, title, year, episodes):
        self.title = title
        self.year = year
        self._episodes = episodes

    def episodes(self):
        return self._episodes


class FakeSection:
    def __init__(self, title, type, items=()):
        self.title = title
        self.type = type
        self._items = list(items)

    def all(self):
        return self._items


def fake_plex(*sections):
    return SimpleNamespace(
        friendlyName="TestServer",
        version="1.0",
        library=SimpleNamespace(sections=lambda: list(sections)),
    )


class TestResolveServer:
    @pytest.fixture(autouse=True)
    def clean_env(self, monkeypatch):
        monkeypatch.delenv("PLEX_URL", raising=False)
        monkeypatch.delenv("PLEX_TOKEN", raising=False)

    def test_from_env(self, monkeypatch):
        monkeypatch.setenv("PLEX_URL", "http://plex")
        monkeypatch.setenv("PLEX_TOKEN", "abc")

        assert plexport.resolve_server() == ("http://plex", "abc")

    def test_missing_token_exits(self, monkeypatch, capsys):
        monkeypatch.setenv("PLEX_URL", "http://plex")

        with pytest.raises(SystemExit):
            plexport.resolve_server()
        assert "PLEX_TOKEN" in capsys.readouterr().err

    def test_missing_url_exits(self, monkeypatch, capsys):
        monkeypatch.setenv("PLEX_TOKEN", "abc")

        with pytest.raises(SystemExit):
            plexport.resolve_server()
        assert "PLEX_URL" in capsys.readouterr().err

    def test_both_missing_reported_together(self, capsys):
        with pytest.raises(SystemExit):
            plexport.resolve_server()

        err = capsys.readouterr().err
        assert "PLEX_URL" in err
        assert "PLEX_TOKEN" in err


class TestGatherLibraryOverview:
    def test_movie_library(self):
        plex = fake_plex(
            FakeSection(
                "Movies",
                "movie",
                [SimpleNamespace(title="Heat", year=1995)],
            )
        )

        overview = plexport.gather_library_overview(plex)

        assert overview == {
            "server_name": "TestServer",
            "version": "1.0",
            "libraries": [
                {
                    "name": "Movies",
                    "type": "movie",
                    "movies": [{"title": "Heat", "year": 1995}],
                }
            ],
        }

    def test_show_episodes_grouped_into_sorted_seasons(self):
        show = FakeShow(
            "The Office",
            2005,
            [
                fake_episode("Gay Witch Hunt", 1, 3, "Season 3"),
                fake_episode("Pilot", 1, 1, "Season 1"),
                fake_episode("Diversity Day", 2, 1, "Season 1"),
            ],
        )
        plex = fake_plex(FakeSection("TV Shows", "show", [show]))

        overview = plexport.gather_library_overview(plex)

        assert overview["libraries"][0]["shows"] == [
            {
                "title": "The Office",
                "year": 2005,
                "seasons": [
                    {
                        "title": "Season 1",
                        "episodes": [
                            {"title": "Pilot", "episode": 1},
                            {"title": "Diversity Day", "episode": 2},
                        ],
                    },
                    {
                        "title": "Season 3",
                        "episodes": [{"title": "Gay Witch Hunt", "episode": 1}],
                    },
                ],
            }
        ]

    def test_unsupported_library_skipped_with_note(self, capsys):
        plex = fake_plex(FakeSection("Music", "artist"))

        overview = plexport.gather_library_overview(plex)

        assert overview["libraries"] == []
        assert "Music" in capsys.readouterr().err

    def test_type_filter(self):
        plex = fake_plex(
            FakeSection("Movies", "movie"),
            FakeSection("TV Shows", "show"),
        )

        overview = plexport.gather_library_overview(plex, types={"movie"})

        assert [lib["name"] for lib in overview["libraries"]] == ["Movies"]

    def test_progress_on_stderr(self, capsys):
        plexport.gather_library_overview(fake_plex(FakeSection("Movies", "movie")))

        assert "Movies" in capsys.readouterr().err


class TestOutput:
    OVERVIEW = {
        "server_name": "TestServer",
        "version": "1.0",
        "libraries": [
            {
                "name": "Movies",
                "type": "movie",
                "movies": [{"title": "Heat", "year": 1995}],
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
                                "episodes": [{"title": "Pilot", "episode": 1}],
                            }
                        ],
                    }
                ],
            },
        ],
    }

    def test_json_roundtrip(self, capsys):
        plexport.output_json(self.OVERVIEW)

        assert json.loads(capsys.readouterr().out) == self.OVERVIEW

    def test_csv_is_one_flat_table(self, capsys):
        plexport.output_csv(self.OVERVIEW)

        rows = list(csv.DictReader(io.StringIO(capsys.readouterr().out)))
        assert rows == [
            {
                "library": "Movies",
                "type": "movie",
                "title": "Heat",
                "year": "1995",
                "season": "",
                "episode": "",
                "episode_title": "",
            },
            {
                "library": "TV Shows",
                "type": "show",
                "title": "The Office",
                "year": "2005",
                "season": "Season 1",
                "episode": "1",
                "episode_title": "Pilot",
            },
        ]

    def test_csv_missing_year_is_blank(self, capsys):
        overview = {
            "server_name": "s",
            "version": "1",
            "libraries": [
                {
                    "name": "Movies",
                    "type": "movie",
                    "movies": [{"title": "Unknown", "year": None}],
                }
            ],
        }

        plexport.output_csv(overview)

        row = next(csv.DictReader(io.StringIO(capsys.readouterr().out)))
        assert row["year"] == ""
