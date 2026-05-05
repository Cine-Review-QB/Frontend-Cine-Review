"""Card de uma review individual.

Reusável em /movie/[id], /feed e /user/[username] — cada página passa
o event handler de toggle_like do seu próprio State.
"""

from typing import Callable, Optional

import reflex as rx

from cine_review.state.auth_state import AuthState
from cine_review.state.movie_detail_state import MovieDetailState, ReviewItem


def _avatar(review: ReviewItem) -> rx.Component:
    return rx.cond(
        review.has_avatar,
        rx.image(
            src=review.avatar_url,
            alt=review.display_name,
            referrer_policy="no-referrer",
            class_name=(
                "w-9 h-9 rounded-full object-cover ring-2 ring-white/10 "
                "flex-shrink-0"
            ),
        ),
        rx.flex(
            rx.icon("user", size=16, class_name="text-teal-400"),
            class_name=(
                "w-9 h-9 rounded-full bg-teal-500/20 items-center "
                "justify-center ring-2 ring-white/10 flex-shrink-0"
            ),
        ),
    )


def _author_link(review: ReviewItem) -> rx.Component:
    """Avatar + nome → link pro perfil do autor."""
    return rx.link(
        rx.flex(
            _avatar(review),
            rx.flex(
                rx.text(
                    review.display_name,
                    class_name=(
                        "text-slate-100 text-sm font-semibold "
                        "hover:text-teal-400 transition-colors"
                    ),
                ),
                rx.text(review.created_str, class_name="text-slate-500 text-xs"),
                class_name="flex-col",
            ),
            class_name="items-center gap-3",
        ),
        href="/user/" + review.username,
        class_name="cursor-pointer",
    )


def _movie_link(review: ReviewItem) -> rx.Component:
    """Header com link pro filme, usado em feed e perfil."""
    return rx.cond(
        review.has_movie_title,
        rx.link(
            rx.flex(
                rx.icon("film", size=12, class_name="text-slate-500"),
                rx.text(
                    review.movie_title,
                    class_name=(
                        "text-slate-300 text-xs font-medium "
                        "hover:text-teal-400 transition-colors"
                    ),
                ),
                class_name="items-center gap-1.5",
            ),
            href="/movie/" + review.movie_id,
            class_name="cursor-pointer mb-3",
        ),
    )


def _like_button(
    review: ReviewItem,
    on_toggle_like,
) -> rx.Component:
    return rx.button(
        rx.flex(
            rx.icon(
                "heart",
                size=14,
                class_name=rx.cond(
                    review.is_liked,
                    "text-red-400 fill-red-400",
                    "text-slate-500",
                ),
            ),
            rx.text(
                review.likes_count.to_string(),
                class_name="text-slate-400 text-xs font-medium",
            ),
            class_name="items-center gap-1.5",
        ),
        on_click=on_toggle_like(review.id),
        disabled=~AuthState.is_authenticated,
        title=rx.cond(
            AuthState.is_authenticated,
            "",
            "Faça login pra curtir",
        ),
        class_name=(
            "bg-transparent hover:bg-white/5 px-2 py-1 rounded transition "
            "cursor-pointer disabled:cursor-not-allowed"
        ),
    )


def _delete_button(review: ReviewItem, on_delete) -> rx.Component:
    """Lixeira com confirmação. Só visível pro autor da review."""
    return rx.cond(
        review.user_id == AuthState.user_id,
        rx.alert_dialog.root(
            rx.alert_dialog.trigger(
                rx.button(
                    rx.icon("trash-2", size=14),
                    title="Apagar minha review",
                    class_name=(
                        "bg-transparent text-slate-500 hover:text-red-400 "
                        "hover:bg-red-500/10 px-2 py-1 rounded transition cursor-pointer"
                    ),
                ),
            ),
            rx.alert_dialog.content(
                rx.alert_dialog.title(
                    "Apagar review?",
                    class_name="text-white font-bold text-lg",
                ),
                rx.alert_dialog.description(
                    "Essa ação não pode ser desfeita. A review e os likes "
                    "associados serão removidos permanentemente.",
                    class_name="text-slate-300 text-sm mt-2 mb-5",
                ),
                rx.flex(
                    rx.alert_dialog.cancel(
                        rx.button(
                            "Cancelar",
                            class_name=(
                                "bg-transparent border border-white/15 "
                                "hover:border-white/30 text-slate-200 "
                                "px-4 py-2 rounded-md cursor-pointer"
                            ),
                        ),
                    ),
                    rx.alert_dialog.action(
                        rx.button(
                            "Apagar",
                            on_click=on_delete(review.id),
                            class_name=(
                                "bg-red-500 hover:bg-red-600 text-white "
                                "font-semibold px-4 py-2 rounded-md cursor-pointer"
                            ),
                        ),
                    ),
                    class_name="gap-3 justify-end",
                ),
                class_name="bg-[#13161e] border border-white/10 max-w-md",
            ),
        ),
    )


def review_card(
    review: ReviewItem,
    on_toggle_like=None,
    on_delete=None,
    show_movie: bool = False,
) -> rx.Component:
    """Card reusável.

    Args:
        review: dados da review (já formatados)
        on_toggle_like: event handler que recebe review_id (default
            MovieDetailState.toggle_like — usado em /movie/[id])
        on_delete: event handler que recebe review_id, ou None pra
            ocultar o botão de apagar
        show_movie: True pra mostrar link do filme no topo (feed/perfil)
    """
    if on_toggle_like is None:
        on_toggle_like = MovieDetailState.toggle_like

    footer_items = [_like_button(review, on_toggle_like)]
    if on_delete is not None:
        footer_items.append(_delete_button(review, on_delete))

    children: list[rx.Component] = []
    if show_movie:
        children.append(_movie_link(review))

    children.extend([
        # Header (autor + rating)
        rx.flex(
            _author_link(review),
            rx.flex(
                rx.icon("star", size=14, class_name="text-amber-400 fill-amber-400"),
                rx.text(
                    review.rating_str,
                    class_name="text-amber-400 text-sm font-bold",
                ),
                class_name="items-center gap-1",
            ),
            class_name="items-center justify-between mb-3",
        ),
        # Texto
        rx.cond(
            review.has_text,
            rx.text(
                review.text,
                class_name="text-slate-300 text-sm leading-relaxed mb-3",
            ),
        ),
        # Footer (like + delete)
        rx.flex(
            *footer_items,
            class_name="items-center justify-between",
        ),
    ])

    return rx.box(
        *children,
        class_name=(
            "bg-[#13161e] border border-white/5 rounded-lg p-4 "
            "hover:border-white/15 transition w-full"
        ),
    )
