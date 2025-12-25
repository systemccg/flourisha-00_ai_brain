"""
Firebase Authentication Middleware

JWT verification for Firebase tokens with user context extraction.
"""
import logging
from typing import Optional, Dict, Any
from functools import lru_cache

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from pydantic import BaseModel

from config import get_settings


logger = logging.getLogger("flourisha.api.auth")

# Security scheme for JWT bearer tokens
security = HTTPBearer(auto_error=False)


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


def _init_firebase() -> bool:
    """Initialize Firebase Admin SDK if not already initialized.

    Returns True if successfully initialized, False otherwise.
    """
    try:
        # Check if already initialized
        firebase_admin.get_app()
        return True
    except ValueError:
        # Not initialized, try to initialize
        settings = get_settings()

        if not settings.firebase_project_id:
            logger.warning("Firebase project ID not configured - auth will be disabled")
            return False

        try:
            # Initialize with default credentials (uses GOOGLE_APPLICATION_CREDENTIALS)
            # or Application Default Credentials
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'projectId': settings.firebase_project_id,
            })
            logger.info(f"Firebase initialized for project: {settings.firebase_project_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            return False


@lru_cache
def is_firebase_available() -> bool:
    """Check if Firebase is available and initialized."""
    return _init_firebase()


async def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a Firebase JWT and return decoded claims.

    Args:
        token: The JWT token string

    Returns:
        Decoded token claims if valid, None if invalid

    Raises:
        HTTPException: If token is invalid or expired
    """
    if not is_firebase_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        )

    try:
        decoded = firebase_auth.verify_id_token(token)
        return decoded
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except firebase_auth.RevokedIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except firebase_auth.InvalidIdTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
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
