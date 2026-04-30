"""Entrypoint do app Reflex."""

import reflex as rx

from cine_review.pages.home import home
from cine_review.state.movie_state import MovieState

app = rx.App(
    theme=rx.theme(appearance="dark", accent_color="teal", radius="medium"),
)

app.add_page(
    home,
    route="/",
    title="CineReviews",
    on_load=[MovieState.load_movies],
)
