from app.models.movie import Movie


def test_movie_creation():
    movie = Movie(id=1, title="Inception", genres="Action,Sci-Fi", rating=8.8)
    assert movie.id == 1
    assert movie.title == "Inception"
    assert movie.genres == "Action,Sci-Fi"
    assert movie.rating == 8.8


def test_get_all_returns_every_movie(app):
    movies = Movie.get_all()
    assert len(movies) == 5


def test_get_movies_by_genre_filters_correctly(app):
    movies = Movie.get_movies_by_genre("Drama")
    titles = {m.title for m in movies}
    assert "The Shawshank Redemption" in titles
    assert "Superbad" not in titles


def test_get_movie_details_found(app):
    movie = Movie.get_movie_details(1)
    assert movie is not None
    assert movie.title == "The Shawshank Redemption"


def test_get_movie_details_not_found(app):
    movie = Movie.get_movie_details(999)
    assert movie is None


def test_get_movies_by_title_partial_match(app):
    movies = Movie.get_movies_by_title("Dark")
    assert len(movies) == 1
    assert movies[0].title == "The Dark Knight"