"""
Firebase Authentication Middleware

JWT verification for Firebase tokens using public key verification.
No service account required - uses Google's public keys API.
"""
import logging
from typing import Optional, Dict, Any
from functools import lru_cache

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
import requests
from cryptography.hazmat.primitives import serialization
from cryptography import x509

from config import get_settings


logger = logging.getLogger("flourisha.api.auth")

# Security scheme for JWT bearer tokens
security = HTTPBearer(auto_error=False)

# Firebase public keys URL
PUBLIC_KEYS_URL = 'https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com'


class UserContext(BaseModel):
    """User context extracted from Firebase JWT."""
    uid: str  # Firebase user ID
    email: Optional[str] = None
    email_verified: bool = False
    name: Optional[str] = None
    picture: Optional[str] = None

    # Custom claims (set via Firebase Admin SDK)
    tenant_id: Optional[str] = None
    tenant_user_id: Optional[str] = None
    roles: list[str] = []

    # Raw token claims for advanced usage
    raw_claims: Dict[str, Any] = {}


@lru_cache(maxsize=1)
def _get_public_keys() -> Dict[str, str]:
    """Fetch Firebase public keys for JWT verification (cached)."""
    try:
        response = requests.get(PUBLIC_KEYS_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch Firebase public keys: {e}")
        raise


def _clear_keys_cache():
    """Clear the public keys cache (call if keys rotated)."""
    _get_public_keys.cache_clear()


@lru_cache
def is_firebase_available() -> bool:
    """Check if Firebase config is available."""
    settings = get_settings()
    return bool(settings.firebase_project_id)


async def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a Firebase JWT using public key verification.

    No service account required - uses Google's public keys API.

    Args:
        token: The JWT token string

    Returns:
        Decoded token claims if valid

    Raises:
        HTTPException: If token is invalid or expired
    """
    settings = get_settings()

    if not settings.firebase_project_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firebase project ID not configured"
        )

    try:
        # Decode header to get key id (kid)
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')

        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token header missing 'kid' field",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get public keys
        public_keys = _get_public_keys()

        if kid not in public_keys:
            # Keys might have rotated, clear cache and retry
            _clear_keys_cache()
            public_keys = _get_public_keys()

            if kid not in public_keys:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Public key not found for kid: {kid}",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        # Convert certificate to public key
        cert_str = public_keys[kid]
        cert_obj = x509.load_pem_x509_certificate(cert_str.encode())
        public_key = cert_obj.public_key()

        # Convert to PEM format for PyJWT
        pem_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Verify and decode token
        decoded = jwt.decode(
            token,
            pem_key,
            algorithms=['RS256'],
            audience=settings.firebase_project_id,
            issuer=f'https://securetoken.google.com/{settings.firebase_project_id}',
            options={
                'verify_exp': True,
                'verify_iat': True,
                'verify_aud': True,
                'verify_iss': True
            }
        )

        return decoded

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


def extract_user_context(decoded_token: Dict[str, Any]) -> UserContext:
    """Extract UserContext from decoded Firebase token.

    Args:
        decoded_token: The decoded JWT claims

    Returns:
        UserContext with extracted user information
    """
    return UserContext(
        uid=decoded_token.get("uid", decoded_token.get("sub", "")),
        email=decoded_token.get("email"),
        email_verified=decoded_token.get("email_verified", False),
        name=decoded_token.get("name"),
        picture=decoded_token.get("picture"),
        tenant_id=decoded_token.get("tenant_id"),
        tenant_user_id=decoded_token.get("tenant_user_id"),
        roles=decoded_token.get("roles", []),
        raw_claims=decoded_token,
    )


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> UserContext:
    """FastAPI dependency to get current authenticated user.

    Usage:
        @app.get("/protected")
        async def protected_route(user: UserContext = Depends(get_current_user)):
            return {"user_id": user.uid}

    Raises:
        HTTPException: 401 if no token or invalid token
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    decoded = await verify_token(credentials.credentials)
    user = extract_user_context(decoded)

    # Store user in request state for access in middleware
    request.state.user = user

    return user


async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[UserContext]:
    """FastAPI dependency for optional authentication.

    Returns user context if valid token provided, None otherwise.
    Useful for endpoints that work both authenticated and unauthenticated.

    Usage:
        @app.get("/public")
        async def public_route(user: Optional[UserContext] = Depends(get_optional_user)):
            if user:
                return {"message": f"Hello {user.name}!"}
            return {"message": "Hello guest!"}
    """
    if not credentials:
        return None

    try:
        decoded = await verify_token(credentials.credentials)
        user = extract_user_context(decoded)
        request.state.user = user
        return user
    except HTTPException:
        return None


def require_roles(*required_roles: str):
    """Dependency factory for role-based access control.

    Usage:
        @app.get("/admin")
        async def admin_route(
            user: UserContext = Depends(require_roles("admin"))
        ):
            return {"admin": True}
    """
    async def role_checker(
        user: UserContext = Depends(get_current_user),
    ) -> UserContext:
        if not any(role in user.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(required_roles)}"
            )
        return user

    return role_checker
