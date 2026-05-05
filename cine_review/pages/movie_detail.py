"""Página /movie/[id] — detalhes do filme + reviews + form."""

import reflex as rx

from cine_review.components.navbar import navbar
from cine_review.components.review_card import review_card
from cine_review.components.review_form import review_form
from cine_review.state.auth_state import AuthState
from cine_review.state.movie_detail_state import MovieDetailState


def _back_link() -> rx.Component:
    return rx.link(
        rx.flex(
            rx.icon("arrow-left", size=14),
            rx.text("Voltar"),
            class_name="items-center gap-2",
        ),
        href="/",
        class_name=(
            "absolute top-24 left-8 z-20 text-slate-300 hover:text-teal-400 "
            "text-sm font-medium transition"
        ),
    )


def _hero() -> rx.Component:
    movie = MovieDetailState.movie
    return rx.box(
        # Backdrop
        rx.box(
            rx.cond(
                movie.has_backdrop,
                rx.image(
                    src=movie.backdrop_url,
                    alt="",
                    referrer_policy="no-referrer",
                    class_name="w-full h-full object-cover opacity-40",
                ),
                rx.cond(
                    movie.has_poster,
                    rx.image(
                        src=movie.poster_url,
                        alt="",
                        referrer_policy="no-referrer",
                        class_name=(
                            "w-full h-full object-cover blur-2xl scale-125 opacity-30"
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
        ),
        # Gradients
        rx.box(
            class_name=(
                "absolute inset-0 bg-gradient-to-t "
                "from-[#0a0a0f] via-[#0a0a0f]/85 to-[#0a0a0f]/30"
            ),
        ),
        # Conteúdo
        rx.flex(
            # Pôster
            rx.cond(
                movie.has_poster,
                rx.image(
                    src=movie.poster_url,
                    alt=movie.title,
                    referrer_policy="no-referrer",
                    class_name=(
                        "w-[220px] aspect-[2/3] object-cover rounded-xl "
                        "shadow-2xl flex-shrink-0"
                    ),
                ),
                rx.flex(
                    rx.icon("film", size=42, class_name="text-slate-600"),
                    class_name=(
                        "w-[220px] aspect-[2/3] bg-gradient-to-br "
                        "from-[#1a1e28] to-[#13161e] rounded-xl "
                        "items-center justify-center flex-shrink-0"
                    ),
                ),
            ),
            # Info
            rx.flex(
                rx.flex(
                    rx.icon("star", size=20, class_name="text-amber-400 fill-amber-400"),
                    rx.text(
                        movie.rating_str,
                        class_name="text-amber-400 text-xl font-bold",
                    ),
                    rx.text("·", class_name="text-slate-500"),
                    rx.text(movie.year_str, class_name="text-slate-300"),
                    rx.cond(
                        movie.runtime_str != "",
                        rx.flex(
                            rx.text("·", class_name="text-slate-500"),
                            rx.text(
                                movie.runtime_str,
                                class_name="text-slate-300",
                            ),
                            class_name="items-center gap-3",
                        ),
                    ),
                    class_name="items-center gap-3",
                ),
                rx.heading(
                    movie.title,
                    size="9",
                    class_name="text-white font-bold tracking-tight",
                ),
                rx.cond(
                    movie.genres_str != "",
                    rx.text(movie.genres_str, class_name="text-slate-400 text-sm"),
                ),
                rx.cond(
                    movie.has_overview,
                    rx.text(
                        movie.overview,
                        class_name="text-slate-200 text-base max-w-3xl mt-2 leading-relaxed",
                    ),
                ),
                rx.cond(
                    movie.director != "",
                    rx.flex(
                        rx.text(
                            "Diretor",
                            class_name="text-slate-500 text-xs uppercase tracking-wider",
                        ),
                        rx.text(movie.director, class_name="text-slate-300 text-sm"),
                        class_name="items-center gap-2 mt-3",
                    ),
                ),
                class_name="flex-col gap-3 max-w-3xl",
            ),
            class_name=(
                "items-end gap-8 relative z-10 px-8 pt-32 pb-12 "
                "max-w-[1400px] mx-auto"
            ),
        ),
        class_name="relative w-full",
    )


def _reviews_section() -> rx.Component:
    return rx.box(
        rx.heading(
            "Reviews",
            size="6",
            class_name="text-white font-bold mb-6",
        ),
        rx.cond(
            AuthState.is_authenticated,
            rx.vstack(
                review_form(),
                rx.cond(
                    MovieDetailState.has_reviews,
                    rx.vstack(
                        rx.foreach(
                            MovieDetailState.reviews,
                            lambda r: review_card(
                                r,
                                on_toggle_like=MovieDetailState.toggle_like,
                                on_delete=MovieDetailState.delete_review,
                            ),
                        ),
                        class_name="gap-3 w-full",
                    ),
                    rx.box(
                        rx.text(
                            "Seja o primeiro a escrever uma review!",
                            class_name="text-slate-500 text-center py-8",
                        ),
                        class_name="w-full",
                    ),
                ),
                class_name="gap-6 items-stretch w-full",
            ),
            rx.box(
                rx.flex(
                    rx.icon("lock", size=20, class_name="text-slate-500"),
                    rx.text(
                        "Faça login pra ver e escrever reviews.",
                        class_name="text-slate-400",
                    ),
                    class_name="items-center justify-center gap-2 py-12",
                ),
                class_name="border border-white/10 rounded-lg w-full",
            ),
        ),
        class_name="px-8 max-w-3xl mx-auto pb-24 mt-12",
    )


def _loading() -> rx.Component:
    return rx.flex(
        rx.spinner(class_name="text-teal-400"),
        rx.text("Carregando...", class_name="text-slate-400 ml-3"),
        class_name="items-center justify-center min-h-[60vh]",
    )


def _error() -> rx.Component:
    return rx.flex(
        rx.icon("triangle-alert", size=24, class_name="text-red-400"),
        rx.text(MovieDetailState.error, class_name="text-red-400"),
        class_name="items-center justify-center min-h-[60vh] gap-2",
    )


def movie_detail() -> rx.Component:
    return rx.box(
        navbar(),
        rx.cond(
            MovieDetailState.is_loading,
            _loading(),
            rx.cond(
                MovieDetailState.error != "",
                _error(),
                rx.box(
                    _back_link(),
                    _hero(),
                    _reviews_section(),
                ),
            ),
        ),
        class_name="min-h-screen bg-[#0a0a0f] text-slate-200 font-sans",
    )
