import pytest

from app import create_app
from config.config import TestingConfig, Config
from app.utils.database import get_db


@pytest.fixture
def app(monkeypatch):
    # get_db() usa Config.DATABASE_PATH directamente (no app.config),
    # así que hay que parcharlo aquí para que las pruebas usen una
    # base de datos en memoria y no la real.
    monkeypatch.setattr(Config, "DATABASE_PATH", ":memory:")

    flask_app = create_app(TestingConfig)
    flask_app.config['TESTING'] = True

    with flask_app.app_context():
        db = get_db()
        db.execute(
            "CREATE TABLE movies (id INTEGER PRIMARY KEY, title TEXT NOT NULL, "
            "genres TEXT NOT NULL, vote_average REAL)"
        )
        db.executemany(
            "INSERT INTO movies (id, title, genres, vote_average) VALUES (?, ?, ?, ?)",
            [
                (1, "The Shawshank Redemption", "Drama", 9.3),
                (2, "The Dark Knight", "Action,Crime,Drama", 9.0),
                (3, "Inception", "Action,Sci-Fi", 8.8),
                (4, "The Notebook", "Romance,Drama", 7.8),
                (5, "Superbad", "Comedy", 7.6),
            ],
        )
        db.commit()
        yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()