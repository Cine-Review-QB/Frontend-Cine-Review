"""Formulário de escrever review: estrelas (0.5–5) + textarea + submit."""

import reflex as rx

from cine_review.state.movie_detail_state import MovieDetailState


def _star_slot(position: int) -> rx.Component:
    """Estrela com 2 zonas de clique e hover. Usa form_rating_display
    (hover quando ativo, real caso contrário) pra decidir o preenchimento."""
    rating = MovieDetailState.form_rating_display
    return rx.box(
        # Background — sempre cinza vazio
        rx.icon(
            "star",
            size=28,
            class_name="text-slate-700",
        ),
        # Foreground — cheio quando rating >= position
        rx.cond(
            rating >= position,
            rx.box(
                rx.icon(
                    "star",
                    size=28,
                    class_name="text-amber-400 fill-amber-400",
                ),
                class_name="absolute inset-0",
            ),
            # Meio — quando rating >= position - 0.5 (e < position)
            rx.cond(
                rating >= position - 0.5,
                rx.box(
                    rx.icon(
                        "star",
                        size=28,
                        class_name="text-amber-400 fill-amber-400",
                    ),
                    class_name="absolute inset-0 overflow-hidden",
                    style={"clipPath": "inset(0 50% 0 0)"},
                ),
            ),
        ),
        # Zona esquerda → meia estrela
        rx.box(
            on_click=MovieDetailState.set_form_rating_value(position - 0.5),
            on_mouse_enter=MovieDetailState.set_form_rating_hover(position - 0.5),
            title=f"{position - 0.5}",
            class_name=(
                "absolute left-0 top-0 w-1/2 h-full cursor-pointer z-10"
            ),
        ),
        # Zona direita → estrela cheia
        rx.box(
            on_click=MovieDetailState.set_form_rating_value(position),
            on_mouse_enter=MovieDetailState.set_form_rating_hover(position),
            title=f"{position}",
            class_name=(
                "absolute right-0 top-0 w-1/2 h-full cursor-pointer z-10"
            ),
        ),
        class_name="relative w-7 h-7 hover:scale-110 transition-transform",
    )


def _star_picker() -> rx.Component:
    return rx.flex(
        _star_slot(1),
        _star_slot(2),
        _star_slot(3),
        _star_slot(4),
        _star_slot(5),
        # Saiu do widget — limpa o hover, volta a mostrar o real
        on_mouse_leave=MovieDetailState.clear_form_rating_hover,
        class_name="items-center gap-1",
    )


def review_form() -> rx.Component:
    return rx.box(
        rx.heading(
            "Escrever review",
            size="4",
            class_name="text-white font-semibold mb-4",
        ),
        # Linha de nota: label + estrelas + valor numérico
        rx.flex(
            rx.text(
                "Nota",
                class_name="text-slate-400 text-xs uppercase tracking-wider w-12",
            ),
            _star_picker(),
            rx.text(
                MovieDetailState.form_rating_str,
                class_name="text-amber-400 font-bold text-base w-10",
            ),
            class_name="items-center gap-4 mb-4",
        ),
        rx.text_area(
            placeholder="Escreva sua review (opcional, máx 1000 caracteres)",
            value=MovieDetailState.form_text,
            on_change=MovieDetailState.set_form_text,
            class_name=(
                "w-full bg-[#0a0a0f] border border-white/10 rounded-md p-3 "
                "text-slate-200 text-sm focus:border-teal-400 focus:outline-none "
                "resize-none mb-3"
            ),
            rows="4",
        ),
        rx.cond(
            MovieDetailState.form_error != "",
            rx.flex(
                rx.icon("triangle-alert", size=14, class_name="text-red-400"),
                rx.text(
                    MovieDetailState.form_error,
                    class_name="text-red-400 text-sm",
                ),
                class_name="items-center gap-2 mb-3",
            ),
        ),
        rx.cond(
            MovieDetailState.form_success,
            rx.flex(
                rx.icon("circle-check", size=14, class_name="text-teal-400"),
                rx.text(
                    "Review publicada!",
                    class_name="text-teal-400 text-sm",
                ),
                class_name="items-center gap-2 mb-3",
            ),
        ),
        rx.button(
            rx.cond(
                MovieDetailState.form_submitting,
                "Publicando...",
                "Publicar review",
            ),
            on_click=MovieDetailState.submit_review,
            disabled=MovieDetailState.form_submitting,
            class_name=(
                "bg-teal-500 hover:bg-teal-400 text-slate-900 font-semibold "
                "px-6 py-2 rounded-lg disabled:opacity-50 cursor-pointer transition"
            ),
        ),
        id="review-form",
        class_name=(
            "bg-[#13161e] border border-white/10 rounded-lg p-5 w-full"
        ),
    )
