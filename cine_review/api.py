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
