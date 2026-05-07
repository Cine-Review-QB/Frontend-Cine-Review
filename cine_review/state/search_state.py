"""Estado da pagina de busca: filmes e usuarios."""

from __future__ import annotations

import logging
import unicodedata
from dataclasses import dataclass

import reflex as rx

from cine_review.api import fetch_users, search_movies
from cine_review.state.auth_state import AuthState
from cine_review.state.movie_state import Movie, _to_movie

logger = logging.getLogger(__name__)


def _norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return value.casefold()


@dataclass
class SearchUser:
    id: str = ""
    auth0_id: str = ""
    username: str = ""
    bio: str = ""
    avatar_url: str = ""
    review_count: int = 0
    has_avatar: bool = False
    has_bio: bool = False


def _to_search_user(data: dict) -> SearchUser:
    avatar = data.get("avatarUrl") or ""
    bio = data.get("bio") or ""
    return SearchUser(
        id=str(data.get("id") or ""),
        auth0_id=data.get("auth0Id") or "",
        username=data.get("username") or "",
        bio=bio,
        avatar_url=avatar,
        review_count=int(data.get("reviewCount") or 0),
        has_avatar=bool(avatar),
        has_bio=bool(bio),
    )


class SearchState(rx.State):
    active_tab: str = "movies"
    query: str = ""
    results: list[Movie] = []
    user_results: list[SearchUser] = []
    is_searching: bool = False
    has_searched: bool = False
    error: str = ""

    @rx.var
    def has_results(self) -> bool:
        return len(self.results) > 0

    @rx.var
    def has_user_results(self) -> bool:
        return len(self.user_results) > 0

    @rx.var
    def is_movie_tab(self) -> bool:
        return self.active_tab == "movies"

    @rx.var
    def is_social_tab(self) -> bool:
        return self.active_tab == "users"

    async def _run_search(self):
        q = self.query.strip()
        self.error = ""

        if len(q) < 2:
            self.results = []
            self.user_results = []
            self.is_searching = False
            self.has_searched = False
            return

        self.is_searching = True
        self.has_searched = True

        auth = await self.get_state(AuthState)
        try:
            if self.active_tab == "users":
                if not auth.access_token:
                    self.error = "Faca login para buscar usuarios."
                    self.user_results = []
                    return
                raw_users = await fetch_users(auth.access_token, q)
                needle = _norm(q)
                users = []
                for item in raw_users:
                    haystack = _norm(
                        f"{item.get('username') or ''} {item.get('bio') or ''}"
                    )
                    if needle in haystack:
                        users.append(_to_search_user(item))
                self.user_results = users[:30]
                return

            raw = await search_movies(q, limit=30, token=auth.access_token)
            self.results = [_to_movie(d) for d in raw if d.get("poster_url")]
        except Exception as e:
            logger.warning("Falha na busca: %s", e)
            self.error = f"Falha na busca: {e}"
            if self.active_tab == "users":
                self.user_results = []
            else:
                self.results = []
        finally:
            self.is_searching = False

    @rx.event
    async def set_tab(self, tab: str):
        self.active_tab = tab
        self.results = []
        self.user_results = []
        await self._run_search()

    @rx.event
    async def set_query(self, value: str):
        self.query = value[:200]
        await self._run_search()

    @rx.event
    async def submit_search(self, form_data: dict | None = None):
        await self._run_search()
