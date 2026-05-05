"""Página /feed — reviews dos usuários que o autenticado segue."""

import reflex as rx

from cine_review.components.navbar import navbar
from cine_review.components.review_card import review_card
from cine_review.state.auth_state import AuthState
from cine_review.state.feed_state import FeedState


def _empty() -> rx.Component:
    return rx.flex(
        rx.icon("users", size=24, class_name="text-slate-500"),
        rx.flex(
            rx.text(
                "Seu feed está vazio.",
                class_name="text-slate-300 font-semibold",
            ),
            rx.text(
                "Visite o perfil de outros usuários e siga eles pra ver "
                "as reviews aqui.",
                class_name="text-slate-500 text-sm",
            ),
            class_name="flex-col gap-1 items-center",
        ),
        class_name="flex-col items-center justify-center gap-4 py-24",
    )


def _logged_out() -> rx.Component:
    return rx.flex(
        rx.icon("lock", size=24, class_name="text-slate-500"),
        rx.text(
            "Faça login pra ver seu feed.",
            class_name="text-slate-400",
        ),
        class_name="items-center justify-center gap-2 py-24",
    )


def feed() -> rx.Component:
    return rx.box(
        navbar(),
        rx.box(
            rx.heading("Feed", size="7", class_name="text-white font-bold mb-2"),
            rx.text(
                "Reviews de quem você segue",
                class_name="text-slate-400 text-sm mb-8",
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
                            class_name="gap-3 w-full",
                        ),
                        _empty(),
                    ),
                ),
                _logged_out(),
            ),
            class_name="px-8 max-w-3xl mx-auto pt-12 pb-24",
        ),
        class_name="min-h-screen bg-[#0a0a0f] text-slate-200 font-sans",
    )
