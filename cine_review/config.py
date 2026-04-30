"""Configurações lidas de variáveis de ambiente."""

import os

CONTENT_API_URL = os.environ.get("CONTENT_API_URL", "http://localhost:5000")
GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://localhost:8000")

GENRES_TO_SHOW = [
    "Drama",
    "Action",
    "Science Fiction",
    "Comedy",
    "Romance",
    "Thriller",
]

MOVIES_PER_SHELF = 15
INITIAL_FETCH_LIMIT = 100
