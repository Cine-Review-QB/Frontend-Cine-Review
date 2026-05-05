"""Página /genre/[name] — todos os filmes de um gênero, paginados."""

import reflex as rx

from cine_review.components.movie_card import movie_card
from cine_review.components.navbar import navbar
from cine_review.state.genre_state import GenreState


def _header() -> rx.Component:
    return rx.flex(
        rx.heading(
            GenreState.genre_from_url,
            size="8",
            class_name="text-white font-bold",
        ),
        rx.text(
            GenreState.total.to_string() + " filmes",
            class_name="text-slate-400 text-sm",
        ),
        class_name="flex-col items-center gap-1 pt-12 pb-8",
    )


def _grid() -> rx.Component:
    return rx.flex(
        rx.foreach(
            GenreState.movies,
            lambda m: rx.box(movie_card(m), class_name="w-[180px]"),
        ),
        class_name="flex-wrap gap-4 justify-center",
    )


def _pagination() -> rx.Component:
    return rx.flex(
        rx.button(
            rx.icon("chevron-left", size=16),
            rx.text("Anterior"),
            on_click=GenreState.prev_page,
            disabled=~GenreState.has_prev,
            class_name=(
                "bg-transparent border border-white/15 hover:border-white/40 "
                "text-slate-200 font-medium px-5 py-2 rounded-md cursor-pointer "
                "disabled:opacity-30 disabled:cursor-not-allowed gap-2 items-center"
            ),
        ),
        rx.text(
            GenreState.page_label,
            class_name="text-slate-300 text-sm font-medium px-4",
        ),
        rx.button(
            rx.text("Próxima"),
            rx.icon("chevron-right", size=16),
            on_click=GenreState.next_page,
            disabled=~GenreState.has_next,
            class_name=(
                "bg-transparent border border-white/15 hover:border-white/40 "
                "text-slate-200 font-medium px-5 py-2 rounded-md cursor-pointer "
                "disabled:opacity-30 disabled:cursor-not-allowed gap-2 items-center"
            ),
        ),
        class_name="items-center justify-center gap-3 py-12",
    )


def _empty() -> rx.Component:
    return rx.flex(
        rx.icon("film", size=24, class_name="text-slate-500"),
        rx.text(
            "Nenhum filme encontrado nesse gênero.",
            class_name="text-slate-400",
        ),
        class_name="items-center justify-center gap-2 py-24",
    )


def _error() -> rx.Component:
    return rx.flex(
        rx.icon("triangle-alert", size=24, class_name="text-red-400"),
        rx.text(GenreState.error, class_name="text-red-400"),
        class_name="items-center justify-center gap-2 py-24",
    )


def genre() -> rx.Component:
    return rx.box(
        navbar(),
        _header(),
        rx.cond(
            GenreState.is_loading,
            rx.flex(
                rx.spinner(class_name="text-teal-400"),
                class_name="items-center justify-center py-24",
            ),
            rx.cond(
                GenreState.error != "",
                _error(),
                rx.cond(
                    GenreState.has_movies,
                    rx.box(
                        rx.box(_grid(), class_name="px-8 max-w-[1400px] mx-auto"),
                        _pagination(),
                    ),
                    _empty(),
                ),
            ),
        ),
        class_name="min-h-screen bg-[#0a0a0f] text-slate-200 font-sans pb-12",
    )
