"""Azure AD JWT 認証モジュール"""

import json
import time
from dataclasses import dataclass, field
from urllib.request import urlopen

import jwt
from backend.app.config import settings
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from src.utils.constants import ROLE_DRIVER, ROLE_MANAGER

# Azure AD JWKS キャッシュ（TTL 24時間）
_jwks_cache: dict | None = None
_jwks_cache_time: float = 0.0
_JWKS_TTL_SECONDS = 86400  # 24時間


def _get_jwks(force_refresh: bool = False) -> dict:
    """Azure AD の JWKS（公開鍵セット）を取得（TTL付きキャッシュ）"""
    global _jwks_cache, _jwks_cache_time  # noqa: PLW0603
    now = time.time()
    if not force_refresh and _jwks_cache is not None and (now - _jwks_cache_time) < _JWKS_TTL_SECONDS:
        return _jwks_cache
    jwks_url = f"https://login.microsoftonline.com/{settings.azure_ad_tenant_id}/discovery/v2.0/keys"
    with urlopen(jwks_url, timeout=10) as response:  # noqa: S310
        _jwks_cache = json.loads(response.read())
    _jwks_cache_time = now
    return _jwks_cache


def _find_rsa_key(token: str) -> dict:
    """JWT ヘッダの kid に一致する RSA 公開鍵を取得（kid不一致時は再取得）"""
    jwks = _get_jwks()
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid", "")
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return key
    # kid不一致: キャッシュを無効化して再取得
    jwks = _get_jwks(force_refresh=True)
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="公開鍵が見つかりません",
    )


@dataclass
class CurrentUser:
    """認証済みユーザー情報"""

    user_id: str  # Azure AD oid
    roles: list[str] = field(default_factory=list)
    store_id: int | None = None
    driver_id: int | None = None


def _map_groups_to_roles(groups: list[str]) -> list[str]:
    """Azure AD グループ ID をアプリロールにマッピング"""
    roles = []
    if settings.azure_ad_manager_group_id in groups:
        roles.append(ROLE_MANAGER)
    if settings.azure_ad_driver_group_id in groups:
        roles.append(ROLE_DRIVER)
    return roles


async def verify_token(credentials: HTTPAuthorizationCredentials) -> CurrentUser:
    """JWT トークンを検証し、CurrentUser を返す"""
    token = credentials.credentials

    try:
        rsa_key = _find_rsa_key(token)
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(rsa_key)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.azure_ad_client_id,
            issuer=f"https://login.microsoftonline.com/{settings.azure_ad_tenant_id}/v2.0",
        )
    except jwt.ExpiredSignatureError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンの有効期限が切れています",
        ) from err
    except jwt.InvalidTokenError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです",
        ) from err

    groups = payload.get("groups", [])
    roles = _map_groups_to_roles(groups)
    if not roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="有効なロールが割り当てられていません",
        )

    return CurrentUser(
        user_id=payload["oid"],
        roles=roles,
    )
