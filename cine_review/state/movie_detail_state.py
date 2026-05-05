"""Estado da página de detalhes do filme — info do filme + reviews + form."""

from __future__ import annotations

import dataclasses
import logging
from dataclasses import dataclass, field

import httpx
import reflex as rx

from cine_review.api import (
    delete_review as api_delete_review,
    fetch_movie_by_id,
    fetch_reviews,
    post_review,
    toggle_review_like,
)
from cine_review.state.auth_state import AuthState
from cine_review.state.movie_state import Movie, _to_movie

logger = logging.getLogger(__name__)


@dataclass
class ReviewItem:
    """Review já formatada para a UI."""

    id: str = ""
    user_id: str = ""
    movie_id: str = ""
    movie_title: str = ""
    rating: float = 0.0
    text: str = ""
    likes_count: int = 0
    is_liked: bool = False
    username: str = ""
    avatar_url: str = ""

    # Campos pré-formatados pra UI
    rating_str: str = ""
    created_str: str = ""
    display_name: str = ""
    has_avatar: bool = False
    has_text: bool = False
    has_movie_title: bool = False


def _format_date(iso_str: str) -> str:
    if not iso_str or len(iso_str) < 10:
        return ""
    try:
        yyyy, mm, dd = iso_str[:10].split("-")
        return f"{dd}/{mm}/{yyyy}"
    except ValueError:
        return ""


def _to_review(d: dict) -> ReviewItem:
    rating = float(d.get("rating") or 0.0)
    user_id = d.get("user_id") or ""
    username = d.get("username") or ""
    avatar_url = d.get("avatar_url") or ""
    text = (d.get("text") or "").strip()

    if username:
        display_name = username
    elif "|" in user_id:
        display_name = user_id.split("|")[-1][:10]
    elif user_id:
        display_name = user_id[:10]
    else:
        display_name = "Usuário"

    movie_title = d.get("movie_title") or ""

    return ReviewItem(
        id=str(d.get("id") or ""),
        user_id=user_id,
        movie_id=str(d.get("movie_id") or ""),
        movie_title=movie_title,
        rating=rating,
        text=text,
        likes_count=int(d.get("likes_count") or 0),
        is_liked=bool(d.get("is_liked")),
        username=username,
        avatar_url=avatar_url,
        rating_str=f"{rating:.1f}",
        created_str=_format_date(str(d.get("created_at") or "")),
        display_name=display_name,
        has_avatar=bool(avatar_url),
        has_text=bool(text),
        has_movie_title=bool(movie_title),
    )


class MovieDetailState(rx.State):
    """Estado da página /movie/[id]."""

    # Defaults class-level (mesmo padrão de MovieState). Usar field() com
    # default_factory passando classes/lambdas quebra o compile do Reflex 0.9
    # com erro "cannot pickle mappingproxy" durante deepcopy.
    movie: Movie = Movie()
    reviews: list[ReviewItem] = []
    is_loading: bool = False
    error: str = ""

    # Formulário de criar review
    form_rating: list[float] = [5.0]
    form_text: str = ""
    form_submitting: bool = False
    form_error: str = ""
    form_success: bool = False

    @rx.var
    def movie_id(self) -> str:
        """Lê o ID do filme da URL `/movie/<id>` (não usa _page.params privado)."""
        path = self.router.url.path or ""
        parts = path.strip("/").split("/")
        if len(parts) >= 2 and parts[0] == "movie":
            return parts[1]
        return ""

    @rx.var
    def form_rating_value(self) -> float:
        return self.form_rating[0] if self.form_rating else 5.0

    @rx.var
    def form_rating_str(self) -> str:
        return f"{self.form_rating_value:.1f}"

    @rx.var
    def has_reviews(self) -> bool:
        return len(self.reviews) > 0

    @rx.event
    async def load_detail(self):
        movie_id = self.movie_id
        if not movie_id:
            self.error = "URL inválida"
            return

        self.is_loading = True
        self.error = ""
        self.form_success = False
        self.form_error = ""

        auth = await self.get_state(AuthState)
        token = auth.access_token

        try:
            movie_doc = await fetch_movie_by_id(movie_id, token)
            if movie_doc is None:
                self.error = "Filme não encontrado."
                self.movie = Movie()
                self.reviews = []
                return
            self.movie = _to_movie(movie_doc)

            # Reviews exigem auth — best-effort se não logado
            if token:
                try:
                    raw = await fetch_reviews(movie_id, token)
                    self.reviews = [_to_review(r) for r in raw]
                except Exception as e:
                    logger.warning("Falha ao carregar reviews: %s", e)
                    self.reviews = []
            else:
                self.reviews = []
        except Exception as e:
            self.error = f"Falha ao carregar: {e}"
        finally:
            self.is_loading = False

    @rx.event
    def set_form_rating(self, value: list[float]):
        self.form_rating = value if value else [5.0]
        self.form_error = ""
        self.form_success = False

    @rx.event
    def set_form_text(self, value: str):
        self.form_text = value[:1000]
        self.form_error = ""
        self.form_success = False

    @rx.event
    async def submit_review(self):
        auth = await self.get_state(AuthState)
        if not auth.access_token:
            self.form_error = "Faça login pra escrever uma review."
            return

        rating = self.form_rating_value
        if rating < 0.5 or rating > 5:
            self.form_error = "Nota deve estar entre 0.5 e 5."
            return

        self.form_submitting = True
        self.form_error = ""
        self.form_success = False

        try:
            await post_review(
                movie_id=self.movie_id,
                movie_title=self.movie.title,
                rating=rating,
                text=self.form_text.strip() or None,
                token=auth.access_token,
            )
            self.form_text = ""
            self.form_rating = [5.0]
            self.form_success = True

            raw = await fetch_reviews(self.movie_id, auth.access_token)
            self.reviews = [_to_review(r) for r in raw]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:
                self.form_error = "Você já avaliou esse filme."
            elif e.response.status_code == 401:
                self.form_error = "Sessão expirada. Faça login novamente."
            else:
                self.form_error = f"Falha ao publicar (HTTP {e.response.status_code})."
        except Exception as e:
            self.form_error = f"Falha ao publicar: {e}"
        finally:
            self.form_submitting = False

    @rx.event
    async def toggle_like(self, review_id: str):
        auth = await self.get_state(AuthState)
        if not auth.access_token:
            return

        try:
            result = await toggle_review_like(review_id, auth.access_token)
            self.reviews = [
                dataclasses.replace(
                    r,
                    is_liked=bool(result.get("liked")),
                    likes_count=int(result.get("likes_count") or 0),
                )
                if r.id == review_id
                else r
                for r in self.reviews
            ]
        except Exception as e:
            logger.warning("Falha no toggle de like: %s", e)

    @rx.event
    async def delete_review(self, review_id: str):
        auth = await self.get_state(AuthState)
        if not auth.access_token:
            return

        try:
            await api_delete_review(review_id, auth.access_token)
            self.reviews = [r for r in self.reviews if r.id != review_id]
        except Exception as e:
            logger.warning("Falha ao deletar review: %s", e)
