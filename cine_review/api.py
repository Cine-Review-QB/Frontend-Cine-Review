"""Clientes HTTP para os microsserviços. Sempre chamados a partir do State (server-side).

Todo request vai pelo API Gateway. Rotas públicas (catálogo) não exigem
token; rotas autenticadas (reviews, follow, feed, ranking) exigem o
Bearer JWT obtido no login Auth0.
"""

import httpx

from cine_review.config import GATEWAY_URL


def _bearer(token: str) -> dict:
    """Header Authorization quando há token; dict vazio caso contrário."""
    return {"Authorization": f"Bearer {token}"} if token else {}


# ─── Catálogo (Cine-Content) ──────────────────────────────────────────


async def fetch_movies(
    limit: int = 100,
    skip: int = 0,
    genre: str | None = None,
    token: str = "",
) -> list[dict]:
    """GET /movies via Gateway. Token é opcional (rota pública)."""
    params: dict = {"limit": limit, "skip": skip}
    if genre:
        params["genre"] = genre
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{GATEWAY_URL}/movies",
            params=params,
            headers=_bearer(token),
        )
        r.raise_for_status()
        return r.json().get("movies", [])


async def fetch_movie_by_id(movie_id: str, token: str = "") -> dict | None:
    """GET /movies/{id}. Retorna None se 404."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{GATEWAY_URL}/movies/{movie_id}",
            headers=_bearer(token),
        )
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()


# ─── Reviews (Cine-Review) ────────────────────────────────────────────


async def fetch_reviews(movie_id: str, token: str) -> list[dict]:
    """GET /reviews/{movie_id}. Exige token."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{GATEWAY_URL}/reviews/{movie_id}",
            headers=_bearer(token),
        )
        r.raise_for_status()
        return r.json()


async def post_review(
    movie_id: str,
    movie_title: str,
    rating: float,
    text: str | None,
    token: str,
) -> dict:
    """POST /reviews. Exige token. 409 se já existe review do usuário pro filme."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            f"{GATEWAY_URL}/reviews",
            json={
                "movie_id": movie_id,
                "movie_title": movie_title,
                "rating": rating,
                "text": text,
            },
            headers=_bearer(token),
        )
        r.raise_for_status()
        return r.json()


async def delete_review(review_id: str, token: str) -> None:
    """DELETE /reviews/{review_id}. 403 se não for o autor."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.delete(
            f"{GATEWAY_URL}/reviews/{review_id}",
            headers=_bearer(token),
        )
        r.raise_for_status()


async def toggle_review_like(review_id: str, token: str) -> dict:
    """POST /reviews/{review_id}/like. Toggle: cria like se não existe, remove se existe.
    Retorna {liked: bool, likes_count: int}."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            f"{GATEWAY_URL}/reviews/{review_id}/like",
            headers=_bearer(token),
        )
        r.raise_for_status()
        return r.json()
