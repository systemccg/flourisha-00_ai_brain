"""
Firebase Authentication - JWT Verification without Service Account
Verifies Firebase JWT tokens using public keys from Google's API

Project: flourisha
Project ID: flourisha-d959a
Project Number: 664808461264
"""

import jwt
import requests
from functools import lru_cache
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Firebase project configuration
FIREBASE_PROJECT_ID = "flourisha-d959a"
PUBLIC_KEYS_URL = 'https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com'


class FirebaseAuth:
    """Firebase authentication handler using public key verification"""

    def __init__(self, project_id: str = FIREBASE_PROJECT_ID):
        self.project_id = project_id
        self.public_keys_url = PUBLIC_KEYS_URL

    @lru_cache(maxsize=1)
    def get_public_keys(self) -> Dict[str, str]:
        """
        Fetch Firebase public keys for JWT verification
        Cached to avoid repeated requests (keys rotate infrequently)
        """
        try:
            response = requests.get(self.public_keys_url, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch Firebase public keys: {e}")
            raise ValueError("Could not fetch Firebase public keys")

    def verify_token(self, token: str) -> Dict:
        """
        Verify Firebase JWT token and return decoded claims

        Args:
            token: Firebase ID token (JWT)

        Returns:
            dict: Decoded token claims including user_id, email, tenant_id, etc.

        Raises:
            ValueError: If token is invalid
        """
        try:
            # Decode header to get key id (kid)
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get('kid')

            if not kid:
                raise ValueError("Token header missing 'kid' field")

            # Get public keys
            public_keys = self.get_public_keys()

            if kid not in public_keys:
                # Keys might have rotated, clear cache and retry
                self.get_public_keys.cache_clear()
                public_keys = self.get_public_keys()

                if kid not in public_keys:
                    raise ValueError(f"Public key not found for kid: {kid}")

            # Verify and decode token
            decoded = jwt.decode(
                token,
                public_keys[kid],
                algorithms=['RS256'],
                audience=self.project_id,
                issuer=f'https://securetoken.google.com/{self.project_id}',
                options={
                    'verify_exp': True,
                    'verify_iat': True,
                    'verify_aud': True,
                    'verify_iss': True
                }
            )

            # Validate auth_time (token must not be too old)
            auth_time = decoded.get('auth_time')
            if auth_time:
                # Token should be less than 1 hour old for sensitive operations
                current_time = datetime.now().timestamp()
                if current_time - auth_time > 3600:
                    logger.warning(f"Token is older than 1 hour: auth_time={auth_time}")

            return decoded

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise ValueError(f"Token verification failed: {str(e)}")

    def extract_user_info(self, decoded_token: Dict) -> Dict:
        """
        Extract user information from decoded token

        Returns:
            dict: User info with standard fields
        """
        return {
            'user_id': decoded_token.get('sub') or decoded_token.get('uid'),
            'email': decoded_token.get('email'),
            'email_verified': decoded_token.get('email_verified', False),
            'name': decoded_token.get('name'),
            'picture': decoded_token.get('picture'),
            # Custom claims (set by backend when user is assigned to tenant)
            'tenant_id': decoded_token.get('tenant_id'),
            'tenant_user_id': decoded_token.get('tenant_user_id'),
            'groups': decoded_token.get('groups', []),
            'role': decoded_token.get('role', 'user'),
            # Token metadata
            'auth_time': decoded_token.get('auth_time'),
            'iat': decoded_token.get('iat'),
            'exp': decoded_token.get('exp')
        }


# Singleton instance
_firebase_auth: Optional[FirebaseAuth] = None


def get_firebase_auth(project_id: str = FIREBASE_PROJECT_ID) -> FirebaseAuth:
    """Get or create Firebase auth instance"""
    global _firebase_auth
    if _firebase_auth is None:
        _firebase_auth = FirebaseAuth(project_id)
    return _firebase_auth


# Convenience functions
def verify_firebase_token(token: str, project_id: str = FIREBASE_PROJECT_ID) -> Dict:
    """Verify Firebase token and return decoded claims"""
    auth = get_firebase_auth(project_id)
    return auth.verify_token(token)


def get_user_from_token(token: str, project_id: str = FIREBASE_PROJECT_ID) -> Dict:
    """Verify token and extract user information"""
    auth = get_firebase_auth(project_id)
    decoded = auth.verify_token(token)
    return auth.extract_user_info(decoded)
