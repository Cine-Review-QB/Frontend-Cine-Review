"""Hero do topo da home. Backdrop com pôster esticado + blur + gradient overlay."""

import reflex as rx

from cine_review.state.movie_state import Movie, MovieState


def _backdrop(movie: Movie) -> rx.Component:
    """Backdrop do hero. Prefere backdrop_url (horizontal, sem blur);
    cai pra poster_url com blur; cai pra gradient sólido."""
    return rx.box(
        rx.cond(
            movie.has_backdrop,
            rx.image(
                src=movie.backdrop_url,
                alt="",
                referrer_policy="no-referrer",
                class_name="w-full h-full object-cover opacity-70",
            ),
            rx.cond(
                movie.has_poster,
                rx.image(
                    src=movie.poster_url,
                    alt="",
                    referrer_policy="no-referrer",
                    class_name=(
                        "w-full h-full object-cover blur-2xl scale-125 opacity-50"
                    ),
                ),
                rx.box(
                    class_name=(
                        "w-full h-full bg-gradient-to-br "
                        "from-[#1a1e28] via-[#13161e] to-[#0a0a0f]"
                    ),
                ),
            ),
        ),
        class_name="absolute inset-0 overflow-hidden",
    )


def _gradients() -> rx.Component:
    return rx.fragment(
        rx.box(
            class_name=(
                "absolute inset-0 bg-gradient-to-r "
                "from-[#0a0a0f] via-[#0a0a0f]/85 to-transparent"
            ),
        ),
        rx.box(
            class_name=(
                "absolute inset-0 bg-gradient-to-t "
                "from-[#0a0a0f] via-transparent to-transparent"
            ),
        ),
    )


def _meta_row(movie: Movie) -> rx.Component:
    return rx.flex(
        rx.cond(
            movie.rating > 0,
            rx.flex(
                rx.icon("star", size=18, class_name="text-amber-400 fill-amber-400"),
                rx.text(
                    movie.rating_str,
                    class_name="text-amber-400 font-bold text-base",
                ),
                rx.cond(
                    movie.has_votes,
                    rx.text(
                        "(" + movie.vote_count_str + " votos)",
                        class_name="text-slate-400 text-sm",
                    ),
                ),
                class_name="items-center gap-1.5",
            ),
        ),
        rx.cond(
            movie.year_str != "",
            rx.text(movie.year_str, class_name="text-slate-300 text-sm"),
        ),
        rx.cond(
            movie.runtime_str != "",
            rx.text(movie.runtime_str, class_name="text-slate-300 text-sm"),
        ),
        rx.cond(
            movie.genres_str != "",
            rx.text(movie.genres_str, class_name="text-slate-400 text-sm"),
        ),
        class_name="items-center gap-4",
    )


def _ctas(movie: Movie) -> rx.Component:
    return rx.link(
        rx.flex(
            rx.icon("info", size=16),
            rx.text("Ver detalhes"),
            class_name="items-center gap-2",
        ),
        href="/movie/" + movie.id,
        class_name=(
            "bg-teal-500 hover:bg-teal-400 text-slate-900 font-semibold "
            "px-6 py-3 rounded-lg transition-colors cursor-pointer mt-4 "
            "self-start"
        ),
    )


def _content(movie: Movie) -> rx.Component:
    return rx.flex(
        rx.box(
            rx.cond(
                movie.has_poster,
                rx.image(
                    src=movie.poster_url,
                    alt=movie.title,
                    referrer_policy="no-referrer",
                    class_name="w-full h-full object-cover",
                ),
                rx.flex(
                    rx.icon("film", size=42, class_name="text-slate-600"),
                    class_name=(
                        "items-center justify-center w-full h-full "
                        "bg-gradient-to-br from-[#1a1e28] to-[#13161e]"
                    ),
                ),
            ),
            class_name=(
                "w-[220px] aspect-[2/3] rounded-xl overflow-hidden "
                "shadow-2xl shadow-black/60 flex-shrink-0 "
                "border border-white/10 hidden md:block"
            ),
        ),
        rx.flex(
            _meta_row(movie),
            rx.heading(
                movie.title,
                class_name=(
                    "text-white font-bold tracking-tight max-w-2xl "
                    "text-4xl md:text-5xl leading-tight"
                ),
            ),
            rx.cond(
                movie.has_overview,
                rx.text(
                    movie.overview,
                    class_name=(
                        "text-slate-300 text-base max-w-2xl line-clamp-3 leading-relaxed"
                    ),
                ),
            ),
            _ctas(movie),
            class_name="flex-col gap-4 max-w-2xl",
        ),
        class_name=(
            "items-end gap-8 relative z-10 px-8 pb-16 pt-32 max-w-[1400px] mx-auto"
        ),
    )


def _dots() -> rx.Component:
    """Indicadores clicáveis embaixo do hero, mostrando posição no carrossel."""
    return rx.cond(
        MovieState.has_multiple_featured,
        rx.flex(
            rx.foreach(
                MovieState.featured_pool,
                lambda _m, i: rx.box(
                    on_click=MovieState.set_featured_index(i),
                    class_name=rx.cond(
                        i == MovieState.featured_index,
                        "w-8 h-1.5 bg-teal-400 rounded-full cursor-pointer transition-all",
                        "w-1.5 h-1.5 bg-white/30 hover:bg-white/50 rounded-full cursor-pointer transition-all",
                    ),
                ),
            ),
            class_name=(
                "absolute bottom-6 left-1/2 -translate-x-1/2 z-20 "
                "items-center gap-2"
            ),
        ),
    )


def hero(movie: Movie) -> rx.Component:
    """Hero com crossfade entre os filmes do carrossel.

    O movie passado em argumento já vem do MovieState.featured (computed),
    então cada troca de featured_index retriggera o render.
    """
    return rx.box(
        rx.box(
            _backdrop(movie),
            _gradients(),
            _content(movie),
            class_name=rx.cond(
                MovieState.featured_fading,
                "opacity-0 transition-opacity duration-500",
                "opacity-100 transition-opacity duration-500",
            ),
        ),
        _dots(),
        class_name="relative w-full min-h-[68vh] overflow-hidden",
    )
