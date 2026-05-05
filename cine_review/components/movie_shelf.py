"""Prateleira horizontal de filmes. Quando `shelf.available=False`, renderiza skeleton."""

import reflex as rx

from cine_review.components.movie_card import movie_card
from cine_review.state.movie_state import Movie, MovieState, Shelf


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


def _shelf_title(shelf: Shelf) -> rx.Component:
    """Quando é prateleira de gênero, vira link clicável pra /genre/{name}.
    As outras (top_week, feed) renderizam só texto — não há página dedicada
    pra elas (o ranking já é o "/feed" do dia, e o feed tem página própria)."""
    return rx.cond(
        shelf.kind == "genre",
        rx.link(
            rx.flex(
                rx.heading(
                    shelf.title,
                    size="5",
                    class_name=(
                        "text-slate-100 font-bold tracking-tight "
                        "group-hover:text-teal-400 transition-colors"
                    ),
                ),
                rx.icon(
                    "chevron-right",
                    size=18,
                    class_name=(
                        "text-slate-500 group-hover:text-teal-400 "
                        "transition-colors mt-0.5"
                    ),
                ),
                class_name="items-center gap-1 group cursor-pointer",
            ),
            href="/genre/" + shelf.title,
        ),
        rx.heading(
            shelf.title,
            size="5",
            class_name="text-slate-100 font-bold tracking-tight",
        ),
    )


def _scroll_btn(shelf: Shelf, direction: int) -> rx.Component:
    """Chevron flutuante. Aparece no hover, escondida por default.
    direction: -1 esquerda, +1 direita."""
    is_right = direction > 0
    return rx.button(
        rx.icon(
            "chevron-right" if is_right else "chevron-left",
            size=22,
        ),
        on_click=MovieState.scroll_shelf(shelf.title, direction),
        class_name=(
            ("right-2" if is_right else "left-2")
            + " absolute top-1/2 -translate-y-1/2 z-20 "
            "w-10 h-10 rounded-full bg-black/70 hover:bg-black/90 "
            "border border-white/10 text-white "
            "items-center justify-center cursor-pointer "
            "opacity-0 group-hover:opacity-100 transition-opacity duration-200"
        ),
    )


def movie_shelf(shelf: Shelf) -> rx.Component:
    return rx.box(
        rx.flex(
            _shelf_title(shelf),
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
            rx.box(
                rx.flex(
                    rx.foreach(shelf.movies, _card_wrapper),
                    id="shelf-" + shelf.title,
                    class_name=(
                        "gap-3 overflow-x-auto pb-4 px-8 scroll-smooth "
                        # Esconde scrollbar nativo (Chrome/Safari + Firefox)
                        "[&::-webkit-scrollbar]:hidden [scrollbar-width:none]"
                    ),
                ),
                _scroll_btn(shelf, -1),
                _scroll_btn(shelf, +1),
                class_name="relative group",
            ),
            _skeleton_row(),
        ),
        class_name="mb-10",
    )
