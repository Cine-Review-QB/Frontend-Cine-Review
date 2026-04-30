"""Home page — hero + prateleiras horizontais."""

import reflex as rx

from cine_review.components.hero import hero
from cine_review.components.movie_shelf import movie_shelf
from cine_review.components.navbar import navbar
from cine_review.state.movie_state import MovieState


def _loading() -> rx.Component:
    return rx.flex(
        rx.spinner(size="3", class_name="text-teal-400"),
        rx.text("Carregando filmes...", class_name="text-slate-400 ml-3 text-sm"),
        class_name="items-center justify-center min-h-[60vh]",
    )


def _error() -> rx.Component:
    return rx.flex(
        rx.icon("triangle-alert", size=32, class_name="text-red-400 mb-3"),
        rx.text(MovieState.error, class_name="text-red-400 text-center max-w-md"),
        rx.text(
            "Verifique se o Cine-Content está rodando em "
            "http://localhost:5000 e se o MongoDB foi populado.",
            class_name="text-slate-500 text-xs text-center mt-2 max-w-md",
        ),
        class_name="flex-col items-center justify-center min-h-[60vh] px-8",
    )


def _empty() -> rx.Component:
    return rx.flex(
        rx.icon("film", size=48, class_name="text-slate-600 mb-3"),
        rx.heading(
            "Nenhum filme cadastrado ainda",
            size="5",
            class_name="text-slate-300 mb-2",
        ),
        rx.text(
            "Rode o seed do Cine-Content para popular o MongoDB:",
            class_name="text-slate-500 text-sm",
        ),
        rx.code(
            "uv run python scripts/seed_movies_from_kaggle.py --limit 1000",
            class_name="mt-3 text-teal-400 bg-[#13161e] px-3 py-1.5 rounded text-xs",
        ),
        class_name="flex-col items-center justify-center min-h-[60vh] px-8",
    )


def _content() -> rx.Component:
    return rx.box(
        hero(MovieState.featured),
        rx.box(
            rx.foreach(MovieState.shelves, movie_shelf),
            class_name="max-w-[1400px] mx-auto pt-12 pb-24",
        ),
    )


def home() -> rx.Component:
    return rx.box(
        navbar(),
        rx.cond(
            MovieState.is_loading,
            _loading(),
            rx.cond(
                MovieState.error != "",
                _error(),
                rx.cond(
                    MovieState.is_empty,
                    _empty(),
                    _content(),
                ),
            ),
        ),
        class_name=(
            "min-h-screen bg-[#0a0a0f] text-slate-200 "
            "font-[Inter,system-ui,sans-serif]"
        ),
    )
