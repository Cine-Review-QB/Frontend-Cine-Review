"""Estado da página de busca de filmes."""

from __future__ import annotations

import logging

import reflex as rx

from cine_review.api import search_movies
from cine_review.state.auth_state import AuthState
from cine_review.state.movie_state import Movie, _to_movie

logger = logging.getLogger(__name__)


class SearchState(rx.State):
    query: str = ""
    results: list[Movie] = []
    is_searching: bool = False
    has_searched: bool = False
    error: str = ""

    @rx.var
    def has_results(self) -> bool:
        return len(self.results) > 0

    @rx.event
    def set_query(self, value: str):
        self.query = value[:200]

    @rx.event
    async def submit_search(self, form_data: dict | None = None):
        # form_data vem do on_submit do form (Enter); ignorado pois a
        # query já está em state via on_change.
        q = self.query.strip()
        if not q:
            return
        self.is_searching = True
        self.has_searched = True
        self.error = ""

        auth = await self.get_state(AuthState)
        try:
            raw = await search_movies(q, limit=30, token=auth.access_token)
            self.results = [_to_movie(d) for d in raw if d.get("poster_url")]
        except Exception as e:
            self.error = f"Falha na busca: {e}"
            self.results = []
        finally:
            self.is_searching = False
