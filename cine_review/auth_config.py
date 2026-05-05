"""Configurações de autenticação Auth0.

Os valores reais vêm de variáveis de ambiente (.env). Enquanto o tenant
Auth0 não estiver criado, os defaults vazios fazem `start_login` exibir
um aviso amigável em vez de gerar URL inválida.
"""

import os

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "")
AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID", "")
AUTH0_AUDIENCE = os.environ.get("AUTH0_AUDIENCE", "https://api.cinereviews.com")

# URL pra onde o Auth0 redireciona após autenticar. Tem que ser
# registrada exatamente igual em "Allowed Callback URLs" no dashboard.
AUTH0_REDIRECT_URI = os.environ.get(
    "AUTH0_REDIRECT_URI", "http://localhost:3000/callback"
)

# URL pra onde o Auth0 manda após /v2/logout. Também precisa estar
# em "Allowed Logout URLs" no dashboard.
AUTH0_LOGOUT_RETURN_TO = os.environ.get(
    "AUTH0_LOGOUT_RETURN_TO", "http://localhost:3000"
)


def is_configured() -> bool:
    """True quando o tenant Auth0 está configurado e dá pra logar."""
    return bool(AUTH0_DOMAIN and AUTH0_CLIENT_ID)
