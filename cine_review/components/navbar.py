"""Barra de navegação superior. Mostra Feed e Perfil mesmo desabilitados — o usuário precisa ver pra onde a plataforma vai."""

import reflex as rx


def _nav_link(label: str, href: str = "#", disabled: bool = False) -> rx.Component:
    if disabled:
        return rx.box(
            label,
            class_name=(
                "text-slate-600 cursor-not-allowed text-sm font-medium px-3 py-2 "
                "select-none"
            ),
            title="Em breve",
        )
    return rx.link(
        label,
        href=href,
        class_name=(
            "text-slate-300 hover:text-teal-400 text-sm font-medium px-3 py-2 "
            "transition-colors"
        ),
    )


def navbar() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.flex(
                rx.heading(
                    "CineReviews",
                    size="6",
                    class_name="text-teal-400 font-bold tracking-tight",
                ),
                rx.flex(
                    _nav_link("Início", href="/"),
                    _nav_link("Buscar", disabled=True),
                    _nav_link("Feed", disabled=True),
                    class_name="items-center gap-1 ml-8",
                ),
                class_name="items-center",
            ),
            rx.button(
                "Entrar",
                disabled=True,
                title="Em breve — login via Auth0",
                class_name=(
                    "bg-teal-500 hover:bg-teal-400 text-slate-900 font-semibold "
                    "px-5 py-2 rounded-lg transition-colors disabled:opacity-40 "
                    "disabled:cursor-not-allowed"
                ),
            ),
            class_name=(
                "items-center justify-between max-w-[1400px] mx-auto px-8 py-4"
            ),
        ),
        class_name=(
            "sticky top-0 z-50 backdrop-blur-md bg-[#0a0a0f]/80 "
            "border-b border-white/5"
        ),
    )
