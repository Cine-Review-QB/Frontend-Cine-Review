"""Página /callback do OAuth Auth0.

Toda a lógica está em AuthState.handle_callback (registrado como on_load
desta página). A UI aqui é só um placeholder visual enquanto o handshake
roda — em condições normais, o usuário só vê "Autenticando..." por menos
de um segundo antes de ser redirecionado.
"""

import reflex as rx

from cine_review.state.auth_state import AuthState


def callback() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.cond(
                AuthState.auth_error == "",
                rx.flex(
                    rx.spinner(class_name="text-teal-400"),
                    rx.text(
                        "Autenticando...",
                        class_name="text-slate-400 ml-3 text-sm",
                    ),
                    class_name="items-center",
                ),
                rx.flex(
                    rx.icon(
                        "triangle-alert",
                        size=32,
                        class_name="text-red-400",
                    ),
                    rx.text(
                        AuthState.auth_error,
                        class_name="text-red-300 text-center mt-3 max-w-md text-sm",
                    ),
                    rx.link(
                        "Voltar para o início",
                        href="/",
                        class_name=(
                            "text-teal-400 hover:text-teal-300 mt-4 text-sm "
                            "underline underline-offset-4"
                        ),
                    ),
                    class_name="flex-col items-center",
                ),
            ),
            class_name="items-center justify-center min-h-screen",
        ),
        class_name="bg-[#0a0a0f] text-slate-200 font-sans",
    )
