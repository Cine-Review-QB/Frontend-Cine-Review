"""Página /search — input + grid de resultados."""

import reflex as rx

from cine_review.components.movie_card import movie_card
from cine_review.components.navbar import navbar
from cine_review.state.search_state import SearchState


def _search_bar() -> rx.Component:
    """Form HTML nativo — Enter dentro do input dispara on_submit.
    Usamos rx.el.input (e não rx.input) pra evitar styling default
    do Radix que comprimia o campo."""
    return rx.el.form(
        rx.box(
            rx.icon(
                "search",
                size=20,
                class_name=(
                    "text-slate-400 absolute left-5 top-1/2 "
                    "-translate-y-1/2 pointer-events-none z-10"
                ),
            ),
            rx.el.input(
                placeholder="Buscar por título",
                value=SearchState.query,
                on_change=SearchState.set_query,
                auto_focus=True,
                type="text",
                class_name=(
                    "w-full bg-[#13161e] border border-white/10 rounded-lg "
                    "pl-14 pr-32 py-4 text-slate-200 text-lg "
                    "placeholder:text-slate-500 "
                    "focus:border-teal-400 focus:outline-none"
                ),
            ),
            rx.el.button(
                "Buscar",
                type="submit",
                class_name=(
                    "absolute right-2 top-1/2 -translate-y-1/2 "
                    "bg-teal-500 hover:bg-teal-400 text-slate-900 font-semibold "
                    "px-5 py-2 rounded-md transition cursor-pointer"
                ),
            ),
            class_name="relative w-full",
        ),
        on_submit=SearchState.submit_search,
        class_name="max-w-3xl mx-auto px-8 pt-12 w-full",
    )


def _results_grid() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.foreach(
                SearchState.results,
                lambda m: rx.box(movie_card(m), class_name="w-[180px]"),
            ),
            class_name="flex-wrap gap-4 justify-center",
        ),
        class_name="px-8 pt-10 pb-24 max-w-[1400px] mx-auto",
    )


def _empty_state() -> rx.Component:
    return rx.flex(
        rx.icon("search-x", size=24, class_name="text-slate-500"),
        rx.text(
            "Nenhum resultado encontrado.",
            class_name="text-slate-400",
        ),
        class_name="items-center justify-center gap-2 py-24",
    )


def _hint() -> rx.Component:
    return rx.flex(
        rx.icon("search", size=24, class_name="text-slate-500"),
        rx.text(
            "Digite o nome de um filme e pressione Enter.",
            class_name="text-slate-400",
        ),
        class_name="items-center justify-center gap-2 py-24",
    )


def search() -> rx.Component:
    return rx.box(
        navbar(),
        rx.heading(
            "Buscar filmes",
            size="7",
            class_name="text-white font-bold text-center pt-12",
        ),
        _search_bar(),
        rx.cond(
            SearchState.is_searching,
            rx.flex(
                rx.spinner(class_name="text-teal-400"),
                rx.text("Buscando...", class_name="text-slate-400 ml-3"),
                class_name="items-center justify-center py-12",
            ),
            rx.cond(
                SearchState.has_searched,
                rx.cond(
                    SearchState.has_results,
                    _results_grid(),
                    _empty_state(),
                ),
                _hint(),
            ),
        ),
        class_name="min-h-screen bg-[#0a0a0f] text-slate-200 font-sans",
    )
