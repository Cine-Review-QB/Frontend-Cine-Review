"""Formulário de escrever review: slider de nota + textarea + submit."""

import reflex as rx

from cine_review.state.movie_detail_state import MovieDetailState


def review_form() -> rx.Component:
    return rx.box(
        rx.heading(
            "Escrever review",
            size="4",
            class_name="text-white font-semibold mb-4",
        ),
        # Slider de nota
        rx.flex(
            rx.text(
                "Nota",
                class_name="text-slate-400 text-xs uppercase tracking-wider",
            ),
            rx.box(
                rx.slider(
                    default_value=[5.0],
                    min=0.5,
                    max=5.0,
                    step=0.5,
                    on_change=MovieDetailState.set_form_rating,
                ),
                class_name="flex-1",
            ),
            rx.flex(
                rx.icon("star", size=14, class_name="text-amber-400 fill-amber-400"),
                rx.text(
                    MovieDetailState.form_rating_str,
                    class_name="text-amber-400 font-bold text-sm w-8",
                ),
                class_name="items-center gap-1",
            ),
            class_name="items-center gap-4 mb-4",
        ),
        # Textarea
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
        # Erro / sucesso
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
        # Submit
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
        class_name=(
            "bg-[#13161e] border border-white/10 rounded-lg p-5 w-full"
        ),
    )
