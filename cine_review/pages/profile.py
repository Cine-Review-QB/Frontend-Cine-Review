"""Pagina /user/[username] - perfil de um usuario."""

import reflex as rx

from cine_review.components.navbar import navbar
from cine_review.state.auth_state import AuthState
from cine_review.state.movie_detail_state import ReviewItem
from cine_review.state.profile_state import ProfileState


def _avatar_block() -> rx.Component:
    user = ProfileState.user
    avatar_class = (
        "w-28 h-28 md:w-36 md:h-36 rounded-full object-cover "
        "ring-2 ring-white/10 flex-shrink-0"
    )
    fallback_class = (
        "w-28 h-28 md:w-36 md:h-36 rounded-full bg-[#111827] "
        "items-center justify-center ring-2 ring-white/10 flex-shrink-0"
    )
    return rx.cond(
        user.has_avatar,
        rx.image(
            src=user.avatar_url,
            alt=user.username,
            referrer_policy="no-referrer",
            class_name=avatar_class,
        ),
        rx.flex(
            rx.icon("user", size=52, class_name="text-teal-400"),
            class_name=fallback_class,
        ),
    )


def _follow_button() -> rx.Component:
    return rx.cond(
        ProfileState.is_following,
        rx.button(
            rx.icon("user-minus", size=15),
            "Deixar de seguir",
            on_click=ProfileState.toggle_follow,
            class_name=(
                "h-9 bg-transparent border border-white/20 hover:border-red-400 "
                "hover:text-red-400 text-slate-200 text-sm font-semibold px-4 "
                "rounded-md cursor-pointer transition flex items-center gap-2"
            ),
        ),
        rx.button(
            rx.icon("user-plus", size=15),
            "Seguir",
            on_click=ProfileState.toggle_follow,
            class_name=(
                "h-9 bg-teal-500 hover:bg-teal-400 text-slate-950 text-sm "
                "font-semibold px-4 rounded-md cursor-pointer transition "
                "flex items-center gap-2"
            ),
        ),
    )


def _profile_action() -> rx.Component:
    return rx.cond(
        ProfileState.is_own_profile,
        rx.button(
            rx.cond(
                ProfileState.is_editing_bio,
                rx.icon("x", size=15),
                rx.icon("pencil", size=15),
            ),
            rx.cond(ProfileState.is_editing_bio, "Cancelar", "Editar bio"),
            on_click=ProfileState.toggle_bio_edit,
            class_name=(
                "h-9 bg-white/10 hover:bg-white/20 text-slate-100 text-sm "
                "font-semibold px-4 rounded-md cursor-pointer transition "
                "flex items-center gap-2"
            ),
        ),
        rx.cond(
            AuthState.is_authenticated,
            _follow_button(),
            rx.fragment(),
        ),
    )


def _stat(value, label: str) -> rx.Component:
    return rx.flex(
        rx.text(value.to_string(), class_name="text-white text-base font-bold"),
        rx.text(label, class_name="text-slate-400 text-sm"),
        class_name="items-baseline gap-1.5",
    )


def _stats_row() -> rx.Component:
    return rx.flex(
        _stat(ProfileState.user.review_count, "reviews"),
        _stat(ProfileState.user.followers_count, "seguidores"),
        _stat(ProfileState.user.following_count, "seguindo"),
        class_name="items-center gap-5 md:gap-8 flex-wrap",
    )


def _bio_text() -> rx.Component:
    return rx.cond(
        ProfileState.user.has_bio,
        rx.text(
            ProfileState.user.bio,
            class_name=(
                "text-slate-200 text-sm leading-relaxed whitespace-pre-wrap "
                "break-words max-w-2xl"
            ),
        ),
        rx.cond(
            ProfileState.is_own_profile,
            rx.text(
                "Adicione uma bio para seu perfil.",
                class_name="text-slate-500 text-sm",
            ),
            rx.fragment(),
        ),
    )


def _bio_form() -> rx.Component:
    return rx.box(
        rx.text_area(
            value=ProfileState.bio_input,
            on_change=ProfileState.set_bio_input,
            placeholder="Escreva algo sobre você...",
            class_name=(
                "w-full min-h-24 bg-[#10131b] border border-white/10 "
                "rounded-md text-slate-200 text-sm p-3 resize-none "
                "focus:border-teal-400 outline-none"
            ),
        ),
        rx.flex(
            rx.button(
                "Salvar",
                on_click=ProfileState.save_bio,
                is_loading=ProfileState.is_saving_bio,
                class_name=(
                    "bg-teal-500 hover:bg-teal-400 text-slate-950 text-sm "
                    "font-semibold px-4 py-2 rounded-md cursor-pointer transition"
                ),
            ),
            rx.cond(
                ProfileState.bio_error != "",
                rx.text(ProfileState.bio_error, class_name="text-red-400 text-xs"),
                rx.fragment(),
            ),
            class_name="items-center gap-3 mt-3",
        ),
        class_name="max-w-2xl",
    )


def _bio_area() -> rx.Component:
    return rx.cond(
        ProfileState.is_own_profile,
        rx.cond(ProfileState.is_editing_bio, _bio_form(), _bio_text()),
        _bio_text(),
    )


def _header() -> rx.Component:
    user = ProfileState.user
    return rx.box(
        rx.flex(
            _avatar_block(),
            rx.flex(
                rx.flex(
                    rx.heading(
                        user.username,
                        size="6",
                        class_name=(
                            "text-white font-semibold tracking-normal break-words"
                        ),
                    ),
                    _profile_action(),
                    class_name=(
                        "items-start md:items-center justify-between gap-4 "
                        "flex-col md:flex-row w-full"
                    ),
                ),
                _stats_row(),
                _bio_area(),
                class_name="flex-col gap-4 flex-1 min-w-0",
            ),
            class_name="items-start gap-8 md:gap-12 flex-col md:flex-row",
        ),
        class_name="border-b border-white/10 pb-10",
    )


def _tabs() -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.icon("grid-3x3", size=14, class_name="text-teal-400"),
            rx.text("Reviews", class_name="text-slate-100 text-xs font-bold"),
            class_name=(
                "items-center gap-2 h-12 border-t border-teal-400 -mt-px px-4"
            ),
        ),
        class_name="items-center justify-center border-t border-white/10",
    )


def _review_tile(review: ReviewItem) -> rx.Component:
    return rx.box(
        rx.flex(
            rx.link(
                rx.flex(
                    rx.icon("film", size=14, class_name="text-slate-500"),
                    rx.text(
                        rx.cond(
                            review.has_movie_title,
                            review.movie_title,
                            "Filme",
                        ),
                        class_name=(
                            "text-slate-100 text-sm font-semibold truncate "
                            "hover:text-teal-400 transition-colors"
                        ),
                    ),
                    class_name="items-center gap-2 min-w-0",
                ),
                href="/movie/" + review.movie_id,
                class_name="min-w-0",
            ),
            rx.flex(
                rx.icon("star", size=14, class_name="text-amber-400 fill-amber-400"),
                rx.text(review.rating_str, class_name="text-amber-400 text-sm font-bold"),
                class_name="items-center gap-1 flex-shrink-0",
            ),
            class_name="items-center justify-between gap-3",
        ),
        rx.cond(
            review.has_text,
            rx.text(
                review.text,
                class_name=(
                    "text-slate-300 text-sm leading-relaxed mt-5 overflow-hidden "
                    "break-words max-h-28"
                ),
            ),
            rx.flex(
                rx.icon("message-circle", size=18, class_name="text-slate-600"),
                rx.text("Review sem texto", class_name="text-slate-500 text-sm"),
                class_name="items-center justify-center gap-2 mt-8",
            ),
        ),
        rx.flex(
            rx.text(review.created_str, class_name="text-slate-500 text-xs"),
            rx.button(
                rx.icon(
                    "heart",
                    size=15,
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
                on_click=ProfileState.toggle_like(review.id),
                disabled=~AuthState.is_authenticated,
                class_name=(
                    "bg-transparent hover:bg-white/5 px-2 py-1 rounded "
                    "transition cursor-pointer disabled:cursor-not-allowed "
                    "flex items-center gap-1.5"
                ),
            ),
            class_name="items-center justify-between mt-auto pt-5",
        ),
        class_name=(
            "min-h-[13rem] bg-[#11141c] border border-white/10 rounded-md p-4 "
            "flex flex-col hover:border-white/20 transition"
        ),
    )


def _empty_reviews() -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.icon("clapperboard", size=28, class_name="text-slate-500"),
            class_name=(
                "w-16 h-16 rounded-full border border-white/10 items-center "
                "justify-center"
            ),
        ),
        rx.text(
            "Nenhuma review ainda.",
            class_name="text-slate-200 text-sm font-semibold",
        ),
        rx.text(
            "As reviews publicadas aparecem aqui em formato de posts.",
            class_name="text-slate-500 text-sm text-center",
        ),
        class_name="flex-col items-center justify-center gap-3 py-20",
    )


def _reviews_grid() -> rx.Component:
    return rx.box(
        rx.cond(
            ProfileState.has_reviews,
            rx.grid(
                rx.foreach(ProfileState.reviews, lambda r: _review_tile(r)),
                columns="1",
                gap="4",
                class_name="md:grid-cols-2",
            ),
            _empty_reviews(),
        ),
        class_name="w-full",
    )


def _follow_preview(title: str, items, empty_text: str) -> rx.Component:
    return rx.box(
        rx.flex(
            rx.text(title, class_name="text-slate-100 text-sm font-semibold"),
            rx.text(
                items.length().to_string(),
                class_name="text-slate-500 text-xs font-semibold",
            ),
            class_name="items-center justify-between mb-4",
        ),
        rx.cond(
            items.length() > 0,
            rx.vstack(
                rx.foreach(
                    items,
                    lambda u: rx.link(
                        rx.flex(
                            rx.cond(
                                u.has_avatar,
                                rx.image(
                                    src=u.avatar_url,
                                    alt=u.username,
                                    referrer_policy="no-referrer",
                                    class_name=(
                                        "w-9 h-9 rounded-full object-cover ring-1 "
                                        "ring-white/10 flex-shrink-0"
                                    ),
                                ),
                                rx.flex(
                                    rx.icon("user", size=15, class_name="text-teal-400"),
                                    class_name=(
                                        "w-9 h-9 rounded-full bg-teal-500/20 "
                                        "items-center justify-center ring-1 "
                                        "ring-white/10 flex-shrink-0"
                                    ),
                                ),
                            ),
                            rx.text(
                                u.username,
                                class_name=(
                                    "text-slate-300 text-sm font-medium truncate "
                                    "group-hover:text-teal-400 transition-colors"
                                ),
                            ),
                            class_name="items-center gap-3 min-w-0 group",
                        ),
                        href="/user/" + u.username,
                        class_name="w-full",
                    ),
                ),
                class_name="gap-3 max-h-56 overflow-y-auto pr-1",
            ),
            rx.text(
                empty_text,
                class_name="text-slate-500 text-sm",
            ),
        ),
        class_name="border-t border-white/10 pt-5",
    )


def _connections_sidebar() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.flex(
                rx.icon("users", size=16, class_name="text-slate-500"),
                rx.text("Conexões", class_name="text-slate-200 text-sm font-semibold"),
                class_name="items-center gap-2",
            ),
            _follow_preview(
                "Seguidores",
                ProfileState.followers,
                "Sem seguidores por enquanto.",
            ),
            _follow_preview(
                "Seguindo",
                ProfileState.following,
                "Não segue ninguém ainda.",
            ),
            class_name="flex-col gap-5",
        ),
        class_name="w-full lg:w-72 lg:sticky lg:top-28 self-start",
    )


def _content() -> rx.Component:
    return rx.flex(
        rx.box(_reviews_grid(), class_name="flex-1 min-w-0"),
        _connections_sidebar(),
        class_name="gap-10 flex-col lg:flex-row",
    )


def _logged_out() -> rx.Component:
    return rx.flex(
        rx.icon("lock", size=24, class_name="text-slate-500"),
        rx.text("Faça login pra ver perfis.", class_name="text-slate-400"),
        class_name="items-center justify-center gap-2 py-24",
    )


def _error() -> rx.Component:
    return rx.flex(
        rx.icon("triangle-alert", size=24, class_name="text-red-400"),
        rx.text(ProfileState.error, class_name="text-red-400"),
        class_name="items-center justify-center gap-2 py-24",
    )


def profile() -> rx.Component:
    return rx.box(
        navbar(),
        rx.cond(
            AuthState.is_authenticated,
            rx.cond(
                ProfileState.is_loading,
                rx.flex(
                    rx.spinner(class_name="text-teal-400"),
                    class_name="items-center justify-center py-24",
                ),
                rx.cond(
                    ProfileState.error != "",
                    _error(),
                    rx.box(
                        _header(),
                        _tabs(),
                        _content(),
                        class_name="px-5 md:px-8 max-w-5xl mx-auto pt-10 pb-24",
                    ),
                ),
            ),
            _logged_out(),
        ),
        class_name="min-h-screen bg-[#0a0a0f] text-slate-200 font-sans",
    )
