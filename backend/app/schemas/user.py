"""
Pydantic schemas for user authentication and profile management.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    preferred_currency: str = "USD"
    timezone: str = "UTC"


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str
    
    @validator("password")
    def validate_password(cls, v):
        """Validate password requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class UserUpdate(BaseModel):
    """Schema for user profile updates."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    preferred_currency: Optional[str] = None
    timezone: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response data."""
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    has_plaid_connection: bool = False
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Token payload data."""
    email: Optional[str] = None
    user_id: Optional[str] = None


class PasswordReset(BaseModel):
    """Password reset request schema."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema."""
    token: str
    new_password: str
    
    @validator("new_password")
    def validate_password(cls, v):
        """Validate password requirements."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class PlaidConnection(BaseModel):
    """Schema for Plaid connection status."""
    isConnected: bool
    institutionName: Optional[str] = None
    accountsCount: int = 0
    lastSync: Optional[datetime] = None 