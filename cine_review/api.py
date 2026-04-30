"""Clientes HTTP para os microsserviços. Sempre chamados a partir do State (server-side)."""

import httpx

from cine_review.config import CONTENT_API_URL


async def fetch_movies(limit: int = 100, skip: int = 0, genre: str | None = None) -> list[dict]:
    """Busca filmes no Content Service. Retorna lista bruta de docs."""
    params: dict = {"limit": limit, "skip": skip}
    if genre:
        params["genre"] = genre
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{CONTENT_API_URL}/api/movies/", params=params)
        r.raise_for_status()
        return r.json().get("movies", [])
