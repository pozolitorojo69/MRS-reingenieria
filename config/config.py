import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    DATA_DIR = os.path.join(BASE_DIR, 'data')
    DATABASE_PATH = os.path.join(DATA_DIR, 'movies.db')
    MOVIES_METADATA_PATH = os.path.join(DATA_DIR, 'tmdb_5000_movies.csv')
    CREDITS_PATH = os.path.join(DATA_DIR, 'tmdb_5000_credits.csv')

    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')

    TMDB_API_KEY = os.environ.get('TMDB_API_KEY')
    TMDB_BASE_URL = os.environ.get('TMDB_BASE_URL', 'https://api.themoviedb.org/3')
    TMDB_TIMEOUT_SECONDS = int(os.environ.get('TMDB_TIMEOUT_SECONDS', 5))

    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DATABASE_PATH = ':memory:'


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}


def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)