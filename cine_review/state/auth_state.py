"""Estado de autenticação. Implementa OAuth Authorization Code + PKCE com Auth0.

Sem client secret — padrão para Single Page Apps. O code_verifier vive em
SessionStorage durante o handshake; tokens vivem em LocalStorage para
sobreviver F5.
"""

import base64
import hashlib
import json
import logging
import secrets
from urllib.parse import urlencode

import httpx
import reflex as rx

from cine_review.auth_config import (
    AUTH0_AUDIENCE,
    AUTH0_CLIENT_ID,
    AUTH0_DOMAIN,
    AUTH0_LOGOUT_RETURN_TO,
    AUTH0_REDIRECT_URI,
    is_configured,
)
from cine_review.config import GATEWAY_URL

logger = logging.getLogger(__name__)


def _decode_jwt_payload(token: str) -> dict:
    """Decodifica o payload do JWT sem verificar assinatura.

    Seguro porque o token vem direto do Auth0 via TLS — não é input não
    confiável. A verificação de assinatura é responsabilidade do Gateway
    quando ele recebe o Bearer.
    """
    parts = token.split(".")
    if len(parts) < 2:
        return {}
    payload = parts[1]
    padding = "=" * (-len(payload) % 4)
    try:
        decoded = base64.urlsafe_b64decode(payload + padding)
        return json.loads(decoded)
    except (ValueError, json.JSONDecodeError):
        return {}


def _make_pkce() -> tuple[str, str]:
    """Gera (code_verifier, code_challenge) para PKCE com método S256."""
    verifier = secrets.token_urlsafe(64)
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
        .decode()
        .rstrip("=")
    )
    return verifier, challenge


class AuthState(rx.State):
    """Identidade do usuário autenticado + handlers do fluxo OAuth."""

    # Persistido em LocalStorage (sobrevive reload da página).
    access_token: str = rx.LocalStorage("")
    user_id: str = rx.LocalStorage("")
    username: str = rx.LocalStorage("")
    avatar_url: str = rx.LocalStorage("")

    # Usado entre o redirect pro /authorize e o /callback. Em LocalStorage
    # (não SessionStorage) por timing — Reflex 0.9 não garante persistência
    # de SessionStorage antes de rx.redirect externo, e o verifier era
    # perdido na volta do Auth0.
    code_verifier: str = rx.LocalStorage("")

    # Mensagem de erro para exibir na UI quando algo falhar.
    auth_error: str = ""

    @rx.var
    def is_authenticated(self) -> bool:
        return self.access_token != ""

    @rx.var
    def display_name(self) -> str:
        return self.username if self.username else "perfil"

    @rx.event
    def start_login(self):
        """Botão 'Entrar' → redireciona pro /authorize do Auth0."""
        if not is_configured():
            self.auth_error = (
                "Auth0 ainda não configurado. Defina AUTH0_DOMAIN e "
                "AUTH0_CLIENT_ID no .env do frontend."
            )
            return None

        verifier, challenge = _make_pkce()
        self.code_verifier = verifier
        self.auth_error = ""

        params = {
            "client_id": AUTH0_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": AUTH0_REDIRECT_URI,
            "scope": "openid profile email",
            "audience": AUTH0_AUDIENCE,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
        url = f"https://{AUTH0_DOMAIN}/authorize?{urlencode(params)}"
        return rx.redirect(url, is_external=True)

    @rx.event
    async def handle_callback(self):
        """on_load da página /callback. Roda no backend Reflex.

        Lê o `code` da query string, troca por tokens via /oauth/token,
        decodifica o id_token para popular o perfil e redireciona pra home.
        """
        params = self.router.url.query_parameters
        code = params.get("code", "")
        oauth_error = params.get("error", "")

        if oauth_error:
            self.auth_error = (
                f"Auth0 retornou erro: {oauth_error} — "
                f"{params.get('error_description', '')}"
            )
            return rx.redirect("/")

        if not code:
            self.auth_error = "Código de autorização ausente no callback."
            return rx.redirect("/")

        if not self.code_verifier:
            self.auth_error = (
                "Sessão expirada (code_verifier perdido). Tente entrar de novo."
            )
            return rx.redirect("/")

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.post(
                    f"https://{AUTH0_DOMAIN}/oauth/token",
                    data={
                        "grant_type": "authorization_code",
                        "client_id": AUTH0_CLIENT_ID,
                        "code_verifier": self.code_verifier,
                        "code": code,
                        "redirect_uri": AUTH0_REDIRECT_URI,
                    },
                )
        except httpx.RequestError as e:
            self.auth_error = f"Falha ao contatar Auth0: {e}"
            return rx.redirect("/")

        if r.status_code != 200:
            self.auth_error = (
                f"Troca do code por token falhou: HTTP {r.status_code} — "
                f"{r.text[:200]}"
            )
            return rx.redirect("/")

        tokens = r.json()
        access_token = tokens.get("access_token", "")
        id_token = tokens.get("id_token", "")

        if not access_token:
            self.auth_error = "Auth0 não retornou access_token."
            return rx.redirect("/")

        self.access_token = access_token

        claims = _decode_jwt_payload(id_token)
        self.user_id = claims.get("sub", "")
        self.username = (
            claims.get("nickname")
            or claims.get("preferred_username")
            or claims.get("name")
            or (claims.get("email") or "").split("@")[0]
            or "user"
        )
        self.avatar_url = claims.get("picture", "")

        # Verifier é uso único — limpa.
        self.code_verifier = ""

        # Garante que o perfil existe no Cine-Users.
        await self._ensure_profile()

        return rx.redirect("/")

    @rx.event
    def logout(self):
        """Limpa state local e redireciona pro logout do Auth0."""
        self.access_token = ""
        self.user_id = ""
        self.username = ""
        self.avatar_url = ""
        self.auth_error = ""

        if not is_configured():
            return rx.redirect("/")

        params = {
            "client_id": AUTH0_CLIENT_ID,
            "returnTo": AUTH0_LOGOUT_RETURN_TO,
        }
        return rx.redirect(
            f"https://{AUTH0_DOMAIN}/v2/logout?{urlencode(params)}",
            is_external=True,
        )

    async def _ensure_profile(self) -> None:
        """Best-effort: cria o perfil no Cine-Users se ainda não existe.

        Falhas aqui não derrubam o login — o usuário fica autenticado e
        a próxima ação que precise do perfil tenta de novo. Útil porque
        no primeiro login o registro ainda não existe no Postgres.
        """
        if not self.access_token:
            return

        headers = {"Authorization": f"Bearer {self.access_token}"}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                me = await client.get(
                    f"{GATEWAY_URL}/auth/me", headers=headers
                )
                if me.status_code == 404:
                    await client.post(
                        f"{GATEWAY_URL}/auth",
                        headers=headers,
                        json={
                            "username": self.username,
                            "bio": "",
                            "avatarUrl": self.avatar_url,
                        },
                    )
                elif me.status_code == 200:
                    # Perfil existe — sincroniza username caso o usuário
                    # tenha mudado no Cine-Users.
                    data = me.json()
                    if data.get("username"):
                        self.username = data["username"]
                    if data.get("avatarUrl"):
                        self.avatar_url = data["avatarUrl"]
        except httpx.RequestError as e:
            logger.warning(
                "_ensure_profile falhou (best-effort, ignorando): %s", e
            )
