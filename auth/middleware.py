"""
Firebase Authentication Middleware
FastAPI dependency for JWT token verification
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional
from .firebase_auth import FirebaseAuth

# Security scheme
security = HTTPBearer()

# Initialize Firebase auth
firebase_auth = FirebaseAuth()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    FastAPI dependency to get current authenticated user from Firebase JWT

    Returns:
        Dict with user claims including:
        - sub: Firebase user ID
        - email: User email
        - tenant_id: Organization tenant ID (from custom claims)
        - tenant_user_id: User ID within tenant (from custom claims)
        - groups: User groups (from custom claims)

    Raises:
        HTTPException: 401 if token is invalid
    """
    token = credentials.credentials

    try:
        # Verify token using Firebase public keys
        user_claims = firebase_auth.verify_token(token)

        # Auto-assign default tenant if not set (for development/testing)
        # In production, this should be done during user provisioning
        if 'tenant_id' not in user_claims or not user_claims.get('tenant_id'):
            user_id = user_claims.get('sub') or user_claims.get('uid')
            user_claims['tenant_id'] = 'mk3029839'  # Default tenant (CoCreators)
            user_claims['tenant_user_id'] = user_id
            user_claims['groups'] = user_claims.get('groups', [])
            user_claims['role'] = user_claims.get('role', 'user')

        return user_claims

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[Dict]:
    """
    Optional authentication - returns None if no token provided
    Useful for endpoints that have different behavior for authenticated vs anonymous users
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_tenant(tenant_id: str):
    """
    Dependency factory to ensure user belongs to specific tenant

    Usage:
        @app.get("/api/v1/data")
        async def get_data(user: Dict = Depends(require_tenant("mk3029839"))):
            ...
    """
    async def _require_tenant(user: Dict = Depends(get_current_user)) -> Dict:
        user_tenant = user.get('tenant_id')
        if user_tenant != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required tenant: {tenant_id}"
            )
        return user

    return _require_tenant


def require_group(group_name: str):
    """
    Dependency factory to ensure user belongs to specific group

    Usage:
        @app.get("/api/v1/admin")
        async def admin_endpoint(user: Dict = Depends(require_group("admin"))):
            ...
    """
    async def _require_group(user: Dict = Depends(get_current_user)) -> Dict:
        user_groups = user.get('groups', [])
        if group_name not in user_groups:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required group: {group_name}"
            )
        return user

    return _require_group
