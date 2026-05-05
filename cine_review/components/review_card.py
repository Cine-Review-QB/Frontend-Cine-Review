"""Card de uma review individual: avatar + nome + nota + texto + like + delete."""

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


def _like_button(review: ReviewItem) -> rx.Component:
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
        on_click=MovieDetailState.toggle_like(review.id),
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


def _delete_button(review: ReviewItem) -> rx.Component:
    return rx.cond(
        review.user_id == AuthState.user_id,
        rx.button(
            rx.icon("trash-2", size=14),
            on_click=MovieDetailState.delete_review(review.id),
            title="Apagar minha review",
            class_name=(
                "bg-transparent text-slate-500 hover:text-red-400 "
                "hover:bg-red-500/10 px-2 py-1 rounded transition cursor-pointer"
            ),
        ),
    )


def review_card(review: ReviewItem) -> rx.Component:
    return rx.box(
        # Header
        rx.flex(
            rx.flex(
                _avatar(review),
                rx.flex(
                    rx.text(
                        review.display_name,
                        class_name="text-slate-100 text-sm font-semibold",
                    ),
                    rx.text(
                        review.created_str,
                        class_name="text-slate-500 text-xs",
                    ),
                    class_name="flex-col",
                ),
                class_name="items-center gap-3",
            ),
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
        # Texto da review (se tiver)
        rx.cond(
            review.has_text,
            rx.text(
                review.text,
                class_name="text-slate-300 text-sm leading-relaxed mb-3",
            ),
        ),
        # Footer: like + delete
        rx.flex(
            _like_button(review),
            _delete_button(review),
            class_name="items-center justify-between",
        ),
        class_name=(
            "bg-[#13161e] border border-white/5 rounded-lg p-4 "
            "hover:border-white/15 transition w-full"
        ),
    )
