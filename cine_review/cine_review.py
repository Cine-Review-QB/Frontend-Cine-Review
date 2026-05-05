"""Entrypoint do app Reflex."""

import reflex as rx

from cine_review.pages.callback import callback
from cine_review.pages.home import home
from cine_review.state.auth_state import AuthState
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

# Callback do OAuth Auth0. handle_callback faz a troca code→token e
# redireciona pra home.
app.add_page(
    callback,
    route="/callback",
    title="Autenticando — CineReviews",
    on_load=[AuthState.handle_callback],
)
