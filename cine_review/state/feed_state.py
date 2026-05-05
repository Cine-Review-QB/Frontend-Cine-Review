"""Estado do feed — reviews dos usuários que o autenticado segue."""

from __future__ import annotations

import dataclasses
import logging

import reflex as rx

from cine_review.api import fetch_feed, toggle_review_like
from cine_review.state.auth_state import AuthState
from cine_review.state.movie_detail_state import ReviewItem, _to_review

logger = logging.getLogger(__name__)


class FeedState(rx.State):
    items: list[ReviewItem] = []
    is_loading: bool = False
    error: str = ""

    @rx.var
    def has_items(self) -> bool:
        return len(self.items) > 0

    @rx.event
    async def load_feed(self):
        auth = await self.get_state(AuthState)
        if not auth.access_token:
            self.error = "Faça login pra ver seu feed."
            self.items = []
            return

        self.is_loading = True
        self.error = ""

        try:
            raw = await fetch_feed(auth.access_token)
            self.items = [_to_review(r) for r in raw]
        except Exception as e:
            self.error = f"Falha ao carregar feed: {e}"
            self.items = []
        finally:
            self.is_loading = False

    @rx.event
    async def toggle_like(self, review_id: str):
        auth = await self.get_state(AuthState)
        if not auth.access_token:
            return
        try:
            result = await toggle_review_like(review_id, auth.access_token)
            self.items = [
                dataclasses.replace(
                    r,
                    is_liked=bool(result.get("liked")),
                    likes_count=int(result.get("likes_count") or 0),
                )
                if r.id == review_id
                else r
                for r in self.items
            ]
        except Exception as e:
            logger.warning("Falha no toggle de like (feed): %s", e)
