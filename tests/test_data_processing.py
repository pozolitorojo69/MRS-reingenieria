import os
import csv
import tempfile

import pytest

from config.config import Config
from app.data_processing import demographic_filtering as demo
from app.data_processing import content_based_filtering as content


MOVIES_ROWS = [
    {
        "id": "1", "title": "Space Warriors", "overview": "Brave astronauts fight aliens in deep space.",
        "genres": "[{'id': 1, 'name': 'Action'}, {'id': 2, 'name': 'Sci-Fi'}]",
        "keywords": "[{'id': 10, 'name': 'space'}, {'id': 11, 'name': 'war'}]",
        "vote_count": "1000", "vote_average": "8.1",
    },
    {
        "id": "2", "title": "Love in Paris", "overview": "Two strangers fall in love in the streets of Paris.",
        "genres": "[{'id': 3, 'name': 'Romance'}]",
        "keywords": "[{'id': 12, 'name': 'love'}, {'id': 13, 'name': 'paris'}]",
        "vote_count": "500", "vote_average": "7.0",
    },
    {
        "id": "3", "title": "Galaxy Defenders", "overview": "A team of astronauts defends earth from an alien invasion.",
        "genres": "[{'id': 1, 'name': 'Action'}, {'id': 2, 'name': 'Sci-Fi'}]",
        "keywords": "[{'id': 10, 'name': 'space'}, {'id': 14, 'name': 'alien'}]",
        "vote_count": "1200", "vote_average": "8.5",
    },
    {
        "id": "4", "title": "Quiet Nights", "overview": "A romantic comedy about second chances.",
        "genres": "[{'id': 3, 'name': 'Romance'}, {'id': 4, 'name': 'Comedy'}]",
        "keywords": "[{'id': 12, 'name': 'love'}, {'id': 15, 'name': 'comedy'}]",
        "vote_count": "300", "vote_average": "6.5",
    },
]

CREDITS_ROWS = [
    {"id": "1", "cast": "[{'name': 'Actor A'}, {'name': 'Actor B'}]",
     "crew": "[{'job': 'Director', 'name': 'Director X'}]"},
    {"id": "2", "cast": "[{'name': 'Actor C'}]",
     "crew": "[{'job': 'Director', 'name': 'Director Y'}]"},
    {"id": "3", "cast": "[{'name': 'Actor A'}, {'name': 'Actor D'}]",
     "crew": "[{'job': 'Director', 'name': 'Director X'}]"},
    {"id": "4", "cast": "[{'name': 'Actor C'}]",
     "crew": "[{'job': 'Director', 'name': 'Director Y'}]"},
]


@pytest.fixture
def synthetic_csvs(monkeypatch):
    tmpdir = tempfile.mkdtemp()
    movies_path = os.path.join(tmpdir, "movies.csv")
    credits_path = os.path.join(tmpdir, "credits.csv")

    with open(movies_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(MOVIES_ROWS[0].keys()))
        writer.writeheader()
        writer.writerows(MOVIES_ROWS)

    with open(credits_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(CREDITS_ROWS[0].keys()))
        writer.writeheader()
        writer.writerows(CREDITS_ROWS)

    monkeypatch.setattr(Config, "MOVIES_METADATA_PATH", movies_path)
    monkeypatch.setattr(Config, "CREDITS_PATH", credits_path)
    demo.load_and_process_data.cache_clear()


def test_load_and_process_data_ranks_by_weighted_rating(synthetic_csvs):
    result = demo.load_and_process_data()
    assert "score" in result.columns
    assert len(result) >= 1


def test_get_top_movies_respects_n(synthetic_csvs):
    top = demo.get_top_movies(2)
    assert len(top) <= 2


def test_prepare_content_based_data_and_get_recommendations(synthetic_csvs):
    df, cosine_sim, indices = content.prepare_content_based_data()
    recs = content.get_recommendations("Space Warriors", df, cosine_sim, indices)
    assert "Space Warriors" not in recs.values
    assert "Galaxy Defenders" in recs.values


def test_get_recommendations_unknown_title_returns_empty_series(synthetic_csvs):
    df, cosine_sim, indices = content.prepare_content_based_data()
    recs = content.get_recommendations("Nonexistent Movie XYZ", df, cosine_sim, indices)
    assert recs.empty