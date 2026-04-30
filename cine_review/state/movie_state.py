"""Estado dos filmes na home. Carrega do Content Service e agrupa em prateleiras."""

from dataclasses import dataclass, field

import reflex as rx

from cine_review.api import fetch_movies
from cine_review.config import GENRES_TO_SHOW, INITIAL_FETCH_LIMIT, MOVIES_PER_SHELF


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

    rating_str: str = ""
    year_str: str = ""
    runtime_str: str = ""
    genres_str: str = ""

    has_poster: bool = False
    has_backdrop: bool = False
    has_overview: bool = False


@dataclass
class Shelf:
    """Prateleira horizontal na home. `kind` decide a fonte de dados."""

    title: str = ""
    kind: str = "genre"
    movies: list[Movie] = field(default_factory=list)
    available: bool = True


def _to_movie(d: dict) -> Movie:
    rating = float(d.get("rating") or 0.0)
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
        rating_str=f"{rating:.1f}" if rating > 0 else "—",
        year_str=str(year) if year else "",
        runtime_str=f"{runtime} min" if runtime else "",
        genres_str=" · ".join(genres[:3]),
        has_poster=bool(poster),
        has_backdrop=bool(backdrop),
        has_overview=bool(overview),
    )


def _build_shelves(movies: list[Movie]) -> list[Shelf]:
    """Monta a lista de prateleiras: placeholders sociais + gêneros reais.

    Filmes sem poster_url são descartados das prateleiras — com 45k filmes no
    catálogo sobra muito de cada gênero, e card sem pôster polui visualmente.
    """
    with_poster = [m for m in movies if m.has_poster]

    shelves: list[Shelf] = [
        Shelf(title="Top da semana", kind="top_week", available=False),
        Shelf(title="Reviews de quem você segue", kind="feed", available=False),
    ]

    for genre in GENRES_TO_SHOW:
        items = [m for m in with_poster if genre in m.genres][:MOVIES_PER_SHELF]
        if items:
            shelves.append(
                Shelf(title=genre, kind="genre", movies=items, available=True)
            )

    return shelves


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
            self.shelves = _build_shelves(movies)
        except Exception as e:
            self.error = f"Não foi possível carregar os filmes: {e}"
        finally:
            self.is_loading = False
