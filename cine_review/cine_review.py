"""Entrypoint do app Reflex."""

import reflex as rx

from cine_review.pages.callback import callback
from cine_review.pages.feed import feed
from cine_review.pages.genre import genre
from cine_review.pages.home import home
from cine_review.pages.movie_detail import movie_detail
from cine_review.pages.profile import profile
from cine_review.pages.search import search
from cine_review.state.auth_state import AuthState
from cine_review.state.feed_state import FeedState
from cine_review.state.genre_state import GenreState
from cine_review.state.movie_detail_state import MovieDetailState
from cine_review.state.movie_state import MovieState
from cine_review.state.profile_state import ProfileState
from cine_review.state.search_state import SearchState  # noqa: F401  (registra)

app = rx.App(
    theme=rx.theme(appearance="dark", accent_color="teal", radius="medium"),
)

app.add_page(
    home,
    route="/",
    title="CineReviews",
    on_load=[MovieState.load_movies],
)

app.add_page(
    movie_detail,
    route="/movie/[id]",
    title="Filme — CineReviews",
    on_load=[MovieDetailState.load_detail],
)

app.add_page(
    search,
    route="/search",
    title="Buscar — CineReviews",
)

app.add_page(
    feed,
    route="/feed",
    title="Feed — CineReviews",
    on_load=[FeedState.load_feed],
)

app.add_page(
    profile,
    route="/user/[name]",
    title="Perfil — CineReviews",
    on_load=[ProfileState.load_profile],
)

app.add_page(
    genre,
    route="/genre/[gname]",
    title="Gênero — CineReviews",
    on_load=[GenreState.load_genre],
)

# Callback do OAuth Auth0. handle_callback faz a troca code→token e
# redireciona pra home.
app.add_page(
    callback,
    route="/callback",
    title="Autenticando — CineReviews",
    on_load=[AuthState.handle_callback],
)
