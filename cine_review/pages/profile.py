"""Página /user/[username] — perfil de um usuário."""

import reflex as rx

from cine_review.components.navbar import navbar
from cine_review.components.review_card import review_card
from cine_review.state.auth_state import AuthState
from cine_review.state.profile_state import ProfileState


def _avatar_block() -> rx.Component:
    user = ProfileState.user
    return rx.cond(
        user.has_avatar,
        rx.image(
            src=user.avatar_url,
            alt=user.username,
            referrer_policy="no-referrer",
            class_name=(
                "w-24 h-24 rounded-full object-cover ring-4 ring-white/10 "
                "flex-shrink-0"
            ),
        ),
        rx.flex(
            rx.icon("user", size=42, class_name="text-teal-400"),
            class_name=(
                "w-24 h-24 rounded-full bg-teal-500/20 items-center "
                "justify-center ring-4 ring-white/10 flex-shrink-0"
            ),
        ),
    )


def _follow_button() -> rx.Component:
    return rx.cond(
        ProfileState.is_following,
        rx.button(
            "Deixar de seguir",
            on_click=ProfileState.toggle_follow,
            class_name=(
                "bg-transparent border border-white/20 hover:border-red-400 "
                "hover:text-red-400 text-slate-200 font-semibold "
                "px-5 py-2 rounded-lg cursor-pointer transition"
            ),
        ),
        rx.button(
            "Seguir",
            on_click=ProfileState.toggle_follow,
            class_name=(
                "bg-teal-500 hover:bg-teal-400 text-slate-900 font-semibold "
                "px-5 py-2 rounded-lg cursor-pointer transition"
            ),
        ),
    )


def _stat(value, label: str) -> rx.Component:
    return rx.flex(
        rx.text(
            value.to_string(),
            class_name="text-white font-bold text-base",
        ),
        rx.text(
            label,
            class_name="text-slate-500 text-xs uppercase tracking-wider",
        ),
        class_name="flex-col items-center gap-0.5",
    )


def _header() -> rx.Component:
    user = ProfileState.user
    return rx.flex(
        _avatar_block(),
        rx.flex(
            rx.heading(user.username, size="7", class_name="text-white font-bold"),
            rx.cond(
                user.has_bio,
                rx.text(user.bio, class_name="text-slate-300 text-sm mt-1"),
            ),
            rx.flex(
                _stat(user.review_count, "reviews"),
                rx.box(class_name="w-px h-8 bg-white/10"),
                _stat(user.followers_count, "seguidores"),
                rx.box(class_name="w-px h-8 bg-white/10"),
                _stat(user.following_count, "seguindo"),
                class_name="items-center gap-5 mt-3",
            ),
            class_name="flex-col flex-1",
        ),
        rx.cond(
            ProfileState.is_own_profile,
            rx.fragment(),
            rx.cond(
                AuthState.is_authenticated,
                _follow_button(),
                rx.fragment(),
            ),
        ),
        class_name="items-start gap-6 mb-10",
    )


def _reviews_section() -> rx.Component:
    return rx.box(
        rx.heading(
            "Reviews",
            size="5",
            class_name="text-white font-bold mb-4",
        ),
        rx.cond(
            ProfileState.has_reviews,
            rx.vstack(
                rx.foreach(
                    ProfileState.reviews,
                    lambda r: review_card(
                        r,
                        on_toggle_like=ProfileState.toggle_like,
                        show_movie=True,
                    ),
                ),
                class_name="gap-3 w-full",
            ),
            rx.text(
                "Esse usuário ainda não escreveu reviews.",
                class_name="text-slate-500 text-center py-8",
            ),
        ),
    )


def _logged_out() -> rx.Component:
    return rx.flex(
        rx.icon("lock", size=24, class_name="text-slate-500"),
        rx.text(
            "Faça login pra ver perfis.",
            class_name="text-slate-400",
        ),
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
                        _reviews_section(),
                        class_name="px-8 max-w-3xl mx-auto pt-16 pb-24",
                    ),
                ),
            ),
            _logged_out(),
        ),
        class_name="min-h-screen bg-[#0a0a0f] text-slate-200 font-sans",
    )
