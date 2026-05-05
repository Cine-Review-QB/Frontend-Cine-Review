"""Estado dos filmes na home. Carrega do Content Service e agrupa em prateleiras."""

import logging
from dataclasses import dataclass, field

import reflex as rx

from cine_review.api import (
    fetch_feed,
    fetch_movie_by_id,
    fetch_movies,
    fetch_weekly_ranking,
)
from cine_review.config import GENRES_TO_SHOW, INITIAL_FETCH_LIMIT, MOVIES_PER_SHELF
from cine_review.state.auth_state import AuthState

logger = logging.getLogger(__name__)


@dataclass
class Movie:
    """Filme exibido no front. Strings já pré-formatadas para os componentes.

    Reflex 0.9 removeu rx.Base e não trata pydantic.BaseModel como state var.
    Dataclass é o padrão recomendado.
    """

    id: str = ""
    title: str = ""
    overview: str = ""
    director: str = ""
    poster_url: str = ""
    backdrop_url: str = ""
    genres: list[str] = field(default_factory=list)
    rating: float = 0.0
    vote_count: int = 0

    rating_str: str = ""
    year_str: str = ""
    runtime_str: str = ""
    genres_str: str = ""
    vote_count_str: str = ""

    has_poster: bool = False
    has_backdrop: bool = False
    has_overview: bool = False
    has_votes: bool = False


@dataclass
class Shelf:
    """Prateleira horizontal na home. `kind` decide a fonte de dados."""

    title: str = ""
    kind: str = "genre"
    movies: list[Movie] = field(default_factory=list)
    available: bool = True


def _format_votes(n: int) -> str:
    """Compacta vote_count em K/M (ex.: 12345 → '12K', 1500000 → '1.5M')."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M".replace(".0M", "M")
    if n >= 1_000:
        return f"{n / 1_000:.1f}K".replace(".0K", "K")
    return str(n)


def _to_movie(d: dict) -> Movie:
    rating = float(d.get("rating") or 0.0)
    vote_count = int(d.get("vote_count") or 0)
    year = d.get("year")
    runtime = d.get("runtime")
    genres = d.get("genres") or []
    poster = d.get("poster_url") or ""
    backdrop = d.get("backdrop_url") or ""
    overview = (d.get("overview") or "").strip()

    return Movie(
        id=str(d.get("_id", "")),
        title=d.get("title") or "Sem título",
        overview=overview,
        director=d.get("director") or "",
        poster_url=poster,
        backdrop_url=backdrop,
        genres=genres,
        rating=rating,
        vote_count=vote_count,
        rating_str=f"{rating:.1f}" if rating > 0 else "—",
        year_str=str(year) if year else "",
        runtime_str=f"{runtime} min" if runtime else "",
        genres_str=" · ".join(genres[:3]),
        vote_count_str=_format_votes(vote_count) if vote_count > 0 else "",
        has_poster=bool(poster),
        has_backdrop=bool(backdrop),
        has_overview=bool(overview),
        has_votes=vote_count > 0,
    )


def _build_shelves(
    movies: list[Movie],
    top_week: list[Movie] | None = None,
    feed: list[Movie] | None = None,
) -> list[Shelf]:
    """Monta a lista de prateleiras: top da semana + feed + gêneros.

    Filmes sem poster_url são descartados das prateleiras — com 45k filmes no
    catálogo sobra muito de cada gênero, e card sem pôster polui visualmente.

    Top da semana e feed só entram se tiverem dados — caso contrário são
    omitidos (em vez de mostrar skeleton "em breve" pra sempre).
    """
    with_poster = [m for m in movies if m.has_poster]
    top_week = top_week or []
    feed = feed or []

    shelves: list[Shelf] = []

    if top_week:
        shelves.append(
            Shelf(title="Top da semana", kind="top_week", movies=top_week, available=True)
        )

    if feed:
        shelves.append(
            Shelf(
                title="Reviews de quem você segue",
                kind="feed",
                movies=feed,
                available=True,
            )
        )

    for genre in GENRES_TO_SHOW:
        items = [m for m in with_poster if genre in m.genres][:MOVIES_PER_SHELF]
        if items:
            shelves.append(
                Shelf(title=genre, kind="genre", movies=items, available=True)
            )

    return shelves


async def _resolve_movie_ids(
    movies: list[Movie],
    movie_ids: list[str],
    token: str = "",
) -> list[Movie]:
    """Resolve uma lista de movie_ids em objetos Movie.

    Tenta primeiro casar com os filmes já carregados em memória; pra IDs
    que não estão no batch, faz fetch_movie_by_id pontual. Deduplica
    preservando ordem. Filmes sem poster são descartados.
    """
    by_id = {m.id: m for m in movies}
    seen: set[str] = set()
    resolved: list[Movie] = []
    for movie_id in movie_ids:
        if not movie_id or movie_id in seen:
            continue
        seen.add(movie_id)
        movie = by_id.get(movie_id)
        if movie is None:
            try:
                doc = await fetch_movie_by_id(movie_id, token=token)
            except Exception as e:
                logger.warning("Falha ao resolver filme %s: %s", movie_id, e)
                continue
            if doc is None:
                continue
            movie = _to_movie(doc)
        if movie.has_poster:
            resolved.append(movie)
    return resolved


async def _resolve_top_week(movies: list[Movie]) -> list[Movie]:
    """Busca o ranking semanal (público) e resolve em Movie objects."""
    try:
        ranking = await fetch_weekly_ranking()
    except Exception as e:
        logger.warning("Falha ao buscar ranking semanal: %s", e)
        return []
    if not ranking:
        return []
    return await _resolve_movie_ids(
        movies, [str(item.get("movie_id") or "") for item in ranking]
    )


async def _resolve_feed(movies: list[Movie], token: str) -> list[Movie]:
    """Busca o feed (reviews dos seguidos) e resolve em Movie objects únicos."""
    if not token:
        return []
    try:
        feed = await fetch_feed(token, limit=20)
    except Exception as e:
        logger.warning("Falha ao buscar feed: %s", e)
        return []
    if not feed:
        return []
    return await _resolve_movie_ids(
        movies, [str(r.get("movie_id") or "") for r in feed], token=token
    )


def _pick_featured(movies: list[Movie]) -> Movie:
    """Escolhe o filme do hero. Prefere com backdrop (visualmente muito melhor)."""
    with_backdrop = [
        m for m in movies if m.has_backdrop and m.has_poster and m.has_overview
    ]
    if with_backdrop:
        return max(with_backdrop, key=lambda m: m.rating)

    with_poster = [m for m in movies if m.has_poster and m.has_overview]
    if with_poster:
        return max(with_poster, key=lambda m: m.rating)

    if movies:
        return movies[0]
    return Movie()


class MovieState(rx.State):
    shelves: list[Shelf] = []
    featured: Movie = Movie()
    is_loading: bool = False
    error: str = ""
    is_empty: bool = False

    @rx.event
    async def load_movies(self):
        self.is_loading = True
        self.error = ""
        self.is_empty = False
        try:
            raw = await fetch_movies(limit=INITIAL_FETCH_LIMIT)
            movies = [_to_movie(d) for d in raw]

            if not movies:
                self.is_empty = True
                self.shelves = []
                self.featured = Movie()
                return

            self.featured = _pick_featured(movies)
            auth = await self.get_state(AuthState)
            top_week = await _resolve_top_week(movies)
            feed = await _resolve_feed(movies, auth.access_token)
            self.shelves = _build_shelves(movies, top_week=top_week, feed=feed)
        except Exception as e:
            self.error = f"Não foi possível carregar os filmes: {e}"
        finally:
            self.is_loading = False
