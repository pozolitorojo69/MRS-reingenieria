import logging

import requests

from config.config import Config

logger = logging.getLogger(__name__)


class TMDBClient:
    def __init__(self, api_key=None, base_url=None, timeout=None):
        self.api_key = api_key or Config.TMDB_API_KEY
        self.base_url = base_url or Config.TMDB_BASE_URL
        self.timeout = timeout or Config.TMDB_TIMEOUT_SECONDS

    def _get(self, path, **params):
        params['api_key'] = self.api_key
        params.setdefault('language', 'en-US')
        url = f"{self.base_url}{path}"
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            logger.exception("Fallo al llamar a TMDB: %s", path)
            return None

    def get_movie(self, movie_id):
        return self._get(f"/movie/{movie_id}")

    def search_movies(self, query):
        data = self._get("/search/movie", query=query, page=1, include_adult="false")
        return data.get('results', []) if data else []

    def get_movie_recommendations(self, movie_id, n):
        data = self._get(f"/movie/{movie_id}/recommendations", page=1)
        return data.get('results', [])[:n] if data else []


tmdb_client = TMDBClient()