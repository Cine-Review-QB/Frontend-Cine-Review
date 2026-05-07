"""Pagina /search - busca instantanea de filmes e usuarios."""

import reflex as rx

from cine_review.components.movie_card import movie_card
from cine_review.components.navbar import navbar
from cine_review.state.search_state import SearchState, SearchUser


_TAB_ACTIVE = (
    "bg-teal-400 text-slate-950 shadow-lg shadow-teal-500/15 "
    "border-teal-300"
)
_TAB_INACTIVE = (
    "bg-white/[0.03] text-slate-300 hover:text-white hover:bg-white/[0.06] "
    "border-white/10"
)


def _tabs() -> rx.Component:
    return rx.flex(
        rx.button(
            rx.icon("film", size=15),
            "Filmes",
            on_click=SearchState.set_tab("movies"),
            class_name=rx.cond(
                SearchState.is_movie_tab,
                _TAB_ACTIVE,
                _TAB_INACTIVE,
            )
            + (
                " h-10 px-4 rounded-full border text-sm font-bold "
                "transition flex items-center gap-2 cursor-pointer"
            ),
        ),
        rx.button(
            rx.icon("users", size=15),
            "Social",
            on_click=SearchState.set_tab("users"),
            class_name=rx.cond(
                SearchState.is_social_tab,
                _TAB_ACTIVE,
                _TAB_INACTIVE,
            )
            + (
                " h-10 px-4 rounded-full border text-sm font-bold "
                "transition flex items-center gap-2 cursor-pointer"
            ),
        ),
        class_name=(
            "items-center justify-center gap-2 mt-7 bg-black/20 border "
            "border-white/10 rounded-full p-1 w-fit mx-auto"
        ),
    )


def _search_bar() -> rx.Component:
    return rx.el.form(
        rx.box(
            rx.icon(
                rx.cond(SearchState.is_social_tab, "users", "search"),
                size=20,
                class_name=(
                    "text-slate-400 absolute left-5 top-1/2 "
                    "-translate-y-1/2 pointer-events-none z-10"
                ),
            ),
            rx.el.input(
                placeholder=rx.cond(
                    SearchState.is_social_tab,
                    "Buscar usuarios por username ou bio",
                    "Digite para buscar filmes",
                ),
                value=SearchState.query,
                on_change=SearchState.set_query,
                auto_focus=True,
                type="text",
                class_name=(
                    "w-full bg-[#11151f]/95 border border-white/10 rounded-2xl "
                    "pl-14 pr-14 sm:pr-36 py-4 text-slate-100 text-base "
                    "sm:text-lg placeholder:text-slate-500 shadow-2xl "
                    "shadow-black/20 focus:border-teal-400 focus:outline-none "
                    "focus:ring-4 focus:ring-teal-400/10 transition"
                ),
            ),
            rx.cond(
                SearchState.is_searching,
                rx.spinner(
                    class_name=(
                        "absolute right-5 sm:right-28 top-1/2 -translate-y-1/2 "
                        "text-teal-400"
                    ),
                ),
                rx.fragment(),
            ),
            rx.el.button(
                "Buscar",
                type="submit",
                class_name=(
                    "hidden sm:block absolute right-2 top-1/2 -translate-y-1/2 "
                    "bg-teal-500 hover:bg-teal-400 text-slate-950 font-semibold "
                    "px-5 py-2 rounded-xl transition cursor-pointer"
                ),
            ),
            class_name="relative w-full",
        ),
        on_submit=SearchState.submit_search,
        class_name="max-w-3xl mx-auto px-5 sm:px-8 pt-8 w-full",
    )


def _movie_results() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.foreach(
                SearchState.results,
                lambda m: rx.box(
                    movie_card(m),
                    class_name="w-[45vw] max-w-[170px] sm:w-[180px]",
                ),
            ),
            class_name="flex-wrap gap-3 sm:gap-5 justify-center",
        ),
        class_name="px-4 sm:px-8 pt-8 pb-24 max-w-[1400px] mx-auto",
    )


def _user_avatar(user: SearchUser) -> rx.Component:
    return rx.cond(
        user.has_avatar,
        rx.image(
            src=user.avatar_url,
            alt=user.username,
            referrer_policy="no-referrer",
            class_name=(
                "w-12 h-12 rounded-full object-cover ring-2 ring-white/10 "
                "flex-shrink-0"
            ),
        ),
        rx.flex(
            rx.icon("user", size=20, class_name="text-teal-200"),
            class_name=(
                "w-12 h-12 rounded-full bg-teal-500/20 ring-2 ring-white/10 "
                "items-center justify-center flex-shrink-0"
            ),
        ),
    )


def _user_card(user: SearchUser) -> rx.Component:
    return rx.link(
        rx.flex(
            _user_avatar(user),
            rx.flex(
                rx.flex(
                    rx.text(
                        user.username,
                        class_name="text-white text-sm font-black truncate",
                    ),
                    rx.flex(
                        rx.icon("clapperboard", size=13, class_name="text-slate-500"),
                        rx.text(
                            user.review_count.to_string() + " reviews",
                            class_name="text-slate-400 text-xs font-semibold",
                        ),
                        class_name="items-center gap-1.5",
                    ),
                    class_name=(
                        "items-start sm:items-center justify-between gap-2 "
                        "flex-col sm:flex-row"
                    ),
                ),
                rx.cond(
                    user.has_bio,
                    rx.text(
                        user.bio,
                        class_name="text-slate-400 text-sm line-clamp-2",
                    ),
                    rx.text(
                        "Perfil sem bio.",
                        class_name="text-slate-600 text-sm",
                    ),
                ),
                class_name="flex-col gap-1 min-w-0 flex-1",
            ),
            rx.flex(
                rx.text("Ver perfil", class_name="text-xs font-bold"),
                rx.icon("arrow-up-right", size=13),
                class_name=(
                    "hidden sm:flex items-center gap-1 text-teal-300 "
                    "group-hover:text-teal-200"
                ),
            ),
            class_name="items-center gap-4",
        ),
        href="/user/" + user.username,
        class_name=(
            "group block bg-[#11151f]/95 border border-white/10 rounded-2xl "
            "p-4 hover:border-teal-300/25 hover:-translate-y-0.5 "
            "transition-all shadow-xl shadow-black/10"
        ),
    )


def _user_results() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.foreach(SearchState.user_results, _user_card),
            class_name="gap-3 w-full",
        ),
        class_name="px-5 sm:px-8 pt-8 pb-24 max-w-3xl mx-auto",
    )


def _empty_state() -> rx.Component:
    return rx.flex(
        rx.icon("search-x", size=24, class_name="text-slate-500"),
        rx.text(
            rx.cond(
                SearchState.is_social_tab,
                "Nenhum usuario encontrado.",
                "Nenhum filme encontrado.",
            ),
            class_name="text-slate-400",
        ),
        class_name="items-center justify-center gap-2 py-24",
    )


def _hint() -> rx.Component:
    return rx.flex(
        rx.icon(
            rx.cond(SearchState.is_social_tab, "users", "search"),
            size=24,
            class_name="text-slate-500",
        ),
        rx.text(
            rx.cond(
                SearchState.is_social_tab,
                "Digite um username para descobrir pessoas.",
                "Digite pelo menos duas letras para buscar.",
            ),
            class_name="text-slate-400 text-center",
        ),
        class_name="items-center justify-center gap-2 py-24 px-6",
    )


def _results() -> rx.Component:
    return rx.cond(
        SearchState.is_social_tab,
        rx.cond(
            SearchState.has_user_results,
            _user_results(),
            _empty_state(),
        ),
        rx.cond(
            SearchState.has_results,
            _movie_results(),
            _empty_state(),
        ),
    )


def search() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            rx.flex(
                rx.icon("sparkles", size=18, class_name="text-teal-400"),
                rx.text(
                    rx.cond(SearchState.is_social_tab, "Social", "Busca inteligente"),
                    class_name="text-teal-300 text-xs font-bold uppercase",
                ),
                class_name="items-center justify-center gap-2 pt-10",
            ),
            rx.heading(
                rx.cond(
                    SearchState.is_social_tab,
                    "Encontre pessoas para seguir",
                    "Encontre seu proximo filme",
                ),
                size="8",
                class_name="text-white font-bold text-center mt-3 px-4",
            ),
            rx.text(
                rx.cond(
                    SearchState.is_social_tab,
                    "Pesquise usuarios e abra o perfil para seguir.",
                    "Agora a busca entende termos parciais como poke.",
                ),
                class_name="text-slate-400 text-center text-sm mt-3 px-4",
            ),
            _tabs(),
        ),
        _search_bar(),
        rx.cond(
            SearchState.error != "",
            rx.text(
                SearchState.error,
                class_name="text-red-400 text-sm text-center mt-4 px-4",
            ),
            rx.fragment(),
        ),
        rx.cond(
            SearchState.is_searching,
            rx.flex(
                rx.text("Buscando...", class_name="text-slate-400 text-sm"),
                class_name="items-center justify-center py-8",
            ),
            rx.cond(
                SearchState.has_searched,
                _results(),
                _hint(),
            ),
        ),
        class_name="min-h-screen bg-[#0a0a0f] text-slate-200 font-sans",
    )
