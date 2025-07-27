"""
Security utilities for authentication and authorization.
Handles password hashing, JWT tokens, and user verification.
"""

from datetime import datetime, timedelta
from typing import Union, Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload data to encode in the token
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string to verify
    
    Returns:
        Decoded token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored hashed password
    
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_password_reset_token(email: str) -> str:
    """
    Generate a password reset token.
    
    Args:
        email: User email address
    
    Returns:
        JWT token for password reset
    """
    delta = timedelta(hours=24)  # Token valid for 24 hours
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email, "type": "reset"},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and return email.
    
    Args:
        token: Password reset token
    
    Returns:
        Email address if token is valid, None otherwise
    """
    try:
        decoded_token = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        if decoded_token.get("type") == "reset":
            return decoded_token["sub"]
    except JWTError:
        return None
    return None


def encrypt_plaid_token(access_token: str) -> str:
    """
    Encrypt Plaid access token for secure storage.
    This is a simplified version - in production, use proper encryption libraries.
    
    Args:
        access_token: Plaid access token
    
    Returns:
        Encrypted token string
    """
    # In production, use cryptography.fernet or similar
    # For now, we'll use base64 encoding (NOT secure for production)
    import base64
    return base64.b64encode(access_token.encode()).decode()


def decrypt_plaid_token(encrypted_token: str) -> str:
    """
    Decrypt Plaid access token.
    
    Args:
        encrypted_token: Encrypted Plaid token
    
    Returns:
        Decrypted access token
    """
    # In production, use proper decryption
    import base64
    return base64.b64decode(encrypted_token.encode()).decode() 