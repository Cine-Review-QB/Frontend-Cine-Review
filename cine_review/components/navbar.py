"""Barra de navegacao superior responsiva."""

import reflex as rx

from cine_review.components.login_button import login_button


def _nav_link(label: str, href: str, icon: str) -> rx.Component:
    return rx.link(
        rx.flex(
            rx.icon(icon, size=15),
            rx.text(label, class_name="hidden sm:block"),
            class_name="items-center gap-2",
        ),
        href=href,
        class_name=(
            "text-slate-300 hover:text-teal-300 text-sm font-semibold "
            "px-2.5 sm:px-3 py-2 rounded-full hover:bg-white/5 transition"
        ),
    )


def navbar() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.flex(
                rx.link(
                    rx.flex(
                        rx.box(
                            class_name=(
                                "w-2.5 h-2.5 rounded-full bg-teal-400 "
                                "shadow-[0_0_18px_rgba(45,212,191,0.8)]"
                            ),
                        ),
                        rx.heading(
                            "CineReviews",
                            size="5",
                            class_name=(
                                "text-teal-300 font-black tracking-normal "
                                "hover:text-teal-200 transition-colors"
                            ),
                        ),
                        class_name="items-center gap-2",
                    ),
                    href="/",
                ),
                rx.flex(
                    _nav_link("Inicio", "/", "home"),
                    _nav_link("Buscar", "/search", "search"),
                    _nav_link("Feed", "/feed", "messages-square"),
                    class_name=(
                        "items-center gap-1 ml-0 sm:ml-6 order-3 sm:order-none "
                        "w-full sm:w-auto justify-center sm:justify-start"
                    ),
                ),
                class_name=(
                    "items-center gap-3 sm:gap-0 flex-wrap sm:flex-nowrap "
                    "min-w-0"
                ),
            ),
            login_button(),
            class_name=(
                "items-center justify-between gap-4 max-w-[1400px] mx-auto "
                "px-4 sm:px-8 py-3 sm:py-4 flex-wrap sm:flex-nowrap"
            ),
        ),
        class_name=(
            "sticky top-0 z-50 backdrop-blur-xl bg-[#07080d]/85 "
            "border-b border-white/10 shadow-lg shadow-black/10"
        ),
    )
