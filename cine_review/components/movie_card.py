"""Card de filme: pôster + badge de rating sempre visível + overlay no hover."""

import reflex as rx

from cine_review.state.movie_state import Movie


def _poster_or_fallback(movie: Movie) -> rx.Component:
    return rx.cond(
        movie.has_poster,
        rx.image(
            src=movie.poster_url,
            alt=movie.title,
            loading="lazy",
            referrer_policy="no-referrer",
            class_name="w-full h-full object-cover",
        ),
        rx.flex(
            rx.icon("film", size=28, class_name="text-slate-600"),
            rx.text(
                movie.title,
                class_name="text-slate-500 text-xs text-center mt-2 px-3 line-clamp-3",
            ),
            class_name=(
                "flex-col items-center justify-center w-full h-full "
                "bg-gradient-to-br from-[#1a1e28] to-[#13161e]"
            ),
        ),
    )


def _rating_badge(movie: Movie) -> rx.Component:
    """Badge sempre visível no canto. DNA Letterboxd no card Stremio."""
    return rx.cond(
        movie.rating > 0,
        rx.flex(
            rx.icon("star", size=11, class_name="text-amber-400 fill-amber-400"),
            rx.text(
                movie.rating_str,
                class_name="text-amber-400 text-[11px] font-bold leading-none",
            ),
            class_name=(
                "absolute top-2 right-2 items-center gap-1 "
                "bg-black/75 backdrop-blur-sm px-2 py-1 rounded-md "
                "border border-white/5"
            ),
        ),
    )


def _hover_overlay(movie: Movie) -> rx.Component:
    return rx.box(
        rx.box(
            rx.text(
                movie.title,
                class_name="text-white font-semibold text-sm leading-tight line-clamp-2",
            ),
            rx.cond(
                movie.year_str != "",
                rx.text(
                    movie.year_str,
                    class_name="text-slate-300 text-xs mt-1",
                ),
            ),
            class_name="absolute bottom-0 left-0 right-0 p-3",
        ),
        class_name=(
            "absolute inset-0 bg-gradient-to-t from-black via-black/70 to-transparent "
            "opacity-0 group-hover:opacity-100 transition-opacity duration-200"
        ),
    )


def movie_card(movie: Movie) -> rx.Component:
    return rx.link(
        rx.box(
            rx.box(
                _poster_or_fallback(movie),
                _rating_badge(movie),
                _hover_overlay(movie),
                class_name=(
                    "relative w-full aspect-[2/3] overflow-hidden rounded-lg "
                    "bg-[#13161e] border border-white/5 "
                    "group-hover:border-white/15 transition-colors"
                ),
            ),
            class_name=(
                "group cursor-pointer transition-transform duration-200 "
                "hover:scale-[1.04] hover:shadow-2xl hover:shadow-amber-500/10 "
                "will-change-transform"
            ),
        ),
        href="/movie/" + movie.id,
        class_name="block",
    )
