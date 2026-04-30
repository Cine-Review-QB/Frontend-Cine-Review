"""Hero do topo da home. Backdrop com pôster esticado + blur + gradient overlay."""

import reflex as rx

from cine_review.state.movie_state import Movie


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


def _ctas() -> rx.Component:
    return rx.flex(
        rx.button(
            rx.icon("info", size=16),
            "Ver detalhes",
            disabled=True,
            title="Em breve",
            class_name=(
                "bg-teal-500 hover:bg-teal-400 text-slate-900 font-semibold "
                "px-6 py-3 rounded-lg transition-colors gap-2 items-center "
                "disabled:opacity-50 disabled:cursor-not-allowed"
            ),
        ),
        rx.button(
            rx.icon("pencil", size=16),
            "Escrever review",
            disabled=True,
            title="Em breve — requer login",
            class_name=(
                "bg-transparent border border-white/20 hover:border-white/40 "
                "text-white font-semibold px-6 py-3 rounded-lg transition-colors "
                "gap-2 items-center disabled:opacity-50 disabled:cursor-not-allowed"
            ),
        ),
        class_name="items-center gap-3 mt-4",
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
            _ctas(),
            class_name="flex-col gap-4 max-w-2xl",
        ),
        class_name=(
            "items-end gap-8 relative z-10 px-8 pb-16 pt-32 max-w-[1400px] mx-auto"
        ),
    )


def hero(movie: Movie) -> rx.Component:
    return rx.box(
        _backdrop(movie),
        _gradients(),
        _content(movie),
        class_name="relative w-full min-h-[68vh] overflow-hidden",
    )
