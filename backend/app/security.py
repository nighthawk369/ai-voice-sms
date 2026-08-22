"""Authentication and security utilities"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import get_settings
import secrets
import string
import hashlib
import hmac

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def create_access_token(user_id: str, org_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = {
        "sub": user_id,
        "org_id": org_id,
        "type": "access"
    }

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: str, org_id: str) -> str:
    """Create JWT refresh token"""
    to_encode = {
        "sub": user_id,
        "org_id": org_id,
        "type": "refresh"
    }
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def get_token_user_id(token: str) -> Optional[str]:
    """Extract user_id from token"""
    payload = decode_token(token)
    if payload:
        return payload.get("sub")
    return None


def get_token_org_id(token: str) -> Optional[str]:
    """Extract organization_id from token"""
    payload = decode_token(token)
    if payload:
        return payload.get("org_id")
    return None


def validate_token_type(token: str, expected_type: str) -> bool:
    """Validate that token is of expected type"""
    payload = decode_token(token)
    if payload:
        return payload.get("type") == expected_type
    return False


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    alphabet = string.ascii_letters + string.digits + "-_"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def hash_token(token: str) -> str:
    """Hash a token for storage"""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_token_hash(plain_token: str, token_hash: str) -> bool:
    """Verify a token against its hash"""
    return hmac.compare_digest(hash_token(plain_token), token_hash)


def generate_api_key() -> Tuple[str, str]:
    """Generate API key and its hash"""
    key = f"sk_{generate_secure_token(32)}"
    key_hash = hash_token(key)
    return key, key_hash
