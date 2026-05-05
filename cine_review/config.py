"""Configurações lidas de variáveis de ambiente."""

import os

# Toda comunicação passa pelo API Gateway (Cine-Api-Gateway).
# Override via env apenas se o Gateway estiver em outra máquina/porta.
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
