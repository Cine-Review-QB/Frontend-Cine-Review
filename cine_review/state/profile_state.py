"""Estado da página de perfil de um usuário."""

from __future__ import annotations

import dataclasses
import logging
from dataclasses import dataclass

import reflex as rx

from cine_review.api import (
    fetch_followers,
    fetch_following,
    fetch_user_by_username,
    fetch_user_reviews,
    follow_user,
    toggle_review_like,
    unfollow_user,
    update_profile,
)
from cine_review.state.auth_state import AuthState
from cine_review.state.movie_detail_state import ReviewItem, _to_review

logger = logging.getLogger(__name__)


@dataclass
class ProfileUser:
    id: str = ""
    auth0_id: str = ""
    username: str = ""
    bio: str = ""
    avatar_url: str = ""
    review_count: int = 0
    followers_count: int = 0
    following_count: int = 0
    has_avatar: bool = False
    has_bio: bool = False


@dataclass
class FollowUser:
    id: str = ""
    username: str = ""
    avatar_url: str = ""
    has_avatar: bool = False


class ProfileState(rx.State):
    user: ProfileUser = ProfileUser()
    reviews: list[ReviewItem] = []
    followers: list[FollowUser] = []
    following: list[FollowUser] = []
    is_following: bool = False
    is_own_profile: bool = False
    is_loading: bool = False
    error: str = ""
    bio_input: str = ""
    is_editing_bio: bool = False
    is_saving_bio: bool = False
    bio_error: str = ""

    def _to_follow_user(self, data: dict, direction: str) -> FollowUser:
        if direction == "followers":
            user_id = data.get("follower_id") or ""
            username = data.get("follower_username") or ""
            avatar = data.get("follower_avatar_url") or ""
        else:
            user_id = data.get("following_id") or ""
            username = data.get("following_username") or ""
            avatar = data.get("following_avatar_url") or ""

        if not username:
            if "|" in user_id:
                username = user_id.split("|")[-1][:12]
            else:
                username = user_id[:12] if user_id else "usuário"

        return FollowUser(
            id=user_id,
            username=username,
            avatar_url=avatar,
            has_avatar=bool(avatar),
        )

    @rx.var
    def username_from_url(self) -> str:
        path = self.router.url.path or ""
        parts = path.strip("/").split("/")
        if len(parts) >= 2 and parts[0] == "user":
            return parts[1]
        return ""

    @rx.var
    def has_reviews(self) -> bool:
        return len(self.reviews) > 0

    @rx.event
    async def load_profile(self):
        username = self.username_from_url
        if not username:
            self.error = "URL inválida"
            return

        self.is_loading = True
        self.error = ""
        self.is_following = False
        self.is_editing_bio = False
        self.is_saving_bio = False
        self.bio_error = ""

        auth = await self.get_state(AuthState)
        token = auth.access_token

        if not token:
            # Sem token não dá pra chamar nada via Gateway autenticado.
            self.error = "Faça login pra ver perfis."
            self.is_loading = False
            return

        try:
            user_data = await fetch_user_by_username(username, token)
            if user_data is None:
                self.error = "Usuário não encontrado."
                self.user = ProfileUser()
                self.reviews = []
                return

            avatar = user_data.get("avatarUrl") or ""
            bio = user_data.get("bio") or ""
            target_auth0 = user_data.get("auth0Id") or ""

            # Counts de follow (best-effort — falhas não derrubam a página).
            followers_count = 0
            following_count = 0
            try:
                followers = await fetch_followers(target_auth0, token)
                followers_count = len(followers)
            except Exception as e:
                logger.warning("Falha ao carregar followers: %s", e)
            try:
                following = await fetch_following(target_auth0, token)
                following_count = len(following)
            except Exception as e:
                logger.warning("Falha ao carregar following: %s", e)

            self.user = ProfileUser(
                id=str(user_data.get("id") or ""),
                auth0_id=target_auth0,
                username=user_data.get("username") or "",
                bio=bio,
                avatar_url=avatar,
                review_count=int(user_data.get("reviewCount") or 0),
                followers_count=followers_count,
                following_count=following_count,
                has_avatar=bool(avatar),
                has_bio=bool(bio),
            )
            self.bio_input = bio

            self.is_own_profile = self.user.auth0_id == auth.user_id

            try:
                raw = await fetch_user_reviews(self.user.auth0_id, token)
                self.reviews = [_to_review(r) for r in raw]
            except Exception as e:
                logger.warning("Falha ao carregar reviews do perfil: %s", e)
                self.reviews = []

            # Carrega listas de seguidores/seguindo (best-effort)
            try:
                followers = await fetch_followers(target_auth0, token)
                self.followers = [
                    self._to_follow_user(f, "followers") for f in followers
                ]
            except Exception as e:
                logger.warning("Falha ao carregar followers list: %s", e)
                self.followers = []

            try:
                following = await fetch_following(target_auth0, token)
                self.following = [
                    self._to_follow_user(f, "following") for f in following
                ]
            except Exception as e:
                logger.warning("Falha ao carregar following list: %s", e)
                self.following = []

            if not self.is_own_profile:
                try:
                    following = await fetch_following(auth.user_id, token)
                    target = self.user.auth0_id
                    self.is_following = any(
                        f.get("following_id") == target for f in following
                    )
                except Exception as e:
                    logger.warning("Falha ao checar following: %s", e)
        except Exception as e:
            self.error = f"Falha ao carregar perfil: {e}"
        finally:
            self.is_loading = False

    @rx.event
    async def toggle_follow(self):
        auth = await self.get_state(AuthState)
        if not auth.access_token or self.is_own_profile:
            return

        target = self.user.auth0_id
        try:
            if self.is_following:
                await unfollow_user(target, auth.access_token)
                self.is_following = False
                # Decrementa otimisticamente o counter de seguidores.
                self.user = dataclasses.replace(
                    self.user,
                    followers_count=max(0, self.user.followers_count - 1),
                )
            else:
                await follow_user(target, auth.access_token)
                self.is_following = True
                self.user = dataclasses.replace(
                    self.user,
                    followers_count=self.user.followers_count + 1,
                )
                self.followers = [
                    FollowUser(
                        id=auth.user_id,
                        username=auth.username or auth.user_id,
                        avatar_url=auth.avatar_url,
                        has_avatar=bool(auth.avatar_url),
                    ),
                    *self.followers,
                ]
        except Exception as e:
            logger.warning("toggle_follow falhou: %s", e)

    @rx.event
    def toggle_bio_edit(self):
        if not self.is_own_profile:
            return
        self.is_editing_bio = not self.is_editing_bio
        self.bio_error = ""

    @rx.event
    def set_bio_input(self, value: str):
        if not self.is_own_profile:
            return
        self.bio_input = value[:200]
        self.bio_error = ""

    @rx.event
    async def save_bio(self):
        auth = await self.get_state(AuthState)
        if not auth.access_token or not self.is_own_profile:
            return

        self.is_saving_bio = True
        self.bio_error = ""

        try:
            data = await update_profile(
                username=self.user.username,
                bio=self.bio_input.strip(),
                avatar_url=self.user.avatar_url,
                token=auth.access_token,
            )
            bio = data.get("bio") or ""
            self.user = dataclasses.replace(
                self.user,
                bio=bio,
                has_bio=bool(bio),
            )
            self.is_editing_bio = False
        except Exception as e:
            self.bio_error = f"Falha ao salvar bio: {e}"
        finally:
            self.is_saving_bio = False

    @rx.event
    async def toggle_like(self, review_id: str):
        auth = await self.get_state(AuthState)
        if not auth.access_token:
            return
        try:
            result = await toggle_review_like(review_id, auth.access_token)
            self.reviews = [
                dataclasses.replace(
                    r,
                    is_liked=bool(result.get("liked")),
                    likes_count=int(result.get("likes_count") or 0),
                )
                if r.id == review_id
                else r
                for r in self.reviews
            ]
        except Exception as e:
            logger.warning("Falha no toggle de like (profile): %s", e)
