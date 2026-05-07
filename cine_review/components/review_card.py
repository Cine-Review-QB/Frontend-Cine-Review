"""Card reutilizavel para reviews."""

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
                "w-11 h-11 rounded-full object-cover ring-2 ring-white/10 "
                "flex-shrink-0 transition-transform group-hover:scale-105"
            ),
        ),
        rx.flex(
            rx.icon("user", size=17, class_name="text-teal-200"),
            class_name=(
                "w-11 h-11 rounded-full bg-gradient-to-br from-teal-500/50 "
                "to-sky-500/30 items-center justify-center ring-2 "
                "ring-white/10 flex-shrink-0"
            ),
        ),
    )


def _author_link(review: ReviewItem) -> rx.Component:
    return rx.link(
        rx.flex(
            _avatar(review),
            rx.flex(
                rx.text(
                    review.display_name,
                    class_name=(
                        "text-slate-100 text-sm font-bold leading-tight "
                        "group-hover:text-teal-300 transition-colors truncate"
                    ),
                ),
                rx.text(review.created_str, class_name="text-slate-500 text-xs"),
                class_name="flex-col min-w-0",
            ),
            class_name="items-center gap-3 min-w-0 group",
        ),
        href="/user/" + review.username,
        class_name="cursor-pointer min-w-0",
    )


def _movie_link(review: ReviewItem) -> rx.Component:
    return rx.cond(
        review.has_movie_title,
        rx.link(
            rx.flex(
                rx.icon("film", size=13, class_name="text-teal-300"),
                rx.text(
                    review.movie_title,
                    class_name=(
                        "text-teal-100 text-xs font-bold truncate "
                        "hover:text-teal-300 transition-colors"
                    ),
                ),
                class_name="items-center gap-2 min-w-0",
            ),
            href="/movie/" + review.movie_id,
            class_name=(
                "inline-flex max-w-full bg-teal-500/10 border border-teal-400/10 "
                "rounded-full px-3 py-1 mb-4"
            ),
        ),
        rx.fragment(),
    )


def _rating(review: ReviewItem) -> rx.Component:
    return rx.flex(
        rx.icon("star", size=15, class_name="text-amber-300 fill-amber-300"),
        rx.text(review.rating_str, class_name="text-amber-200 text-sm font-black"),
        class_name=(
            "items-center gap-1 bg-amber-400/10 border border-amber-300/10 "
            "px-2.5 py-1.5 rounded-full flex-shrink-0"
        ),
    )


def _like_button(review: ReviewItem, on_toggle_like) -> rx.Component:
    return rx.button(
        rx.flex(
            rx.icon(
                "heart",
                size=16,
                class_name=rx.cond(
                    review.is_liked,
                    "text-red-400 fill-red-400",
                    "text-slate-500",
                ),
            ),
            rx.text(
                review.likes_count.to_string(),
                class_name="text-slate-400 text-xs font-semibold",
            ),
            class_name="items-center gap-1.5",
        ),
        on_click=on_toggle_like(review.id),
        disabled=~AuthState.is_authenticated,
        title=rx.cond(AuthState.is_authenticated, "", "Faca login pra curtir"),
        class_name=(
            "bg-white/0 hover:bg-white/5 px-2.5 py-1.5 rounded-full transition "
            "cursor-pointer disabled:cursor-not-allowed"
        ),
    )


def _delete_button(review: ReviewItem, on_delete) -> rx.Component:
    return rx.cond(
        review.user_id == AuthState.user_id,
        rx.alert_dialog.root(
            rx.alert_dialog.trigger(
                rx.button(
                    rx.icon("trash-2", size=15),
                    title="Apagar minha review",
                    class_name=(
                        "bg-transparent text-slate-500 hover:text-red-300 "
                        "hover:bg-red-500/10 px-2.5 py-1.5 rounded-full "
                        "transition cursor-pointer"
                    ),
                ),
            ),
            rx.alert_dialog.content(
                rx.alert_dialog.title(
                    "Apagar review?",
                    class_name="text-white font-bold text-lg",
                ),
                rx.alert_dialog.description(
                    "Essa acao nao pode ser desfeita. A review e os likes "
                    "associados serao removidos permanentemente.",
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
        rx.fragment(),
    )


def review_card(
    review: ReviewItem,
    on_toggle_like=None,
    on_delete=None,
    show_movie: bool = False,
) -> rx.Component:
    if on_toggle_like is None:
        on_toggle_like = MovieDetailState.toggle_like

    footer_items = [_like_button(review, on_toggle_like)]
    if on_delete is not None:
        footer_items.append(_delete_button(review, on_delete))

    children: list[rx.Component] = []
    if show_movie:
        children.append(_movie_link(review))

    children.extend(
        [
            rx.flex(
                _author_link(review),
                _rating(review),
                class_name="items-start justify-between gap-4 mb-4",
            ),
            rx.cond(
                review.has_text,
                rx.text(
                    review.text,
                    class_name=(
                        "text-slate-200 text-sm sm:text-[15px] leading-relaxed "
                        "mb-5 whitespace-pre-wrap break-words"
                    ),
                ),
                rx.text(
                    "Review sem comentario.",
                    class_name="text-slate-500 text-sm mb-5",
                ),
            ),
            rx.flex(
                rx.flex(*footer_items, class_name="items-center gap-1"),
                rx.link(
                    rx.flex(
                        rx.text("Abrir filme", class_name="text-xs font-semibold"),
                        rx.icon("arrow-up-right", size=13),
                        class_name="items-center gap-1",
                    ),
                    href="/movie/" + review.movie_id,
                    class_name=(
                        "text-slate-500 hover:text-teal-300 transition-colors"
                    ),
                ),
                class_name="items-center justify-between pt-3 border-t border-white/5",
            ),
        ]
    )

    return rx.box(
        *children,
        class_name=(
            "relative overflow-hidden bg-[#11151f]/95 border border-white/10 "
            "rounded-2xl p-4 sm:p-5 w-full shadow-xl shadow-black/10 "
            "hover:border-teal-300/25 hover:-translate-y-0.5 "
            "hover:shadow-teal-500/5 transition-all duration-200"
        ),
    )
