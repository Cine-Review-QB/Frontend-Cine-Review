"""Estado dos filmes na home. Carrega do Content Service e agrupa em prateleiras."""

import logging
from dataclasses import dataclass, field

import reflex as rx

from cine_review.api import fetch_movie_by_id, fetch_movies, fetch_weekly_ranking
from cine_review.config import GENRES_TO_SHOW, INITIAL_FETCH_LIMIT, MOVIES_PER_SHELF

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
) -> list[Shelf]:
    """Monta a lista de prateleiras: top da semana + feed (placeholder) + gêneros.

    Filmes sem poster_url são descartados das prateleiras — com 45k filmes no
    catálogo sobra muito de cada gênero, e card sem pôster polui visualmente.
    """
    with_poster = [m for m in movies if m.has_poster]
    top_week = top_week or []

    shelves: list[Shelf] = []

    # Top da semana: só inclui se tiver dados — caso contrário a prateleira
    # não aparece (em vez de mostrar skeleton "em breve" pra sempre).
    if top_week:
        shelves.append(
            Shelf(title="Top da semana", kind="top_week", movies=top_week, available=True)
        )

    # Feed continua como placeholder até o front consumir aqui na home (hoje
    # tem página /feed dedicada).
    shelves.append(
        Shelf(title="Reviews de quem você segue", kind="feed", available=False)
    )

    for genre in GENRES_TO_SHOW:
        items = [m for m in with_poster if genre in m.genres][:MOVIES_PER_SHELF]
        if items:
            shelves.append(
                Shelf(title=genre, kind="genre", movies=items, available=True)
            )

    return shelves


async def _resolve_top_week(movies: list[Movie]) -> list[Movie]:
    """Busca o ranking semanal e resolve os movie_ids em objetos Movie.

    Tenta primeiro casar com os 100 filmes já carregados (no comum, são os
    populares e há overlap). Pra IDs que não estão no batch, faz fetch por
    ID. Falhas individuais são ignoradas — best-effort.
    """
    try:
        ranking = await fetch_weekly_ranking()
    except Exception as e:
        logger.warning("Falha ao buscar ranking semanal: %s", e)
        return []

    if not ranking:
        return []

    by_id = {m.id: m for m in movies}
    resolved: list[Movie] = []
    for item in ranking:
        movie_id = str(item.get("movie_id") or "")
        if not movie_id:
            continue
        movie = by_id.get(movie_id)
        if movie is None:
            try:
                doc = await fetch_movie_by_id(movie_id)
            except Exception as e:
                logger.warning("Falha ao resolver filme %s: %s", movie_id, e)
                continue
            if doc is None:
                continue
            movie = _to_movie(doc)
        if movie.has_poster:
            resolved.append(movie)
    return resolved


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
            top_week = await _resolve_top_week(movies)
            self.shelves = _build_shelves(movies, top_week=top_week)
        except Exception as e:
            self.error = f"Não foi possível carregar os filmes: {e}"
        finally:
            self.is_loading = False
