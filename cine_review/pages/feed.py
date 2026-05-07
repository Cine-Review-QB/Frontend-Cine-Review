"""Pagina /feed - reviews dos usuarios seguidos."""

import reflex as rx

from cine_review.components.navbar import navbar
from cine_review.components.review_card import review_card
from cine_review.state.auth_state import AuthState
from cine_review.state.feed_state import FeedState


def _empty() -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.icon("users", size=28, class_name="text-slate-500"),
            class_name=(
                "w-16 h-16 rounded-full border border-white/10 items-center "
                "justify-center bg-white/[0.02]"
            ),
        ),
        rx.text("Seu feed esta vazio.", class_name="text-slate-200 font-bold"),
        rx.text(
            "Siga outros usuarios para ver novas reviews aqui.",
            class_name="text-slate-500 text-sm text-center",
        ),
        class_name="flex-col items-center justify-center gap-3 py-24",
    )


def _logged_out() -> rx.Component:
    return rx.flex(
        rx.icon("lock", size=24, class_name="text-slate-500"),
        rx.text("Faca login pra ver seu feed.", class_name="text-slate-400"),
        class_name="items-center justify-center gap-2 py-24",
    )


def feed() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            rx.flex(
                rx.box(
                    rx.flex(
                        rx.icon("messages-square", size=18, class_name="text-teal-300"),
                        rx.text(
                            "Social",
                            class_name="text-teal-300 text-xs font-bold uppercase",
                        ),
                        class_name="items-center gap-2 mb-3",
                    ),
                    rx.heading(
                        "Feed",
                        size="8",
                        class_name="text-white font-black tracking-normal",
                    ),
                    rx.text(
                        "Reviews recentes de quem voce segue",
                        class_name="text-slate-400 text-sm mt-2",
                    ),
                    class_name="min-w-0",
                ),
                class_name="items-end justify-between gap-4 mb-8",
            ),
            rx.cond(
                AuthState.is_authenticated,
                rx.cond(
                    FeedState.is_loading,
                    rx.flex(
                        rx.spinner(class_name="text-teal-400"),
                        class_name="items-center justify-center py-12",
                    ),
                    rx.cond(
                        FeedState.has_items,
                        rx.vstack(
                            rx.foreach(
                                FeedState.items,
                                lambda r: review_card(
                                    r,
                                    on_toggle_like=FeedState.toggle_like,
                                    show_movie=True,
                                ),
                            ),
                            class_name="gap-4 w-full",
                        ),
                        _empty(),
                    ),
                ),
                _logged_out(),
            ),
            class_name="px-5 sm:px-8 max-w-3xl mx-auto pt-10 sm:pt-14 pb-24",
        ),
        class_name="min-h-screen bg-[#0a0a0f] text-slate-200 font-sans",
    )
