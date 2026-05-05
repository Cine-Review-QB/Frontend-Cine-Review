"""Estado da página /genre/[name] — listagem paginada por gênero."""

from __future__ import annotations

import logging
from urllib.parse import unquote

import reflex as rx

from cine_review.api import fetch_movies_by_genre
from cine_review.state.auth_state import AuthState
from cine_review.state.movie_state import Movie, _to_movie

logger = logging.getLogger(__name__)

PAGE_SIZE = 30


class GenreState(rx.State):
    movies: list[Movie] = []
    total: int = 0
    page: int = 1
    is_loading: bool = False
    error: str = ""

    @rx.var
    def genre_from_url(self) -> str:
        path = self.router.url.path or ""
        parts = path.strip("/").split("/")
        if len(parts) >= 2 and parts[0] == "genre":
            # /genre/Science%20Fiction → "Science Fiction"
            return unquote(parts[1])
        return ""

    @rx.var
    def total_pages(self) -> int:
        if self.total <= 0:
            return 1
        return (self.total + PAGE_SIZE - 1) // PAGE_SIZE

    @rx.var
    def has_prev(self) -> bool:
        return self.page > 1

    @rx.var
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @rx.var
    def page_label(self) -> str:
        return f"Página {self.page} de {self.total_pages}"

    @rx.var
    def has_movies(self) -> bool:
        return len(self.movies) > 0

    @rx.event
    async def load_genre(self):
        genre = self.genre_from_url
        if not genre:
            self.error = "Gênero inválido"
            return

        self.page = 1
        await self._fetch_page()

    @rx.event
    async def next_page(self):
        if self.has_next:
            self.page += 1
            await self._fetch_page()

    @rx.event
    async def prev_page(self):
        if self.has_prev:
            self.page -= 1
            await self._fetch_page()

    async def _fetch_page(self):
        genre = self.genre_from_url
        if not genre:
            return

        self.is_loading = True
        self.error = ""
        auth = await self.get_state(AuthState)

        try:
            payload = await fetch_movies_by_genre(
                genre=genre,
                limit=PAGE_SIZE,
                skip=(self.page - 1) * PAGE_SIZE,
                token=auth.access_token,
            )
            self.total = int(payload.get("total") or 0)
            raw = payload.get("movies") or []
            self.movies = [_to_movie(d) for d in raw if d.get("poster_url")]
        except Exception as e:
            self.error = f"Falha ao carregar: {e}"
            self.movies = []
        finally:
            self.is_loading = False
