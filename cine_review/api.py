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


async def fetch_movies_by_genre(
    genre: str,
    limit: int = 30,
    skip: int = 0,
    token: str = "",
) -> dict:
    """GET /movies/genre/{genre} via Gateway. Retorna payload completo
    com movies + total pra suportar paginação."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{GATEWAY_URL}/movies/genre/{genre}",
            params={"limit": limit, "skip": skip},
            headers=_bearer(token),
        )
        r.raise_for_status()
        return r.json()


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


async def fetch_weekly_ranking(token: str = "") -> list[dict]:
    """GET /ranking/weekly. Top filmes da semana por número de reviews.
    Rota pública — token opcional."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{GATEWAY_URL}/ranking/weekly",
            headers=_bearer(token),
        )
        r.raise_for_status()
        return r.json()


async def search_movies(query: str, limit: int = 30, token: str = "") -> list[dict]:
    """GET /movies/search?q=. Busca full-text por título."""
    if not query.strip():
        return []
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{GATEWAY_URL}/movies/search",
            params={"q": query, "limit": limit},
            headers=_bearer(token),
        )
        r.raise_for_status()
        return r.json().get("movies", [])


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


async def fetch_user_reviews(user_id: str, token: str) -> list[dict]:
    """GET /reviews/user/{user_id}. Reviews escritas por um usuário."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{GATEWAY_URL}/reviews/user/{user_id}",
            headers=_bearer(token),
        )
        r.raise_for_status()
        return r.json()


# ─── Feed (Cine-Review) ───────────────────────────────────────────────


async def fetch_feed(token: str, limit: int = 30) -> list[dict]:
    """GET /feed. Reviews dos usuários que o autenticado segue."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{GATEWAY_URL}/feed",
            params={"limit": limit},
            headers=_bearer(token),
        )
        r.raise_for_status()
        return r.json()


# ─── Perfil (Cine-Users) ──────────────────────────────────────────────


async def fetch_user_by_username(username: str, token: str) -> dict | None:
    """GET /auth/users/{username}. Retorna None se 404."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{GATEWAY_URL}/auth/users/{username}",
            headers=_bearer(token),
        )
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()


async def update_profile(
    username: str,
    bio: str,
    avatar_url: str,
    token: str,
) -> dict:
    """PUT /auth/me. Atualiza perfil do usuário logado."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.put(
            f"{GATEWAY_URL}/auth/me",
            headers=_bearer(token),
            json={
                "username": username,
                "bio": bio,
                "avatarUrl": avatar_url,
            },
        )
        r.raise_for_status()
        return r.json()


# ─── Follow (Cine-Review) ─────────────────────────────────────────────


async def follow_user(user_id: str, token: str) -> dict:
    """POST /follow/{user_id}. Segue o usuário."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            f"{GATEWAY_URL}/follow/{user_id}",
            headers=_bearer(token),
        )
        r.raise_for_status()
        return r.json()


async def unfollow_user(user_id: str, token: str) -> None:
    """DELETE /follow/{user_id}. Deixa de seguir."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.delete(
            f"{GATEWAY_URL}/follow/{user_id}",
            headers=_bearer(token),
        )
        r.raise_for_status()


async def fetch_following(user_id: str, token: str) -> list[dict]:
    """GET /follows/{user_id}/following. Lista quem `user_id` segue."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{GATEWAY_URL}/follows/{user_id}/following",
            headers=_bearer(token),
        )
        r.raise_for_status()
        return r.json()


async def fetch_followers(user_id: str, token: str) -> list[dict]:
    """GET /follows/{user_id}/followers. Lista quem segue `user_id`."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(
            f"{GATEWAY_URL}/follows/{user_id}/followers",
            headers=_bearer(token),
        )
        r.raise_for_status()
        return r.json()
