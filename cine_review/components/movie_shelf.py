"""Prateleira horizontal de filmes. Quando `shelf.available=False`, renderiza skeleton."""

import reflex as rx

from cine_review.components.movie_card import movie_card
from cine_review.state.movie_state import Movie, Shelf


def _skeleton_card() -> rx.Component:
    return rx.box(
        class_name=(
            "w-[170px] aspect-[2/3] rounded-lg flex-shrink-0 "
            "bg-gradient-to-br from-[#1a1e28] to-[#13161e] "
            "border border-white/5 animate-pulse"
        ),
    )


def _skeleton_row() -> rx.Component:
    return rx.flex(
        _skeleton_card(),
        _skeleton_card(),
        _skeleton_card(),
        _skeleton_card(),
        _skeleton_card(),
        _skeleton_card(),
        _skeleton_card(),
        _skeleton_card(),
        class_name="gap-3 overflow-x-auto pb-4 px-8",
    )


def _card_wrapper(m: Movie) -> rx.Component:
    return rx.box(
        movie_card(m),
        class_name="w-[170px] flex-shrink-0",
    )


def movie_shelf(shelf: Shelf) -> rx.Component:
    return rx.box(
        rx.flex(
            rx.heading(
                shelf.title,
                size="5",
                class_name="text-slate-100 font-bold tracking-tight",
            ),
            rx.cond(
                ~shelf.available,
                rx.text(
                    "Em breve",
                    class_name=(
                        "text-amber-400/80 text-[10px] font-semibold ml-3 "
                        "uppercase tracking-widest border border-amber-400/30 "
                        "px-2 py-0.5 rounded"
                    ),
                ),
            ),
            class_name="items-center mb-4 px-8",
        ),
        rx.cond(
            shelf.available,
            rx.flex(
                rx.foreach(shelf.movies, _card_wrapper),
                class_name="gap-3 overflow-x-auto pb-4 px-8 scroll-smooth",
            ),
            _skeleton_row(),
        ),
        class_name="mb-10",
    )
