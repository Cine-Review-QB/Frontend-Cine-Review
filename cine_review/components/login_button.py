"""Botão de login na navbar.

Renderiza condicionalmente:
- Não autenticado: botão 'Entrar' que dispara AuthState.start_login.
- Autenticado: avatar/inicial + nome + botão sair.
"""

import reflex as rx

from cine_review.state.auth_state import AuthState


def _avatar() -> rx.Component:
    return rx.cond(
        AuthState.avatar_url != "",
        rx.image(
            src=AuthState.avatar_url,
            alt=AuthState.username,
            referrer_policy="no-referrer",
            class_name=(
                "w-8 h-8 rounded-full object-cover ring-2 ring-teal-500/30"
            ),
        ),
        rx.flex(
            rx.icon("user", size=16, class_name="text-teal-400"),
            class_name=(
                "w-8 h-8 rounded-full bg-teal-500/20 items-center "
                "justify-center ring-2 ring-teal-500/30"
            ),
        ),
    )


def _logged_in() -> rx.Component:
    return rx.flex(
        rx.link(
            rx.flex(
                _avatar(),
                rx.text(
                    AuthState.display_name,
                    class_name=(
                        "text-slate-200 text-sm font-medium hidden sm:block "
                        "hover:text-teal-400 transition-colors"
                    ),
                ),
                class_name="items-center gap-2",
            ),
            href="/user/" + AuthState.username,
            class_name="cursor-pointer",
            title="Meu perfil",
        ),
        rx.button(
            "Sair",
            on_click=AuthState.logout,
            class_name=(
                "bg-transparent border border-white/10 hover:border-white/30 "
                "text-slate-400 hover:text-slate-200 text-xs font-medium "
                "px-3 py-1.5 rounded-md transition cursor-pointer"
            ),
        ),
        class_name="items-center gap-3",
    )


def _logged_out() -> rx.Component:
    return rx.button(
        "Entrar",
        on_click=AuthState.start_login,
        class_name=(
            "bg-teal-500 hover:bg-teal-400 text-slate-900 font-semibold "
            "px-4 py-2 rounded-lg transition cursor-pointer"
        ),
    )


def login_button() -> rx.Component:
    return rx.cond(
        AuthState.is_authenticated,
        _logged_in(),
        _logged_out(),
    )
